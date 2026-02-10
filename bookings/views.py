from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from .models import Bus, Seat, Booking, Meal
from .ml_utils import predict_booking_confirmation
from decimal import Decimal
from django.utils import timezone
import re

def home(request):
    buses = Bus.objects.all()
    return render(request, 'bookings/home.html', {'buses': buses})

def seat_selection(request, bus_id=None):
    if bus_id:
        bus = get_object_or_404(Bus, id=bus_id)
    else:
        # Fallback for old links or direct access (redirect to home or pick first)
        bus = Bus.objects.first()
    
    if not bus:
        messages.error(request, "No bus scheduled currently.")
        return redirect('home')
        
    seats = Seat.objects.filter(bus=bus).order_by('id')
    lower_deck = seats.filter(seat_type='LOWER')
    upper_deck = seats.filter(seat_type='UPPER')
    stops = bus.stops.all()
    
    context = {
        'bus': bus,
        'lower_deck': lower_deck,
        'upper_deck': upper_deck,
        'stops': stops
    }
    return render(request, 'bookings/seat_selection.html', context)

@login_required(login_url='login')
def checkout_bulk(request):
    if request.method == 'POST':
        # CASE 1: Processing the booking submission (Confirm Booking)
        if 'confirm_booking' in request.POST:
            seat_ids = request.POST.getlist('seat_ids')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            travel_date_str = request.POST.get('travel_date')
            
            bookings = []
            
            try:
                # 1. Validation Logic
                if not seat_ids:
                    raise Exception("No seats to book.")

                # Phone Check
                if phone:
                    if not phone.isdigit() or len(phone) != 10:
                        raise Exception("Phone number must be exactly 10 digits.")

                for seat_id in seat_ids:
                    name = request.POST.get(f'name_{seat_id}')
                    age = request.POST.get(f'age_{seat_id}')
                    gender = request.POST.get(f'gender_{seat_id}')
                    if not name or not age or not gender:
                        raise Exception("All passenger details are required.")
                    
                    # Name Validation
                    if not re.match(r"^[a-zA-Z\s]+$", name):
                         raise Exception(f"Invalid name '{name}'. Only letters and spaces allowed.")

                # 2. Transaction
                with transaction.atomic():
                    for seat_id in seat_ids:
                        seat = Seat.objects.select_for_update().get(id=seat_id)
                        if seat.is_booked:
                            raise Exception(f"Seat {seat.seat_number} is already booked.")
                        
                        name = request.POST.get(f'name_{seat_id}')
                        age = request.POST.get(f'age_{seat_id}')
                        gender = request.POST.get(f'gender_{seat_id}')
                        meal_id = request.POST.get(f'meal_{seat_id}')
                        
                        selected_meal = None
                        total_price = seat.price
                        if meal_id:
                            selected_meal = Meal.objects.get(id=meal_id)
                            total_price += selected_meal.price
                            
                        prediction_score = predict_booking_confirmation(
                            date=travel_date_str, 
                            seat_count=len(seat_ids), 
                            meal_included=bool(selected_meal)
                        )
                        
                        booking = Booking.objects.create(
                            passenger_name=name,
                            passenger_age=age,
                            passenger_gender=gender,
                            email=email,
                            phone=phone,
                            seat=seat,
                            meal=selected_meal,
                            travel_date=travel_date_str if travel_date_str else timezone.now(),
                            total_amount=total_price,
                            prediction_score=prediction_score,
                            status='CONFIRMED',
                            user=request.user
                        )
                        seat.is_booked = True
                        seat.save()
                        bookings.append(booking)
                        
                    return render(request, 'bookings/success.html', {'bookings': bookings})
                    
            except Exception as e:
                # ERROR HANDLING: Stay on Checkout Page
                messages.error(request, f"Error: {str(e)}")
                
                # Re-fetch data to re-render the form
                seats = Seat.objects.filter(id__in=seat_ids)
                meals = Meal.objects.all()
                from django.utils import timezone
                
                # Preserve input data for seat fields
                for seat in seats:
                    seat.prev_name = request.POST.get(f'name_{seat.id}', '')
                    seat.prev_age = request.POST.get(f'age_{seat.id}', '')
                    seat.prev_gender = request.POST.get(f'gender_{seat.id}', '')
                    seat.prev_meal = request.POST.get(f'meal_{seat.id}', '')

                context = {
                    'seats': seats,
                    'meals': meals,
                    'today_date': timezone.now().date().isoformat(),
                    'total_seats': len(seats),
                    'form_data': request.POST, # Pass entire POST data for top-level fields
                }
                return render(request, 'bookings/checkout.html', context)

        # CASE 2: Initial request from seat selection (arriving at checkout)
        selected_seat_ids = request.POST.getlist('selected_seats')
        if not selected_seat_ids:
             messages.error(request, "No seats selected.")
             return redirect('seat_selection')
             
        seats = Seat.objects.filter(id__in=selected_seat_ids)
        meals = Meal.objects.all()
        from django.utils import timezone
        
        context = {
            'seats': seats,
            'meals': meals,
            'today_date': timezone.now().date().isoformat(),
            'total_seats': len(seats)
        }
        return render(request, 'bookings/checkout.html', context)
    
    return redirect('seat_selection')

@login_required(login_url='login')
def checkout(request, seat_id):
    seat = get_object_or_404(Seat, id=seat_id)
    meals = Meal.objects.all()
    
    if seat.is_booked:
        messages.error(request, "This seat is already booked.")
        return redirect('seat_selection')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        travel_date_str = request.POST.get('travel_date')
        meal_id = request.POST.get('meal')
        
        try:
            # 1. Validation
            try:
                age = int(age)
                if age < 1 or age > 100:
                    raise ValueError("Age must be between 1 and 100.")
            except ValueError:
                raise ValueError("Invalid age.")

            if not name or not age or not gender:
                 raise Exception("All passenger details are required.")

            # Name Validation
            if not re.match(r"^[a-zA-Z\s]+$", name):
                 raise Exception("Name must contain only letters and spaces.")

            if phone:
                if not phone.isdigit() or len(phone) != 10:
                    raise Exception("Phone number must be exactly 10 digits.")
            
            # 2. Preparation
            selected_meal = None
            total_price = seat.price
            
            if meal_id:
                selected_meal = Meal.objects.get(id=meal_id)
                total_price += selected_meal.price
                
            prediction_score = predict_booking_confirmation(
                date=travel_date_str, 
                seat_count=1, 
                meal_included=bool(selected_meal)
            )
            
            # 3. Transaction
            with transaction.atomic():
                seat = Seat.objects.select_for_update().get(id=seat.id)
                if seat.is_booked:
                    raise Exception("Seat just got booked!")
                
                booking = Booking.objects.create(
                    passenger_name=name,
                    passenger_age=age,
                    passenger_gender=gender,
                    email=email,
                    phone=phone,
                    seat=seat,
                    meal=selected_meal,
                    travel_date=travel_date_str if travel_date_str else timezone.now(),
                    total_amount=total_price,
                    prediction_score=prediction_score,
                    status='CONFIRMED',
                    user=request.user
                )
                
                seat.is_booked = True
                seat.save()
                
                return redirect('booking_success', pnr=booking.pnr)
                
        except Exception as e:
            # ERROR HANDLING: Stay on page
            messages.error(request, str(e))
            # Fall through - pass current input back to template
            pass 

    from django.utils import timezone
    
    # Store previous input in seat object for template to use (unifying with bulk logic)
    if request.method == 'POST':
        seat.prev_name = request.POST.get('name', '')
        seat.prev_age = request.POST.get('age', '')
        seat.prev_gender = request.POST.get('gender', '')
        seat.prev_meal = request.POST.get('meal', '')
    
    context = {
        'seats': [seat],
        'meals': meals,
        'today_date': timezone.now().date().isoformat(),
        'form_data': request.POST if request.method == 'POST' else {}
    }
    return render(request, 'bookings/checkout.html', context)

def booking_success(request, pnr):
    booking = get_object_or_404(Booking, pnr=pnr)
    return render(request, 'bookings/success.html', {'booking': booking})

@login_required(login_url='login')
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})

@login_required(login_url='login')
def cancel_booking(request, pnr):
    booking = get_object_or_404(Booking, pnr=pnr)
    
    if booking.user != request.user:
        messages.error(request, "You are not authorized to cancel this booking.")
        return redirect('my_bookings')
        
    if booking.status != 'CANCELLED':
        booking.status = 'CANCELLED'
        booking.seat.is_booked = False
        booking.seat.save()
        booking.save()
        messages.success(request, f"Booking {pnr} cancelled successfully.")
    else:
        messages.warning(request, "Booking is already cancelled.")
    return redirect('my_bookings')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'bookings/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

