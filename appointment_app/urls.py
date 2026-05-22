from django.urls import path
from . import views

urlpatterns = [
    path('about-us/', views.about_us, name='about_us'),

    # Auth
    path('', views.user_login, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    # Forgot Password
    path('forgot-password/', views.forgot_password_request, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    
    # Admin Panel
    path('admin-portal/', views.admin_dashboard, name='admin_dashboard'),
    
    # Provider Portal
    path('provider/dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('provider/staff/', views.staff_list, name='staff_list'),
    path('provider/staff/add/', views.add_staff, name='add_staff'),
    path('provider/staff/edit/<int:pk>/', views.edit_staff, name='edit_staff'),
    path('provider/staff/delete/<int:pk>/', views.delete_staff, name='delete_staff'),
    
    # Customer Portal
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    
    # Shared / Unified
    path('appointments/', views.appointments_list, name='appointments_list'),
    path('appointments/add/', views.add_appointment, name='add_appointment'),
    path('appointments/update/<int:pk>/', views.update_appointment, name='update_appointment'),
    path('whatsapp/<int:pk>/', views.send_whatsapp, name='send_whatsapp'),
]
