# pyrefly: ignore [missing-import]
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
import threading
from .models import User, Staff, Customer, Appointment, Notification, ProviderProfile, Category, SubCategory, OTPRequest
from .forms import StaffForm, AppointmentForm
from .utils import send_whatsapp_message


# ============================
# Role Decorators
# ============================

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'ADMIN')(view_func)

def provider_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'PROVIDER')(view_func)

def customer_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == 'CUSTOMER')(view_func)


# ============================
# Public Pages
# ============================

def about_us(request):
    return render(request, 'about_us.html')


# ============================
# Authentication Views
# ============================

def user_login(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    
    if request.method == 'POST':
        uname = request.POST.get('username', '').strip()
        passw = request.POST.get('password')
        role_type = request.POST.get('role_type')

        user = authenticate(request, username=uname, password=passw)
        if user:
            if role_type and user.role != role_type:
                messages.error(request, f'Invalid credentials for {role_type} role.')
            else:
                login(request, user)
                
                # Remember Me logic
                remember_me = request.POST.get('remember_me')
                if remember_me:
                    request.session.set_expiry(1209600) # 2 weeks
                else:
                    request.session.set_expiry(0) # Browser close
                    
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect_by_role(user)
        else:
            if role_type == 'PROVIDER':
                messages.error(request, 'Please register your service in new registration section.')
            else:
                messages.error(request, 'Invalid username and password please register first.')
            
        return render(request, 'login.html', {'submitted_role': role_type})
            
    role_from_url = request.GET.get('role')
    return render(request, 'login.html', {'submitted_role': role_from_url})


def register_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)
    
    if request.method == 'POST':
        uname = request.POST.get('username', '').strip()
        uemail = request.POST.get('email', '').strip()
        upass = request.POST.get('password')
        upass_confirm = request.POST.get('password_confirm')
        urole = request.POST.get('role', 'CUSTOMER')
        ubusiness = request.POST.get('business_name', '').strip()
        uphone = request.POST.get('phone', '').strip()
        ucategory_id = request.POST.get('category')
        usubcategory_id = request.POST.get('subcategory')

        # Security: Only allow CUSTOMER and PROVIDER registration from frontend
        ALLOWED_ROLES = ['CUSTOMER', 'PROVIDER']
        
        if urole not in ALLOWED_ROLES:
            messages.error(request, 'Invalid role selection.')
        elif not uname or not uemail or not upass:
            messages.error(request, 'All fields are required.')
        elif urole == 'CUSTOMER' and not uphone:
            messages.error(request, 'Phone number is required for customers.')
        elif upass != upass_confirm:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=uname).exists():
            messages.error(request, 'Username already taken.')
        elif User.objects.filter(email=uemail).exists():
            messages.error(request, 'An account with this email already exists.')
        elif urole == 'CUSTOMER' and Customer.objects.filter(phone=uphone).exists():
            messages.error(request, 'A customer with this phone number already exists.')
        else:
            user = User.objects.create_user(username=uname, email=uemail, password=upass, role=urole)
            
            # Create profiles based on role
            if urole == 'CUSTOMER':
                Customer.objects.create(user=user, name=uname, email=uemail, phone=uphone)
            elif urole == 'PROVIDER':
                business_name = ubusiness if ubusiness else f"{uname}'s Business"
                
                raw_amount = request.POST.get('booking_amount')
                try:
                    booking_amount = float(raw_amount) if raw_amount else 0.00
                except ValueError:
                    booking_amount = 0.00
                    
                provider = ProviderProfile.objects.create(
                    user=user, 
                    business_name=business_name,
                    upi_id=request.POST.get('upi_id'),
                    booking_amount=booking_amount
                )
                if ucategory_id:
                    provider.category_id = ucategory_id
                if usubcategory_id:
                    provider.subcategory_id = usubcategory_id
                provider.save()
                
                # Automatically create a default staff member so the provider is instantly bookable
                Staff.objects.create(
                    provider=provider,
                    name=f"{uname} (Main)",
                    phone=uphone if uphone else "Not Provided",
                    email=uemail,
                    position="Owner",
                    is_active=True
                )
            
            messages.success(request, f'Account created successfully! Please log in.')
            return redirect('login')
            
    categories = Category.objects.all()
    return render(request, 'register.html', {'categories': categories})


def redirect_by_role(user):
    if user.role == 'ADMIN':
        return redirect('admin_dashboard')
    elif user.role == 'PROVIDER':
        return redirect('provider_dashboard')
    else:
        return redirect('customer_dashboard')


def user_logout(request):
    role = getattr(request.user, 'role', 'CUSTOMER') if request.user.is_authenticated else 'CUSTOMER'
    logout(request)
    messages.success(request, 'You have been logged out.')
    from django.urls import reverse
    return redirect(f"{reverse('login')}?role={role}")

# ============================
# Forgot Password Flow
# ============================

def forgot_password_request(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        # Check if user with this phone exists in Customer (since only customers have explicit phone in UI for now, though providers might. We will check Customer or User model)
        user_exists = User.objects.filter(customer_profile__phone=phone).exists() or User.objects.filter(phone=phone).exists()
        
        # We will generate OTP anyway to not leak info, or we can just send it.
        otp = OTPRequest.generate_otp()
        OTPRequest.objects.filter(phone=phone).delete() # clear old ones
        OTPRequest.objects.create(phone=phone, otp=otp)
        
        # Simulate sending OTP
        print(f"--- SIMULATING OTP SENDING ---")
        print(f"Sending OTP {otp} to phone {phone}")
        print(f"------------------------------")
        
        # Send via WhatsApp using pywhatkit
        formatted_phone = ''.join(filter(str.isdigit, str(phone)))
        if not formatted_phone.startswith('+'):
            if len(formatted_phone) == 10:
                formatted_phone = f"+91{formatted_phone}"
            else:
                formatted_phone = f"+{formatted_phone}"
                
        text = f"Your AppointOS password reset OTP is: {otp}. It is valid for 10 minutes."
        
        try:
            threading.Thread(target=send_whatsapp_message, args=(formatted_phone, text)).start()
            messages.success(request, "An OTP is being sent to your WhatsApp number.")
        except Exception as e:
            messages.error(request, f"Failed to initiate WhatsApp OTP: {str(e)}")
            
        request.session['reset_phone'] = phone
        return redirect('verify_otp')
        
    return render(request, 'forgot_password.html', {'step': 'request'})

def verify_otp(request):
    phone = request.session.get('reset_phone')
    if not phone:
        return redirect('forgot_password')
        
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        otp_req = OTPRequest.objects.filter(phone=phone, otp=otp_entered).first()
        
        if otp_req and otp_req.is_valid():
            otp_req.is_verified = True
            otp_req.save()
            return redirect('reset_password')
        else:
            messages.error(request, "Invalid or expired OTP.")
            
    return render(request, 'forgot_password.html', {'step': 'verify'})

def reset_password(request):
    phone = request.session.get('reset_phone')
    if not phone:
        return redirect('forgot_password')
        
    otp_req = OTPRequest.objects.filter(phone=phone, is_verified=True).first()
    if not otp_req:
        messages.error(request, "Please verify OTP first.")
        return redirect('verify_otp')
        
    if request.method == 'POST':
        new_pass = request.POST.get('password')
        confirm_pass = request.POST.get('password_confirm')
        
        if new_pass != confirm_pass:
            messages.error(request, "Passwords do not match.")
        elif len(new_pass) < 6:
            messages.error(request, "Password must be at least 6 characters.")
        else:
            # Update password for the user matching this phone
            customer = Customer.objects.filter(phone=phone).first()
            if customer:
                user = customer.user
            else:
                user = User.objects.filter(phone=phone).first()
                
            if user:
                user.set_password(new_pass)
                user.save()
                otp_req.delete()
                del request.session['reset_phone']
                messages.success(request, "Password reset successfully. You can now log in.")
                return redirect('login')
            else:
                messages.error(request, "User not found.")
                
    return render(request, 'forgot_password.html', {'step': 'reset'})


# ============================
# Dashboards
# ============================

@admin_required
def admin_dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'total_providers': User.objects.filter(role='PROVIDER').count(),
        'total_customers': User.objects.filter(role='CUSTOMER').count(),
        'total_appointments': Appointment.objects.count(),
        'recent_appointments': Appointment.objects.all()[:10],
    }
    return render(request, 'dashboards/admin.html', context)


@provider_required
def provider_dashboard(request):
    profile = request.user.provider_profile
    appointments = Appointment.objects.filter(provider=profile)
    
    context = {
        'profile': profile,
        'appointments': appointments.order_by('-appointment_date')[:10],
        'staffs': profile.staff_members.filter(is_active=True),
        'stats': {
            'pending': appointments.filter(status='pending').count(),
            'confirmed': appointments.filter(status='confirmed').count(),
            'total_staff': profile.staff_members.count(),
        }
    }
    return render(request, 'dashboards/provider.html', context)


@customer_required
def customer_dashboard(request):
    profile = request.user.customer_profile
    appointments = Appointment.objects.filter(customer=profile)
    staffs = Staff.objects.filter(is_active=True).select_related('provider').order_by('provider__business_name', 'name')
    
    context = {
        'profile': profile,
        'upcoming': appointments.filter(appointment_date__gte=timezone.now()).order_by('appointment_date'),
        'history': appointments.filter(appointment_date__lt=timezone.now()).order_by('-appointment_date'),
        'staffs': staffs,
        'categories': Category.objects.prefetch_related('subcategories').all(),
    }
    return render(request, 'dashboards/customer.html', context)


# ============================
# Staff Management (Provider Only)
# ============================

@provider_required
def staff_list(request):
    staffs = request.user.provider_profile.staff_members.filter(is_active=True)
    form = StaffForm()
    return render(request, 'staff.html', {'staffs': staffs, 'form': form})


@provider_required
def add_staff(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            staff = form.save(commit=False)
            staff.provider = request.user.provider_profile
            staff.save()
            messages.success(request, 'Staff member added successfully.')
        else:
            for field, errors in form.errors.items():
                messages.error(request, f'{field.capitalize()}: {", ".join(errors)}')
    return redirect('staff_list')


@provider_required
def edit_staff(request, pk):
    staff = get_object_or_404(Staff, pk=pk, provider=request.user.provider_profile)
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, f'{staff.name} updated successfully.')
        else:
            for field, errors in form.errors.items():
                messages.error(request, f'{field.capitalize()}: {", ".join(errors)}')
    return redirect('staff_list')


@provider_required
def delete_staff(request, pk):
    staff = get_object_or_404(Staff, pk=pk, provider=request.user.provider_profile)
    staff.is_active = False
    staff.save()
    messages.success(request, f'{staff.name} has been removed.')
    return redirect('staff_list')


# ============================
# Appointment Management
# ============================

@login_required
def appointments_list(request):
    if request.user.role == 'ADMIN':
        appointments = Appointment.objects.all()
        staffs = Staff.objects.filter(is_active=True).select_related('provider').order_by('provider__business_name', 'name')
    elif request.user.role == 'PROVIDER':
        provider = request.user.provider_profile
        appointments = Appointment.objects.filter(provider=provider)
        staffs = provider.staff_members.filter(is_active=True)
    else:
        # Customers only see their own appointments
        appointments = Appointment.objects.filter(customer=request.user.customer_profile)
        # For new appointments, customers see all active staff (can be further refined)
        staffs = Staff.objects.filter(is_active=True).select_related('provider').order_by('provider__business_name', 'name')
        
    context = {
        'appointments': appointments.order_by('-appointment_date'),
        'staffs': staffs
    }
    return render(request, 'appointments.html', context)


@login_required
def add_appointment(request):
    if request.method == 'POST':
        post_data = request.POST.copy()
        appointment_date = post_data.get('appointment_date', '')
        time_slot = post_data.get('time_slot', '')
        if appointment_date and time_slot and 'T' not in appointment_date:
            from datetime import datetime
            try:
                slot_time = datetime.strptime(time_slot, "%I:%M %p").strftime("%H:%M")
                post_data['appointment_date'] = f"{appointment_date}T{slot_time}"
            except ValueError:
                pass

        form = AppointmentForm(post_data, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            
            # Security Check: Ensure staff member belongs to a valid provider
            # and if current user is PROVIDER, it's their own staff
            if request.user.role == 'PROVIDER':
                if appointment.staff.provider != request.user.provider_profile:
                    messages.error(request, 'Invalid staff selection.')
                    return redirect('appointments_list')

            # Handle customer assignment
            if request.user.role == 'CUSTOMER':
                appointment.customer = request.user.customer_profile
            elif request.user.role == 'PROVIDER':
                # Check if we need to create a new customer manually
                customer_name = request.POST.get('customer_name')
                customer_phone = request.POST.get('customer_phone')
                
                if not appointment.customer_id and customer_name and customer_phone:
                    # Clean the phone number for consistent lookup
                    from .forms import validate_phone
                    try:
                        clean_phone = validate_phone(customer_phone)
                        customer, created = Customer.objects.get_or_create(
                            phone=clean_phone,
                            defaults={'name': customer_name}
                        )
                        appointment.customer = customer
                    except Exception as e:
                        messages.error(request, str(e))
                        return redirect('appointments_list')
                elif not appointment.customer_id:
                    messages.error(request, 'Please select a customer or enter new customer details.')
                    return redirect('appointments_list')

            # Link to the correct provider via the staff member
            appointment.provider = appointment.staff.provider
            
            appointment.save()
            
            Notification.objects.create(
                appointment=appointment,
                message=(
                    f"New appointment request from {appointment.customer.name} for "
                    f"{appointment.service_type}. Payment has been marked as complete."
                ),
                status='pending',
            )

            messages.success(request, 'Payment confirmed and appointment request sent successfully!')
        else:
            for field, errors in form.errors.items():
                messages.error(request, f'{field.capitalize()}: {", ".join(errors)}')
        
    return redirect_by_role(request.user)


@login_required
def update_appointment(request, pk):
    if request.method == 'POST':
        appointment = get_object_or_404(Appointment, pk=pk)
        
        # Security check
        if request.user.role == 'PROVIDER' and appointment.provider != request.user.provider_profile:
            messages.error(request, "Access denied.")
            return redirect('appointments_list')
        elif request.user.role == 'CUSTOMER':
            messages.error(request, "Customers cannot update appointments.")
            return redirect('appointments_list')
            
        status = request.POST.get('status')
        staff_id = request.POST.get('staff')
        new_date = request.POST.get('appointment_date')
        new_time = request.POST.get('time_slot')
        
        if status in dict(Appointment.STATUS_CHOICES):
            appointment.status = status
            
            if status == 'rescheduled' and new_date and new_time:
                from datetime import datetime
                try:
                    nd = datetime.strptime(new_date, '%Y-%m-%d').date()
                    now = datetime.now()
                    
                    if nd < now.date():
                        messages.error(request, "Reschedule date cannot be in the past.")
                        return redirect(request.META.get('HTTP_REFERER', 'appointments_list'))
                    elif nd == now.date():
                        try:
                            nt = datetime.strptime(new_time, "%I:%M %p").time()
                            if nt < now.time():
                                messages.error(request, "Reschedule time cannot be in the past.")
                                return redirect(request.META.get('HTTP_REFERER', 'appointments_list'))
                        except ValueError:
                            pass
                except ValueError:
                    pass
                    
                appointment.appointment_date = new_date
                appointment.time_slot = new_time
            
        if staff_id:
            staff = get_object_or_404(Staff, pk=staff_id)
            if request.user.role == 'PROVIDER' and staff.provider != request.user.provider_profile:
                messages.error(request, "Invalid staff selection.")
                return redirect('appointments_list')
            appointment.staff = staff
            # ensure provider linkage is intact
            appointment.provider = staff.provider
            
        appointment.save()
        messages.success(request, 'Appointment updated successfully.')
        
    # Redirect back to where the request came from, or appointments list as fallback
    return redirect(request.META.get('HTTP_REFERER', 'appointments_list'))


@login_required
def send_whatsapp(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if request.user.role == 'PROVIDER' and appointment.provider != request.user.provider_profile:
        messages.error(request, "Access denied.")
        return redirect('provider_dashboard')
        
    if appointment.whatsapp_sent:
        messages.error(request, "Message already sent. You can only send the WhatsApp message once.")
        return redirect(request.META.get('HTTP_REFERER', 'provider_dashboard'))
    
    appointment.whatsapp_sent = True
    appointment.save()
    
    # Send automatically using pywhatkit (opens browser on host)
    phone = ''.join(filter(str.isdigit, str(appointment.customer.phone)))
    # Add country code if missing (assuming India +91 for now, or just leave as is if they provide it)
    if not phone.startswith('+'):
        # Usually pywhatkit requires a country code. We'll prepend +91 for safety or assume the user inputs it.
        if len(phone) == 10:
            phone = f"+91{phone}"
        else:
            phone = f"+{phone}"
            
    default_text = f"Hello {appointment.customer.name},\nThis is a reminder for your appointment:\nService: {appointment.service_type}\nDate: {appointment.appointment_date.strftime('%Y-%m-%d')} at {appointment.time_slot}\nStatus: {appointment.status}\nProvider: {appointment.provider.business_name if appointment.provider else 'Us'}\nPlease let us know if you need to reschedule!"
    text = request.POST.get('custom_message', default_text)
    
    try:
        threading.Thread(target=send_whatsapp_message, args=(phone, text)).start()
        messages.success(request, "WhatsApp message is being sent automatically in the background without needing to press enter!")
    except Exception as e:
        messages.error(request, f"Failed to send WhatsApp: {str(e)}")
        
    Notification.objects.create(
        appointment=appointment,
        message=f"Automated notification sent for {appointment.service_type} ({appointment.status})",
        status='sent'
    )
    
    return redirect(request.META.get('HTTP_REFERER', 'provider_dashboard'))
