from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import Staff, Roster, RosterConfig, BakeryProduct, BakeryProductRestock
from django.db.models import Sum
from .serializers import StaffSerializer, RosterSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages
from datetime import  timedelta
from django import forms
import logging
logger = logging.getLogger(__name__)
from datetime import datetime 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def bakery_product_view(request):
    products = BakeryProduct.objects.filter(onsell=True)  # Get only products that are on sale
    categories = products.values_list('category', flat=True).distinct()  # Get unique categories

    context = {
        'products': products,
        'categories': categories,
    }
    
    return render(request, 'roster/bakery_product.html', context)


@csrf_exempt
def restock_product(request):
     # Fetch all products that are onsell
    products = BakeryProduct.objects.filter(onsell=True)
    # Get unique categories
    categories = products.values_list('category', flat=True).distinct()

    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            for product in data:
               item_id = product.get('item_id')
            product_name = product.get('product_name')
            restock_quantity = product.get('restock_quantity')
            delivery_date = product.get('delivery_date')
            order_by = product.get('order_by')

            # Create a new instance and save it to the database
            restock_entry = BakeryProductRestock(
                item_id=item_id,
                product_name=product_name,
                restock_quantity=restock_quantity,
                delivery_date=delivery_date,
                order_by=order_by
            )
            restock_entry.save()  # update_date will be set automatically here

            return JsonResponse({'status': 'success', 'message': 'Product restocked successfully.'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
        
 # Handle GET requests by rendering the template
    context = {
        'categories': categories
    }
    # Handle GET requests by rendering the template
    return render(request, 'roster/bakery_product.html')  # Ensure this points to your actual template path

def home(request):
    return render(request, 'roster/home.html')  # Make sure the path matches your template location

# Original views for rendering templates
def staff_list(request):
    active_staff = Staff.objects.filter(is_active=True)  # Get only active staff
    return render(request, 'roster/staff_list.html', {'staff_list': active_staff})

def roster_create(request):
    active_staff = Staff.objects.filter(is_active=True)  # Get active staff
    days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']  # Define days of the week
    week_start_date = None  # Initialize week_start_date
    time_slots = RosterConfig.objects.values_list('time_slot', flat=True).order_by('time_slot')  # Fetch time slots
    formatted_time_slots = [slot.strftime('%H:%M') for slot in time_slots]  # Format to HH:MM:SS
    duty_roles = RosterConfig.objects.values_list('duty_role', flat=True).distinct().order_by('duty_role')


    if request.method == 'POST':
        # Get the week starting date from the form input
        week_start_date_str = request.POST.get('week_start_date')
        if week_start_date_str:  # If the user provided a date
            week_start_date = datetime.strptime(week_start_date_str, '%Y-%m-%d').date()  # Convert to date
        else:
            week_start_date = timezone.now().date()  # Fallback to today's date if not provided
        for staff in active_staff:
            for day in days_of_week:
                shift_start = request.POST.get(f"shift_start_{staff.id}_{day}")
                shift_end = request.POST.get(f"shift_end_{staff.id}_{day}")
                duty_role = request.POST.get(f"duty_role_{staff.id}_{day}")  # Get duty role name directly

                if shift_start and shift_end:
                    # Calculate the work date based on the week start date and day
                    work_date = week_start_date + timedelta(days=days_of_week.index(day))

                    # Check if a roster entry already exists
                    if Roster.objects.filter(staff_name=staff.name, day=day, work_date=work_date).exists():
                        messages.error(request, f"Shift for {staff.name} on {day} already exists.")
                        continue

                    # Convert to TimeField directly
                    shift_start_time = timezone.datetime.strptime(shift_start, "%H:%M").time()
                    shift_end_time = timezone.datetime.strptime(shift_end, "%H:%M").time()
                    no_of_work_hr = round((timezone.datetime.combine(work_date, shift_end_time) - 
                                            timezone.datetime.combine(work_date, shift_start_time)).seconds / 3600.0, 1)


                    # Create roster entry
                    Roster.objects.create(
                        staff_name=staff.name,  # Store the staff member's name
                        day=day,
                        shift_start=shift_start_time,
                        shift_end=shift_end_time,
                        duty_role=duty_role,  # Store the duty role name directly
                        week_start_date=week_start_date,
                        work_date=work_date,
                        no_of_work_hr=no_of_work_hr,  # Store the calculated working hours
                       
                    )

        messages.success(request, "Roster created successfully!")
        return redirect('roster_list')

    return render(request, 'roster/roster_create.html', {
        'staff_list': active_staff,
        'days': days_of_week,
        'week_start_date': week_start_date,
        'time_slots': formatted_time_slots ,  # Pass time slots directly
        'duty_roles': duty_roles,  # Pass duty roles to the template
    })

def roster_list(request):
    active_staff = Staff.objects.filter(is_active=True)  # Fetch only active staff
    roster_list = Roster.objects.all()  # Initial query

    staff_name = request.GET.get('staff_name') 
    month = request.GET.get('month')

    if staff_name:  # Adjusted to use staff_name
        roster_list = roster_list.filter(staff_name__iexact=staff_name)  # Filter by staff name (case-insensitive)

    if month:
        roster_list = roster_list.filter(work_date__month=month)  # Assuming work_date is a DateField

    context = {
        'active_staff': active_staff,
        'roster_list': roster_list,
    }
    return render(request, 'roster/roster_list.html', context)

# New view for displaying shift statistics
def statistics_view(request):
    total_weekly_hours = 40  # Example: Total working hours in a week
    staff_hours = (
        Roster.objects
        .values('staff_name')
        .annotate(total_hours=Sum('no_of_work_hr'))
    )

    staff_names = [item['staff_name'] for item in staff_hours]
    occupied_hours = [item['total_hours'] for item in staff_hours]

    # Calculate ratios and prepare data for the pie chart
    ratios = [(hours / total_weekly_hours) * 100 for hours in occupied_hours]  # Percentage of total hours

    # Handle case where staff_names is empty
    if not staff_names:
        staff_names = ['No Data']
        ratios = [100]  # To avoid pie chart error

    return render(request, 'roster/statistics.html', {
        'staff_names': staff_names,
        'ratios': ratios,
    })

# New API view to get shift counts similar to statistics_view
@api_view(['GET'])
def api_shift_counts(request):
    shift_counts = (
        Roster.objects
        .values('staff__name')
        .annotate(
            am_count=Count('id', filter=Q(shift_start='09:00:00')),
            pm_count=Count('id', filter=Q(shift_start='14:00:00')),
            full_count=Count('id', filter=Q(shift_start='09:00:00', shift_end='19:00:00'))
        )
    )

    return Response(shift_counts)

# New API views using Django REST Framework
class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

class RosterViewSet(viewsets.ModelViewSet):
    queryset = Roster.objects.all()
    serializer_class = RosterSerializer
