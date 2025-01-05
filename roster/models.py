from django.db import models

class Staff(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)  # Field for active status

    def __str__(self):
        return self.name

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

    def __str__(self):
        return f"{self.staff.name} - {self.day}"