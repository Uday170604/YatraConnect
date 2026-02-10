
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sleeper_bus_project.settings')
django.setup()

# OVERRIDE SETTINGS FOR VERIFICATION
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from django.test import Client
from django.contrib.auth.models import User
from bookings.models import Bus, Seat, Booking, Meal
from django.urls import reverse

def run_verification():
    print(">>> STARTING BOOKING FLOW VERIFICATION >>>")
    
    # Clean previous run
    try:
        User.objects.get(username='verifier').delete()
    except User.DoesNotExist:
        pass
    
    # 1. Setup Data
    print("\n[1] Setting up test data...")
    try:
        user = User.objects.create_user(username='verifier', password='password123')
        bus = Bus.objects.create(name="Verification Bus", source="A", destination="B")
        seat = Seat.objects.create(bus=bus, seat_number="V1", seat_type="LOWER", price=1000)
        print("    - User created: 'verifier'")
        print("    - Bus created: 'Verification Bus'")
        print("    - Seat created: 'V1'")
    except Exception as e:
        print(f"!!! Setup Failed: {e}")
        return

    client = Client()

    # 2. Login
    print("\n[2] Attempting Login...")
    login_success = client.login(username='verifier', password='password123')
    if login_success:
        print("    - Login SUCCESS")
    else:
        print("    !!! Login FAILED")
        return

    # 3. Access Seat Selection
    print("\n[3] Accessing Seat Selection page...")
    try:
        url = reverse('seat_selection', args=[bus.id])
        response = client.get(url)
        if response.status_code == 200:
             print("    - Page Load SUCCESS (200 OK)")
        else:
             print(f"    !!! Page Load FAILED (Status: {response.status_code})")
             return
    except Exception as e:
        print(f"    !!! Error accessing page: {e}")
        return

    # 4. Perform Booking (Checkout)
    print("\n[4] Submitting Booking Form...")
    try:
        checkout_url = reverse('checkout', args=[seat.id])
        data = {
            'name': 'Verify User',
            'age': '28',
            'gender': 'M',
            'email': 'verify@example.com',
            'phone': '9876543210',
            'travel_date': '2026-05-20',
            'meal': '' # No meal
        }
        response = client.post(checkout_url, data)
        
        if response.status_code == 302:
            print("    - Submission Redirected (Expected) -> SUCCESS")
            print(f"    - Redirect Location: {response.url}")
        else:
            print(f"    !!! Submission FAILED (Status: {response.status_code})")
            # Print form errors if any
            if 'form_data' in response.context:
                 print(f"    - Context Data: {response.context.get('form_data')}")
            return
    except Exception as e:
         print(f"    !!! Error submitting form: {e}")
         return

    # 5. Verify Database
    print("\n[5] Verifying Database Record...")
    try:
        booking = Booking.objects.get(seat=seat)
        print(f"    - Booking Found: PNR {booking.pnr}")
        print(f"    - Status: {booking.status}")
        print(f"    - Passenger: {booking.passenger_name}")
        print(f"    - Owner: {booking.user.username}")
        
        if booking.user == user and booking.status == 'CONFIRMED':
            print("\n>>> VERIFICATION COMPLETE: BOOKING SYSTEM IS WORKING CORRECTLY <<<")
        else:
             print("\n!!! VERIFICATION FAILED: Data mismatch !!!")
    except Booking.DoesNotExist:
        print("\n!!! VERIFICATION FAILED: Booking not found in DB !!!")

    # Cleanup
    print("\n[Cleanup] Removing test data...")
    try:
        user.delete()
        bus.delete() 
        # Seat deletes cascade from Bus, Booking deletes cascade from Seat... actually Booking has CASCADE on Seat? 
        # Yes, models.py says seat = ForeignKey(Seat, on_delete=models.CASCADE)
    except:
        pass

if __name__ == "__main__":
    run_verification()
