from django.urls import path
from roster.views import home, roster_create, staff_list, statistics_view, roster_list

urlpatterns = [
    path('', home, name='home'),  # Home page for the root URL
    path('create/', roster_create, name='roster_create'),
    path('list/', staff_list, name='staff_list'),
    path('statistics/', statistics_view, name='statistics_view'),
    path('roster/', roster_list, name='roster_list'), 
]