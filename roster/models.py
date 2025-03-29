from django.db import models
from datetime import date
from django.utils import timezone
from django.contrib.auth.models import User

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
    
    # Model for maintaining bakery products
class BakeryProduct(models.Model):
    item_id = models.CharField(max_length=50, unique=True)  # Custom item ID assigned by the store
    category = models.CharField(max_length=100)  # Product category
    item_name = models.CharField(max_length=100)  # Name of the item
    item_name_CHI = models.CharField(max_length=100, blank=True)  # Name of the item in Chinese
    onsell = models.BooleanField(default=True)  # Whether the product is on sale
    start_date = models.DateField()  # When the product is available
    shelved_date = models.DateField(null=True, blank=True)  # When the product was shelved
    remarks = models.TextField(blank=True)  # Additional remarks
    image_url = models.URLField(max_length=200, blank=True)  # URL of the product image
    image_url_cat = models.URLField(max_length=200, blank=True)  # URL of the category image

    def __str__(self):
        return f"{self.item_name} ({self.category})"

# Model for bakery product restocking
class BakeryProductRestock(models.Model):
    item_id = models.CharField(max_length=50)  # Custom item ID assigned by the store
    product_name = models.CharField(max_length=100)  # Name of the product
    restock_quantity = models.PositiveIntegerField()  # Quantity restocked
    delivery_date = models.DateField()  # Delivery date for the restock
    order_by = models.CharField(max_length=100)  # Who placed the order
    update_date = models.DateTimeField(auto_now=True)  # Timestamp for when the record was updated

    def __str__(self):
        return f"{self.product_name} - {self.restock_quantity} (Ordered by: {self.order_by})"
    
class DailyRevenue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business_date = models.DateField()
    business_time = models.TimeField()
    amex = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    debit_card = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    visa = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mastercard = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unionpay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wonderful_card = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gift_card = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    redeem_points = models.IntegerField(default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)  # Automatically set on update

    def __str__(self):
        return f"Revenue for {self.business_date} at {self.business_time} by {self.user.username}"