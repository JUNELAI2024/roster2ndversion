from django.db import models
from datetime import date
from django.utils import timezone

class Staff(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class RosterConfig(models.Model):
    duty_role = models.CharField(max_length=100)
    time_slot = models.TimeField()

    def __str__(self):
        return f"{self.duty_role} - {self.time_slot.strftime('%H:%M')}"  # Keep the original time format



class Config(models.Model):
    duty_role = models.CharField(max_length=100)
    time_slot = models.TimeField()

    def __str__(self):
        return f"{self.duty_role} - {self.time_slot}"

class Roster(models.Model):
    DAY_CHOICES = [
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'),
        ('Wed', 'Wednesday'),
        ('Thu', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Saturday'),
        ('Sun', 'Sunday'),
    ]

    staff_name = models.CharField(max_length=100)  # Change from ForeignKey to CharField
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    shift_start = models.TimeField()
    shift_end = models.TimeField()
    duty_role = models.CharField(max_length=50)
    week_start_date = models.DateField()  # No default value
    work_date = models.DateField()
    no_of_work_hr = models.FloatField(default=0.0)  # Store working hours with one decimal precision

    def save(self, *args, **kwargs):
        # Calculate the number of work hours before saving
        if self.shift_start and self.shift_end:
            start_time = timezone.datetime.combine(self.work_date, self.shift_start)
            end_time = timezone.datetime.combine(self.work_date, self.shift_end)
            self.no_of_work_hr = round((end_time - start_time).seconds / 3600.0, 1)  # Round to 1 decimal place
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.staff_name} - {self.day} ({self.shift_start} to {self.shift_end})"