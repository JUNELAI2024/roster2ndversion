from django.urls import path, include  # Import include for API routing
from rest_framework.routers import DefaultRouter  # Import DRF router
from . import views  # Import your views

# Create a router and register your viewsets with it
router = DefaultRouter()
router.register(r'staff', views.StaffViewSet)  # Register StaffViewSet
router.register(r'rosters', views.RosterViewSet)  # Register RosterViewSet

urlpatterns = [
    path('', views.roster_list, name='roster_list'),  # Roster list page
    path('create/', views.roster_create, name='roster_create'),  # Roster creation page
    path('staff/', views.staff_list, name='staff_list'),  # Active staff list
    path('api/', include(router.urls)),  # Include API routes
]