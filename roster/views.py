from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import Staff, Roster, RosterConfig
from .serializers import StaffSerializer, RosterSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta

# Original views for rendering templates
def staff_list(request):
    active_staff = Staff.objects.filter(is_active=True)  # Get only active staff
    return render(request, 'roster/staff_list.html', {'staff_list': active_staff})

def roster_create(request):
    active_staff = Staff.objects.filter(is_active=True)  # Get active staff
    days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']  # Define days of the week
    week_start_date = timezone.now().date()  # Default to today's date
    time_slots = RosterConfig.objects.values_list('time_slot', flat=True)  # Fetch time slots
     # Format time slots for dropdowns (HH:MM)
    formatted_time_slots = [slot.strftime('%H:%M') for slot in time_slots]
    duty_roles = RosterConfig.objects.all()  # Fetch all duty roles

    if request.method == 'POST':
        for staff in active_staff:
            for day in days_of_week:
                shift_start = request.POST.get(f"shift_start_{staff.id}_{day}")
                shift_end = request.POST.get(f"shift_end_{staff.id}_{day}")
                duty_role_id = request.POST.get(f"duty_role_{staff.id}_{day}")  # Get duty role ID

                if shift_start and shift_end:
                    # Calculate the work date based on the week start date and day
                    work_date = week_start_date + timedelta(days=days_of_week.index(day))

                    # Check for existing entries to prevent duplicates
                    if Roster.objects.filter(staff=staff, day=day, work_date=work_date).exists():
                        messages.error(request, f"Shift for {staff.name} on {day} already exists.")
                        continue

                    # Create roster entry
                    Roster.objects.create(
                        staff=staff,
                        day=day,
                        shift_start=shift_start,
                        shift_end=shift_end,
                        duty_role_id=duty_role_id,  # Store the duty role ID
                        week_start_date=week_start_date,
                        work_date=work_date  # Store the calculated work date
                    )

        messages.success(request, "Roster created successfully!")
        return redirect('roster_list')

    return render(request, 'roster/roster_create.html', {
        'staff_list': active_staff,
        'days': days_of_week,
        'week_start_date': week_start_date,
        'time_slots': formatted_time_slots, # Pass time slots to the template
        'duty_roles': duty_roles,  # Pass duty roles to the template
    })

def roster_list(request):
    rosters = Roster.objects.all()
    return render(request, 'roster/roster_list.html', {'rosters': rosters})

# New view for displaying shift statistics
def statistics_view(request):
    # Fetch data for each staff and their shift counts
    staff_shift_counts = (
        Roster.objects
        .values('staff__name')
        .annotate(
            am_count=Count('id', filter=Q(shift_start='09:00:00')),
            pm_count=Count('id', filter=Q(shift_start='14:00:00')),
            full_count=Count('id', filter=Q(shift_start='09:00:00', shift_end='19:00:00'))
        )
    )

    # Prepare data for the bar chart
    staff_names = [item['staff__name'] for item in staff_shift_counts]
    am_counts = [item['am_count'] for item in staff_shift_counts]
    pm_counts = [item['pm_count'] for item in staff_shift_counts]
    full_counts = [item['full_count'] for item in staff_shift_counts]

    return render(request, 'roster/statistics.html', {
        'staff_names': staff_names,
        'am_counts': am_counts,
        'pm_counts': pm_counts,
        'full_counts': full_counts,
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