from django.urls import path
from . import views

urlpatterns = [
    path('', views.roster_list, name='roster_list'),
    path('create/', views.roster_create, name='roster_create'),  # Roster creation page
    path('staff/', views.staff_list, name='staff_list'),  # Active staff list
]