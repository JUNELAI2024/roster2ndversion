# bakery_roster/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),       # Admin interface URL
    path('', include('roster.urls')),      # Include URLs from the roster app at root
    # Remove the following line to avoid redundancy
    # path('roster/', include('roster.urls')),  
]