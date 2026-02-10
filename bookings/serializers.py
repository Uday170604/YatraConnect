from rest_framework import serializers
from .models import Bus, Meal, Seat, Booking
from .ml_utils import predict_booking_confirmation
from decimal import Decimal
from django.utils import timezone

class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ['id', 'name', 'source', 'destination', 'departure_time', 'arrival_time']

class MealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meal
        fields = ['id', 'name', 'meal_type', 'price', 'description']

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'seat_type', 'price', 'is_booked']

class BookingSerializer(serializers.ModelSerializer):
    # Calculate fields or nested writes
    pnr = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    prediction_score = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'passenger_name', 'passenger_age', 'passenger_gender',
            'email', 'phone', 'seat', 'meal', 'travel_date',
            'pnr', 'total_amount', 'status', 'prediction_score'
        ]

    def validate_passenger_name(self, value):
        import re
        if not re.match(r"^[a-zA-Z\s]+$", value):
            raise serializers.ValidationError("Name must contain only letters and spaces.")
        return value

    def validate_phone(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return value

    def create(self, validated_data):
        from django.db import transaction
        
        # Custom creation logic to handle calculations, prediction and race conditions
        seat_initial = validated_data['seat']
        meal = validated_data.get('meal')
        travel_date = validated_data.get('travel_date', timezone.now().date())
        
        with transaction.atomic():
            # LOCK the seat row to prevent race conditions
            seat = Seat.objects.select_for_update().get(id=seat_initial.id)
            
            if seat.is_booked:
                raise serializers.ValidationError({"seat": "This seat is already booked."})
                
            # Calculate Total
            total_price = seat.price
            if meal:
                total_price += meal.price
                
            # Prediction
            prediction_score = predict_booking_confirmation(
                date=str(travel_date), 
                seat_count=1, 
                meal_included=bool(meal)
            )
            
            booking = Booking.objects.create(
                total_amount=total_price,
                prediction_score=prediction_score,
                status='CONFIRMED',
                # We need to manually inject the locked seat object to be safe, 
                # though validated_data['seat'] has the ID, creating with 'seat' obj is safer
                seat=seat,  
                passenger_name=validated_data['passenger_name'],
                passenger_age=validated_data['passenger_age'],
                passenger_gender=validated_data['passenger_gender'],
                email=validated_data['email'],
                phone=validated_data['phone'],
                meal=meal,
                travel_date=travel_date
            )
            
            seat.is_booked = True
            seat.save()
            
            return booking
