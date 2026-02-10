from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

router = DefaultRouter()
router.register(r'buses', api_views.BusViewSet)
router.register(r'meals', api_views.MealViewSet)
router.register(r'seats', api_views.SeatViewSet)
router.register(r'bookings', api_views.BookingViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('seats/<int:bus_id>/', views.seat_selection, name='seat_selection'),
    path('seats/', views.seat_selection, name='seat_selection_default'), # Fallback
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('checkout/bulk/', views.checkout_bulk, name='checkout_bulk'),
    path('checkout/<int:seat_id>/', views.checkout, name='checkout'),
    path('success/<str:pnr>/', views.booking_success, name='booking_success'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel/<str:pnr>/', views.cancel_booking, name='cancel_booking'),
    
    # API Routes
    path('api/', include(router.urls)),
]
