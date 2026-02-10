from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Bus, Seat, Booking, Meal

class SecurityTest(TestCase):
    def setUp(self):
        # Create Users
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        
        # Create Resources
        self.bus = Bus.objects.create(name="Test Bus", source="A", destination="B")
        self.seat1 = Seat.objects.create(bus=self.bus, seat_number="L1", seat_type="LOWER", price=500)
        self.seat2 = Seat.objects.create(bus=self.bus, seat_number="L2", seat_type="LOWER", price=500)
        
        # Create Booking for User 1
        self.booking1 = Booking.objects.create(
            user=self.user1,
            seat=self.seat1,
            passenger_name="User One",
            passenger_age=30,
            passenger_gender="M",
            email="u1@example.com",
            phone="1234567890",
            total_amount=500,
            status='CONFIRMED'
        )
        self.seat1.is_booked = True
        self.seat1.save()

    def test_booking_creation_associates_user(self):
        self.client.login(username='user2', password='password')
        data = {
            'name': 'User Two',
            'age': '25',
            'gender': 'F',
            'email': 'u2@example.com',
            'phone': '0987654321',
            'travel_date': '2026-12-31'
        }
        self.client.post(reverse('checkout', args=[self.seat2.id]), data)
        
        # Check if booking created and associated with user2
        booking = Booking.objects.get(seat=self.seat2)
        self.assertEqual(booking.user, self.user2)

    def test_my_bookings_privacy(self):
        # Login as User 2
        self.client.login(username='user2', password='password')
        
        # User 2 should NOT see User 1's booking
        response = self.client.get(reverse('my_bookings'))
        self.assertNotContains(response, "User One")
        self.assertNotContains(response, self.booking1.pnr)
        
        # Create a booking for User 2 (manually for speed)
        booking2 = Booking.objects.create(
            user=self.user2,
            seat=self.seat2,
            passenger_name="User Two",
            passenger_age=25,
            passenger_gender="F",
            email="u2@example.com",
            phone="0987654321",
            total_amount=500,
            status='CONFIRMED'
        )
        
        # User 2 SHOULD see their own booking
        response = self.client.get(reverse('my_bookings'))
        self.assertContains(response, "User Two")
        self.assertContains(response, booking2.pnr)

    def test_cancel_booking_security(self):
        # Login as User 2
        self.client.login(username='user2', password='password')
        
        # User 2 tries to cancel User 1's booking
        url = reverse('cancel_booking', args=[self.booking1.pnr])
        response = self.client.get(url, follow=True) # Follow redirect
        
        # Request should be rejected (redirected to my_bookings with error)
        self.assertRedirects(response, reverse('my_bookings'))
        # Reload booking from DB to ensure it wasn't cancelled
        self.booking1.refresh_from_db()
        self.assertEqual(self.booking1.status, 'CONFIRMED')
        
        # Message should verify authorized access denial
        messages = list(response.context['messages'])
        self.assertTrue(any("not authorized" in str(m) for m in messages))

    def test_cancel_booking_success_for_owner(self):
        # Login as User 1
        self.client.login(username='user1', password='password')
        
        # User 1 cancels their own booking
        url = reverse('cancel_booking', args=[self.booking1.pnr])
        response = self.client.get(url, follow=True)
        
        self.booking1.refresh_from_db()
        self.assertEqual(self.booking1.status, 'CANCELLED')
