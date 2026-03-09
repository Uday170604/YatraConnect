from django.db import models
from django.utils import timezone
import random

class Bus(models.Model):
    name = models.CharField(max_length=100, default="Sleeper Express")
    source = models.CharField(max_length=100, default="Ahmedabad")
    destination = models.CharField(max_length=100, default="Mumbai")
    departure_time = models.TimeField(default="22:00")
    arrival_time = models.TimeField(default="06:00")
    total_seats = models.IntegerField(default=30)

    class Meta:
        verbose_name_plural = "Buses"

    def __str__(self):
        return f"{self.name} ({self.source} - {self.destination})"

class BusStop(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='stops')
    name = models.CharField(max_length=100)
    arrival_time = models.TimeField()
    stop_number = models.IntegerField(help_text="Order of the stop")

    class Meta:
        ordering = ['stop_number']

    def __str__(self):
        return f"{self.name} (Stop {self.stop_number} for {self.bus.name})"

class Seat(models.Model):
    SEAT_TYPES = (
        ('LOWER', 'Lower Deck'),
        ('UPPER', 'Upper Deck'),
    )
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.CharField(max_length=5)  # e.g., L1, U1
    seat_type = models.CharField(max_length=10, choices=SEAT_TYPES)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=800.00)
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('bus', 'seat_number')

    def __str__(self):
        return f"{self.seat_number} - {self.seat_type}"

class Meal(models.Model):
    MEAL_TYPES = (
        ('VEG', 'Vegetarian'),
        ('SNACK', 'Snacks'),
    )
    name = models.CharField(max_length=100)
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPES)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_meal_type_display()}) - ₹{self.price}"

from django.contrib.auth.models import User

class Booking(models.Model):
    STATUS_CHOICES = (
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    passenger_name = models.CharField(max_length=100)
    passenger_age = models.IntegerField()
    passenger_gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE) # Changed from OneToOne to allow history/re-booking
    # Ideally booking has many seats, but assignment says "Seat booking" (singular/plural ambiguous). 
    # Let's keep it simple: 1 Booking = 1 Seat for now, or make it cleaner.
    # Actually, standard flow often allows multiple. But "List of seats" is a mandatory endpoint. 
    # Let's stick to 1 booking = 1 seat for simplicity of the prompt's scope "List critical test cases...". 
    # Wait, usually people book multiple. I'll make it ForeignKey so one User can have multiple bookings? 
    # No, `seat = OneToOne` means one seat is associated with ONE active booking record.
    # If I want to support multiple seats in one "Order", I would need an Order model.
    # Given the timeframe and "Simplicity/Clarity", let's treat each seat booked as a Booking record.
    
    meal = models.ForeignKey(Meal, on_delete=models.SET_NULL, null=True, blank=True)
    
    booking_date = models.DateTimeField(auto_now_add=True)
    travel_date = models.DateField(default=timezone.now)
    pnr = models.CharField(max_length=10, unique=True, editable=False)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMED')
    prediction_score = models.FloatField(help_text="Booking confirmation probability", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pnr:
            self.pnr = f"PNR{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.pnr} - {self.passenger_name}"
