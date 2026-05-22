from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Staff, Customer, Appointment, Notification, ProviderProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role', 'phone')}),
    )

@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'created_at']

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'position', 'is_active']
    list_filter = ['is_active', 'position']
    search_fields = ['name', 'phone', 'email']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'created_at']
    search_fields = ['name', 'phone']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'staff', 'appointment_date', 'status', 'whatsapp_sent']
    list_filter = ['status', 'whatsapp_sent', 'appointment_date']
    search_fields = ['customer__name', 'service_type']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'sent_at', 'status']
    list_filter = ['status', 'sent_at']