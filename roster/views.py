from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import Staff, Roster
from .serializers import StaffSerializer, RosterSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Q

# Original views for rendering templates
def staff_list(request):
    active_staff = Staff.objects.filter(is_active=True)  # Get only active staff
    return render(request, 'roster/staff_list.html', {'staff_list': active_staff})

def roster_create(request):
    active_staff = Staff.objects.filter(is_active=True)  # Get active staff
    days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']  # Define days of the week

    if request.method == 'POST':
        for staff in active_staff:
            for day in days_of_week:
                time_choice = request.POST.get(f"{staff.id}_{day}")
                if time_choice:
                    if time_choice == 'AM':
                        Roster.objects.create(staff=staff, day=day, shift_start='09:00:00', shift_end='14:00:00')
                    elif time_choice == 'PM':
                        Roster.objects.create(staff=staff, day=day, shift_start='14:00:00', shift_end='19:00:00')
                    elif time_choice == 'FULL':
                        Roster.objects.create(staff=staff, day=day, shift_start='09:00:00', shift_end='19:00:00')
        return redirect('roster_list')

    return render(request, 'roster/roster_create.html', {'staff_list': active_staff, 'days': days_of_week})

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