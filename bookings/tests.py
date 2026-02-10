from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Bus, BusStop, Seat

class BusModelTest(TestCase):
    def setUp(self):
        self.bus = Bus.objects.create(
            name="Test Bus",
            source="A",
            destination="B",
            departure_time="10:00",
            arrival_time="12:00"
        )

    def test_bus_creation(self):
        self.assertEqual(self.bus.name, "Test Bus")
        self.assertEqual(str(self.bus), "Test Bus (A - B)")

    def test_bus_stop_creation(self):
        stop1 = BusStop.objects.create(bus=self.bus, name="Stop 1", arrival_time="10:30", stop_number=1)
        stop2 = BusStop.objects.create(bus=self.bus, name="Stop 2", arrival_time="11:00", stop_number=2)
        
        self.assertEqual(self.bus.stops.count(), 2)
        self.assertEqual(self.bus.stops.first().name, "Stop 1")

class LoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_login_page_renders(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/login.html')

    def test_valid_login(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'password123'})
        self.assertRedirects(response, reverse('home'))
        
        # Check if user is authenticated in session
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Logout (testuser)')

    def test_invalid_login(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200) # Should stay on page
        self.assertContains(response, "Invalid username or password.")

class BusSelectionTest(TestCase):
    def setUp(self):
        self.bus1 = Bus.objects.create(name="Bus 1", source="A", destination="B", departure_time="10:00", arrival_time="12:00")
        self.bus2 = Bus.objects.create(name="Bus 2", source="C", destination="D", departure_time="13:00", arrival_time="15:00")

    def test_home_page_lists_buses(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, "Bus 1")
        self.assertContains(response, "Bus 2")
        self.assertContains(response, f"/seats/{self.bus1.id}/")

    def test_seat_selection_specific_bus(self):
        response = self.client.get(reverse('seat_selection', args=[self.bus2.id]))
        self.assertContains(response, "Bus 2")
        response = self.client.get(reverse('seat_selection', args=[self.bus2.id]))
        self.assertContains(response, "Bus 2")
        self.assertNotContains(response, "Bus 1")

class BookingFlowTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.bus = Bus.objects.create(name="Test Bus", source="A", destination="B")
        self.seat = Seat.objects.create(bus=self.bus, seat_number="L1", seat_type="LOWER", price=500)
    
    def test_checkout_page_loads(self):
        response = self.client.get(reverse('checkout', args=[self.seat.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "L1")

    def test_successful_booking(self):
        # Simulate POST request to book the seat
        data = {
            'name': 'John Doe',
            'age': '30',
            'gender': 'M',
            'email': 'john@example.com',
            'phone': '1234567890', # Valid 10 digit
            'travel_date': '2026-12-31'
        }
        response = self.client.post(reverse('checkout', args=[self.seat.id]), data)
        
        # Should redirect to success page
        self.assertEqual(response.status_code, 302) 
        
        # Check DB
        self.seat.refresh_from_db()
        self.assertTrue(self.seat.is_booked)
        
        from .models import Booking
        self.assertTrue(Booking.objects.filter(seat=self.seat).exists())

class ValidationAuthTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.bus = Bus.objects.create(name="Test Bus", source="A", destination="B")
        self.seat = Seat.objects.create(bus=self.bus, seat_number="L1", seat_type="LOWER", price=500)

    def test_checkout_requires_login(self):
        # Without login
        response = self.client.get(reverse('checkout', args=[self.seat.id]))
        self.assertRedirects(response, f'/login/?next=/checkout/{self.seat.id}/')

    def test_invalid_phone_validation(self):
        self.client.login(username='testuser', password='password123')
        data = {
            'name': 'John Doe', 'age': '30', 'gender': 'M',
            'email': 'john@example.com', 'travel_date': '2026-12-31',
            'phone': '123' # Invalid
        }
        response = self.client.post(reverse('checkout', args=[self.seat.id]), data)
        self.assertEqual(response.status_code, 200) # Stay on page
        self.assertContains(response, "Phone number must be exactly 10 digits")
        # Check input preservation
        self.assertContains(response, 'value="John Doe"')
        self.assertContains(response, 'value="123"') # Preserved bad input

    def test_invalid_name_validation(self):
        self.client.login(username='testuser', password='password123')
        data = {
            'name': 'John123', # Invalid
            'age': '30', 'gender': 'M',
            'email': 'john@example.com', 'travel_date': '2026-12-31',
            'phone': '1234567890'
        }
        response = self.client.post(reverse('checkout', args=[self.seat.id]), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Name must contain only letters and spaces")
        self.assertContains(response, 'value="John123"')
