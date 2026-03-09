import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sleeper_bus_project.settings')
django.setup()

from bookings.models import Bus, Seat, Meal, BusStop
from django.utils import timezone

def run():
    print("Populating database...")
    
    # Define Routes Data
    routes = [
        {
            'name': "Royal Sleeper Express",
            'source': "Ahmedabad",
            'destination': "Mumbai",
            'departure': "22:00",
            'arrival': "06:00",
            'stops': [
                {'name': 'Vadodara', 'time': '23:30', 'num': 1},
                {'name': 'Surat', 'time': '01:30', 'num': 2},
                {'name': 'Vapi', 'time': '03:00', 'num': 3},
                {'name': 'Borivali', 'time': '05:30', 'num': 4}
            ]
        },
        {
            'name': "Saurashtra mail",
            'source': "Rajkot",
            'destination': "Ahmedabad",
            'departure': "06:00",
            'arrival': "11:00",
            'stops': [
                {'name': 'Limbdi', 'time': '08:00', 'num': 1},
                {'name': 'Bagodara', 'time': '09:00', 'num': 2},
                {'name': 'Sarkhej', 'time': '10:30', 'num': 3}
            ]
        },
        {
            'name': "Capital Connector",
            'source': "Ahmedabad",
            'destination': "Gandhinagar",
            'departure': "09:00",
            'arrival': "10:30",
            'stops': [
                {'name': 'Sabarmati', 'time': '09:20', 'num': 1},
                {'name': 'Visat', 'time': '09:40', 'num': 2},
                {'name': 'Koba Circle', 'time': '10:00', 'num': 3}
            ]
        },
        {
            'name': "Diamond City Express",
            'source': "Ahmedabad",
            'destination': "Surat",
            'departure': "14:00",
            'arrival': "18:00",
            'stops': [
                {'name': 'Nadiad', 'time': '15:00', 'num': 1},
                {'name': 'Anand', 'time': '15:30', 'num': 2},
                {'name': 'Vadodara', 'time': '16:00', 'num': 3},
                {'name': 'Ankleshwar', 'time': '17:15', 'num': 4}
            ]
        }
    ]

    for route in routes:
        # Create Bus
        bus, created = Bus.objects.get_or_create(
            name=route['name'],
            source=route['source'], # To distinguish same name on diff route if needed, but simple for now
            destination=route['destination'],
            defaults={
                'departure_time': route['departure'],
                'arrival_time': route['arrival']
            }
        )
        if not created:
             # Update times if exists
             bus.departure_time = route['departure']
             bus.arrival_time = route['arrival']
             bus.save()

        print(f"Bus: {bus}")
        
        # Stops
        BusStop.objects.filter(bus=bus).delete() # Reset stops
        for stop in route['stops']:
            BusStop.objects.create(
                bus=bus,
                name=stop['name'],
                arrival_time=stop['time'],
                stop_number=stop['num']
            )

        # Seats - Only creating seats for the first bus to keep it fast, 
        # OR create for all. Let's create for all but check if exists.
        if Seat.objects.filter(bus=bus).exists():
             print(f"Seats already exist for {bus}")
        else:
            seats_data = []
            # Lower Deck (15 seats)
            for i in range(1, 16):
                seats_data.append(Seat(
                    bus=bus,
                    seat_number=f"L{i}",
                    seat_type="LOWER",
                    price=800.00 if route['destination'] != "Gandhinagar" else 150.00
                ))
            # Upper Deck (15 seats)
            for i in range(1, 16):
                seats_data.append(Seat(
                    bus=bus,
                    seat_number=f"U{i}",
                    seat_type="UPPER",
                    price=1000.00 if route['destination'] != "Gandhinagar" else 200.00
                ))
            Seat.objects.bulk_create(seats_data)
            print(f"Created {len(seats_data)} seats for {bus.name}.")
    
    # Meals (Global)
    meals_data = [
        ('Standard Veg Thali', 'VEG', 150.00),
        ('Paneer Butter Masala Combo', 'VEG', 220.00),
        ('Vada Pav & Tea', 'SNACK', 80.00),
        ('Sandwich & Coffee', 'SNACK', 120.00),
    ]
    
    for m_name, m_type, m_price in meals_data:
        Meal.objects.get_or_create(
            name=m_name,
            defaults={'meal_type': m_type, 'price': m_price}
        )
    print("Meals created/verified.")
    
    print("Database population complete.")

if __name__ == '__main__':
    run()
