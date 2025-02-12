from django.urls import path, include
from rest_framework.routers import DefaultRouter
from roster import views 
from roster.views import home, roster_create, staff_list, statistics_view, roster_list, bakery_product_view, manage_bakery_products

router = DefaultRouter()
router.register(r'staff', views.StaffViewSet)
router.register(r'rosters', views.RosterViewSet)

urlpatterns = [
     path('', home, name='home'),  # Home page for the root URL
    path('create/', roster_create, name='roster_create'),
    path('list/', staff_list, name='staff_list'),
     path('roster/', roster_list, name='roster_list'), 
    path('statistics/', statistics_view, name='statistics_view'),
      path('bakery/', bakery_product_view, name='bakery_products'),
      path('restock-product/', views.restock_product, name='restock_product'),
       path('manage-bakery-products/', manage_bakery_products, name='manage_bakery_products'),
    path('api/', include(router.urls)),
    path('api/shift-counts/', views.api_shift_counts, name='api_shift_counts'),  # New API endpoint
    
]