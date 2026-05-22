import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_appointment_os.settings')
django.setup()

from appointment_app.models import User

def create_admin():
    username = 'admin'
    email = 'admin@example.com'
    password = 'adminpassword123'
    
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role='ADMIN'
        )
        print(f"Admin user created successfully!")
        print(f"Username: {username}")
        print(f"Password: {password}")
    else:
        print(f"User '{username}' already exists.")

if __name__ == '__main__':
    create_admin()
