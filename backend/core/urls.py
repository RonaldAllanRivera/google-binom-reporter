# backend/core/urls.py
from django.contrib import admin
from django.urls import path
from reports import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/google/', views.google_auth_url),
    path('api/auth/google/callback/', views.google_auth_callback),
    path('api/google-ads/test/', views.google_ads_test_view),
    path('api/report/generate/', views.generate_report),
    path('api/google-ads/manager-check/', views.google_ads_manager_check),
    path('api/combined-report/', views.combined_report_view),
]
