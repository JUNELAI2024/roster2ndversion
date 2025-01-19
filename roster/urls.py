from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'staff', views.StaffViewSet)
router.register(r'rosters', views.RosterViewSet)

urlpatterns = [
    path('', views.roster_list, name='roster_list'),
    path('create/', views.roster_create, name='roster_create'),
    path('staff/', views.staff_list, name='staff_list'),
    path('statistics/', views.statistics_view, name='statistics'),  # Statistics page
    path('api/', include(router.urls)),
]