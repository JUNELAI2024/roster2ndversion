from django.db import models
from datetime import date

class Staff(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

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

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    shift_start = models.TimeField()
    shift_end = models.TimeField()
    duty_role = models.ForeignKey(Config, on_delete=models.SET_NULL, null=True)
    week_start_date = models.DateField(default=date.today)  # New field for the week start date
    work_date = models.DateField(default=date.today)  # New field for the specific date of the shift

    def __str__(self):
        return f"{self.staff.name} - {self.day}: {self.shift_start} to {self.shift_end}"