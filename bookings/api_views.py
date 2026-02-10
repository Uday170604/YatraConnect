from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Bus, Meal, Seat, Booking
from .serializers import BusSerializer, MealSerializer, SeatSerializer, BookingSerializer

class BusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bus.objects.all()
    serializer_class = BusSerializer

class MealViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer

class SeatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    
    def get_queryset(self):
        # Allow filtering by bus or availability if needed
        return Seat.objects.all().order_by('id')

class BookingViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    API endpoint that allows Bookings to be viewed or created.
    """
    queryset = Booking.objects.all().order_by('-booking_date')
    serializer_class = BookingSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status == 'CANCELLED':
            return Response({'status': 'booking already cancelled'}, status=status.HTTP_400_BAD_REQUEST)
            
        booking.status = 'CANCELLED'
        booking.seat.is_booked = False
        booking.seat.save()
        booking.save()
        return Response({'status': 'booking cancelled'}, status=status.HTTP_200_OK)
