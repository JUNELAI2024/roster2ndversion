# bakery_roster/urls.py
from django.urls import path, include
from roster import views  # Import views from the roster app
from django.contrib import admin


urlpatterns = [
    path('', views.home, name='home'),  # Add this line for the home view
    path('home/', views.home, name='home_redirect'),  # Home view at /home
    path('admin/', admin.site.urls),       # Admin interface URL
    path('roster/', include('roster.urls')),  # Ensure this points to your roster app
    # Remove the following line to avoid redundancy
    # path('roster/', include('roster.urls')),  
]