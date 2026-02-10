
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sleeper_bus_project.settings')
django.setup()

from bookings.models import Bus, Seat, BusStop

def add_route():
    print("Adding Somnath to Dwarka route...")
    
    # 1. Create Bus
    bus_name = "Coastal Pilgrim Special"
    source = "Somnath"
    destination = "Dwarka"
    
    # Check if already exists to prevent duplicates
    if Bus.objects.filter(source=source, destination=destination).exists():
        print(f"Bus from {source} to {destination} already exists.")
        return

    bus = Bus.objects.create(
        name=bus_name,
        source=source,
        destination=destination,
        departure_time="08:00:00",
        arrival_time="12:00:00",
        total_seats=30
    )
    print(f"Created Bus: {bus}")

    # 2. Add Stops
    stops_data = [
        {'name': 'Veraval', 'time': '08:30:00', 'num': 1},
        {'name': 'Chorwad', 'time': '09:15:00', 'num': 2},
        {'name': 'Porbandar', 'time': '10:30:00', 'num': 3},
    ]
    
    for stop in stops_data:
        BusStop.objects.create(
            bus=bus,
            name=stop['name'],
            arrival_time=stop['time'],
            stop_number=stop['num']
        )
        print(f"  - Added Stop: {stop['name']}")

    # 3. Add Seats
    # Lower Deck (10 seats) - L1 to L10
    for i in range(1, 11):
        Seat.objects.create(
            bus=bus,
            seat_number=f"L{i}",
            seat_type='LOWER',
            price=600.00 # Slightly cheaper day bus? Or standard. Let's say 600.
        )
    
    # Upper Deck (20 seats) - U1 to U20
    for i in range(1, 21):
        Seat.objects.create(
            bus=bus,
            seat_number=f"U{i}",
            seat_type='UPPER',
            price=800.00
        )
        
    print(f"  - Added {bus.seats.count()} seats.")
    print("Route added successfully!")

if __name__ == "__main__":
    add_route()
