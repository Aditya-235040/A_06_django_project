import re
from django.utils import timezone
from django import forms
from django.contrib.auth import get_user_model
from .models import Staff, Customer, Appointment

User = get_user_model()

def validate_phone(phone):
    """Utility to check if phone is valid digits"""
    clean_phone = re.sub(r'\D', '', str(phone))
    if len(clean_phone) < 10:
        raise forms.ValidationError("Phone number must be at least 10 digits.")
    return clean_phone

class StaffForm(forms.ModelForm):
    """Form for creating/editing staff members"""
    class Meta:
        model = Staff
        fields = ['name', 'phone', 'email', 'position']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter staff name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'position': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter position'}),
        }

    def clean_phone(self):
        return validate_phone(self.cleaned_data.get('phone'))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            qs = Staff.objects.filter(email=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("A staff member with this email already exists.")
        return email

class CustomerForm(forms.ModelForm):
    """Form for creating customers"""
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email (optional)'}),
        }

    def clean_phone(self):
        return validate_phone(self.cleaned_data.get('phone'))

class AppointmentForm(forms.ModelForm):
    """Form for creating/editing appointments"""
    class Meta:
        model = Appointment
        fields = ['customer', 'staff', 'appointment_date', 'time_slot', 'service_type', 'notes']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'staff': forms.Select(attrs={'class': 'form-select'}),
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time_slot': forms.Select(choices=[
                ('09:00 AM', '09:00 AM'), ('10:00 AM', '10:00 AM'),
                ('11:00 AM', '11:00 AM'), ('12:00 PM', '12:00 PM'),
                ('01:00 PM', '01:00 PM'), ('02:00 PM', '02:00 PM'),
                ('03:00 PM', '03:00 PM'), ('04:00 PM', '04:00 PM'),
                ('05:00 PM', '05:00 PM'), ('06:00 PM', '06:00 PM')
            ], attrs={'class': 'form-select'}),
            'service_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service type'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['customer'].required = False
        
        if user:
            if user.role == 'PROVIDER':
                self.fields['staff'].queryset = Staff.objects.filter(provider=user.provider_profile, is_active=True)
            elif user.role == 'CUSTOMER':
                # For customers, we might want to restrict staff based on some criteria
                # For now, just ensure they are active
                self.fields['staff'].queryset = Staff.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('appointment_date')
        time_slot = cleaned_data.get('time_slot')

        if date:
            from datetime import datetime
            compare_date = date.date() if isinstance(date, datetime) else date
            # We use datetime.now() to get local time for comparison
            now = datetime.now()

            if compare_date < now.date():
                self.add_error('appointment_date', "Appointment date cannot be in the past.")
            elif compare_date == now.date():
                if time_slot:
                    try:
                        time_obj = datetime.strptime(time_slot, "%I:%M %p").time()
                        if time_obj < now.time():
                            self.add_error('time_slot', "Appointment time cannot be in the past.")
                    except ValueError:
                        pass
                elif isinstance(date, datetime):
                    if date.time() < now.time():
                        self.add_error('appointment_date', "Appointment time cannot be in the past.")
                    
        return cleaned_data

class LoginForm(forms.Form):
    """Custom login form"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )