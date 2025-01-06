from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('roster.urls')),
    path('roster/', include('roster.urls')),  # Include roster app URLs
]