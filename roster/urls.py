from django.urls import path, include
from rest_framework.routers import DefaultRouter
from roster import views 
from roster.views import home, roster_create, staff_list, statistics_view, roster_list, bakery_product_view, manage_bakery_products,modify_product_info,submit_revenue, revenue_dashboard, login_view, logout_view,export_report, generate_roster_excel_file
from django.conf import settings
from django.conf.urls.static import static

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
        path('modify-product-info/', modify_product_info, name='modify_product_info'),  # New URL for Modify Product Info
    path('api/', include(router.urls)),
    path('api/shift-counts/', views.api_shift_counts, name='api_shift_counts'),  # New API endpoint
     path('manage_staff/', views.manage_staff, name='manage_staff'),  # Add this line
     path('submit-revenue/', submit_revenue, name='submit_revenue'),
    path('revenue_dashboard/', revenue_dashboard, name='revenue_dashboard'),
     path('home/', login_view, name='login_view'),
     path('logout/', logout_view, name='logout'),
      path('export/', export_report, name='export_report'),
       path('generate-roster-excel/', generate_roster_excel_file, name='generate_roster_excel'),
    
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)