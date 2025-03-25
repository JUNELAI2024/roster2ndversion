# bakery_roster/urls.py
from django.urls import path, include
from roster import views  # Import views from the roster app
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),  # Add this line for the home view
    path('admin/', admin.site.urls),       # Admin interface URL
    path('roster/', include('roster.urls')),  # Ensure this points to your roster app

    # Remove the following line to avoid redundancy
    # path('roster/', include('roster.urls')),  
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)