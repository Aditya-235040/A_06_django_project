from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random
import string

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('category', 'name')
        
    def __str__(self):
        return f"{self.category.name} - {self.name}"

class OTPRequest(models.Model):
    phone = models.CharField(max_length=15)
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_valid(self):
        # OTP valid for 10 minutes
        return timezone.now() < self.created_at + timezone.timedelta(minutes=10)

    @classmethod
    def generate_otp(cls):
        return ''.join(random.choices(string.digits, k=6))

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('CUSTOMER', 'Customer'),
        ('PROVIDER', 'Service Provider'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class ProviderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile')
    business_name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)
    upi_id = models.CharField(max_length=100, blank=True, null=True, help_text="UPI ID for receiving payments")
    booking_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Fixed booking amount")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.business_name

class Staff(models.Model):
    """Staff member model for managing employees"""
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='staff_members', null=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    position = models.CharField(max_length=50, default='Staff')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Customer(models.Model):
    """Customer model for appointment bookings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile', null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.phone}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('rescheduled', 'Rescheduled'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='appointments')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='appointments')
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='all_appointments', null=True)
    appointment_date = models.DateTimeField()
    time_slot = models.CharField(max_length=50, blank=True, null=True)
    service_type = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    whatsapp_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date']
    
    def __str__(self):
        return f"{self.customer.name} - {self.appointment_date.strftime('%Y-%m-%d %H:%M')}"

class Notification(models.Model):
    """WhatsApp notification logs"""
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='sent')
    
    def __str__(self):
        return f"Notification for {self.appointment.customer.name}"