from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets
from .models import Staff, Roster, RosterConfig, BakeryProduct, BakeryProductRestock, DailyRevenue
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
from django.db.models.functions import TruncDate
from decimal import Decimal

def modify_product_info(request):
    product = None
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        item_name = request.POST.get('item_name')

        # Search for the product based on item_id or item_name
        if item_id:
            product = get_object_or_404(BakeryProduct, item_id=item_id)
        elif item_name:
            product = BakeryProduct.objects.filter(item_name__icontains=item_name).first()

        # If a product is found and the modify button is pressed
        if product and 'modify' in request.POST:
            product.item_name = request.POST.get('item_name', product.item_name)
            product.item_name_CHI = request.POST.get('item_name_CHI', product.item_name_CHI)
            product.category = request.POST.get('category', product.category)
            product.remarks = request.POST.get('remarks', product.remarks)
            product.save()  # Save updated product information
            return redirect('modify_product_info')  # Redirect after saving

    return render(request, 'roster/modify_product_info.html', {'product': product})

def manage_bakery_products(request):
    if request.method == 'POST':
        # Handle the form submission
        item_id = request.POST.get('item_id')
        category = request.POST.get('category')
        item_name = request.POST.get('item_name')
        item_name_CHI = request.POST.get('item_name_CHI', '')
        onsell = request.POST.get('onsell') == 'True'
        start_date = request.POST.get('start_date')
        shelved_date = request.POST.get('shelved_date') or None
        remarks = request.POST.get('remarks', '')

        # Create a new BakeryProduct instance
        new_product = BakeryProduct(
            item_id=item_id,
            category=category,
            item_name=item_name,
            item_name_CHI=item_name_CHI,
            onsell=onsell,
            start_date=start_date,
            shelved_date=shelved_date,
            remarks=remarks
        )
        new_product.save()  # Save to the database

        return redirect('manage_bakery_products')  # Redirect to the same page after submission

    # Handle GET request to display the form
    return render(request, 'roster/manage_bakery_products.html')

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
        'categories': categories,
         'products': products  # Pass products to the template, including image URLs
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
    # Calculate total hours worked by summing the no_of_work_hr field
    total_hours_worked = Roster.objects.aggregate(total_hours=Sum('no_of_work_hr'))['total_hours'] or 0.0
     # Calculate total working hours by day
    daily_hours = (
        Roster.objects
        .annotate(date=TruncDate('work_date'))  # Group by day
        .values('date')  # Get date values
        .annotate(total_hours=Sum('no_of_work_hr'))  # Sum hours for each day
        .order_by('date')  # Order by date
    )

    # Prepare data for chart
    dates = [entry['date'].strftime('%Y-%m-%d') for entry in daily_hours]  # Format dates
    total_daily_hours = [entry['total_hours'] for entry in daily_hours]  # Get total hours for each day


     # Calculate total working hours by staff
    staff_hours = (
        Roster.objects
        .values('staff_name')  # Group by staff name
        .annotate(total_hours=Sum('no_of_work_hr'))  # Sum hours for each staff
        .order_by('-total_hours')  # Order by total hours descending
    )

    # Convert staff_hours to a list of dictionaries for easier access in the template
    staff_hours_list = list(staff_hours)
 # Get the top 5 staff by total working hours
    top_staff = staff_hours[:5]  # Get the top 5 staff members


    return render(request, 'roster/statistics.html', {
        'total_hours_worked': total_hours_worked,
        'total_daily_hours': total_daily_hours,
        'dates': json.dumps(dates),  # Convert dates to JSON
        'staff_hours': json.dumps(staff_hours_list),  # Convert staff hours to JSON
        'top_staff': json.dumps(list(top_staff)),  # Convert top staff to JSON
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

def manage_staff(request):
    return render(request, 'manage_staff.html')  # Point to your blank HTML page

def submit_revenue(request):
    if request.method == 'POST':
        try:
            user_input = request.POST.get('user')
            business_date = request.POST.get('businessDate')
            business_time = request.POST.get('businessTime')
            amex = Decimal(request.POST.get('amex', 0) or 0).quantize(Decimal('0.01'))  # Standard rounding
            debit_card = Decimal(request.POST.get('debit', 0) or 0).quantize(Decimal('0.01'))  # Standard rounding
            visa = Decimal(request.POST.get('visa', 0) or 0).quantize(Decimal('0.01'))  # Standard rounding
            mastercard = Decimal(request.POST.get('mastercard', 0) or 0).quantize(Decimal('0.01'))  # Standard rounding
            cash = Decimal(request.POST.get('cash', 0) or 0).quantize(Decimal('0.01'))  # Standard rounding
            unionpay = Decimal(request.POST.get('unionpay', 0) or 0).quantize(Decimal('0.01'))  # Standard rounding
            wonderful_card = Decimal(request.POST.get('wonderfulCard', 0) or 0).quantize(Decimal('0.01'))  # Standard rounding
            gift_card = Decimal(request.POST.get('giftCard', 0) or 0).quantize(Decimal('0.01'))  # Standard rounding
            pst = Decimal(request.POST.get('pst', 0) or 0).quantize(Decimal('0.01'))  # Standard rounding
            redeem_points = int(request.POST.get('redeemPoints', 0))

            # Calculate total
            total = (amex + debit_card + visa + mastercard + cash + unionpay + wonderful_card).quantize(Decimal('0.01'))  # Standard rounding

            # Create and save the revenue record
            DailyRevenue.objects.create(
                user_input=user_input,  # Make sure this is set correctly
                business_date=business_date,
                business_time=business_time,
                amex=amex,
                debit_card=debit_card,
                visa=visa,
                mastercard=mastercard,
                cash=cash,
                unionpay=unionpay,
                wonderful_card=wonderful_card,
                gift_card=gift_card,
                pst=pst,
                redeem_points=redeem_points,
                total=total
            )

            return JsonResponse({'status': 'success', 'message': 'Revenue submitted successfully!'})
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return render(request, 'roster/submit_revenue.html')  # Adjust to your template name

def revenue_dashboard(request):
    return render(request, 'roster/revenue_dashboard.html')
