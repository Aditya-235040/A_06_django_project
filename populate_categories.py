import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'whatsapp_appointment_os.settings')
django.setup()

from appointment_app.models import Category, ProviderProfile, Staff, SubCategory, User

DEMO_PASSWORD = "provider123"

categories = {
    'Salon': ['Haircut', 'Beard Style', 'Make Up', 'Hair Color'],
    'Technician': ['Electrician', 'Plumber', 'Carpenter', 'Fridge Repair'],
    'Doctor': ['Heart Specialist', 'Eye Specialist', 'Bone Specialist', 'Skin Doctor'],
    'Education': ['Math Teacher', 'Science Teacher', 'English Teacher', 'Computer Teacher'],
    'Transportation': ['Bike Taxi', 'Car Taxi', 'Bus Service', 'Truck Service'],
}

providers = [
    {
        "username": "salon_provider",
        "email": "salon.provider@example.com",
        "phone": "9876500001",
        "business_name": "Glow & Style Salon",
        "category": "Salon",
        "subcategory": "Haircut",
        "description": "Salon services for haircut, beard styling, makeup, and hair color.",
        "address": "Main Market, Patna",
        "upi_id": "salonprovider@upi",
        "booking_amount": "199.00",
        "staff_name": "Riya Sharma",
        "staff_position": "Senior Stylist",
    },
    {
        "username": "technician_provider",
        "email": "technician.provider@example.com",
        "phone": "9876500002",
        "business_name": "QuickFix Technicians",
        "category": "Technician",
        "subcategory": "Electrician",
        "description": "Home repair professionals for electrical, plumbing, carpentry, and appliance services.",
        "address": "Boring Road, Patna",
        "upi_id": "quickfix@upi",
        "booking_amount": "149.00",
        "staff_name": "Amit Kumar",
        "staff_position": "Lead Technician",
    },
    {
        "username": "doctor_provider",
        "email": "doctor.provider@example.com",
        "phone": "9876500003",
        "business_name": "City Care Clinic",
        "category": "Doctor",
        "subcategory": "Heart Specialist",
        "description": "Clinic appointments for specialist consultations and follow-ups.",
        "address": "Kankarbagh, Patna",
        "upi_id": "citycare@upi",
        "booking_amount": "499.00",
        "staff_name": "Dr. Neha Singh",
        "staff_position": "Consultant",
    },
    {
        "username": "education_provider",
        "email": "education.provider@example.com",
        "phone": "9876500004",
        "business_name": "BrightPath Tutors",
        "category": "Education",
        "subcategory": "Math Teacher",
        "description": "Subject tutors for school and computer education.",
        "address": "Bailey Road, Patna",
        "upi_id": "brightpath@upi",
        "booking_amount": "299.00",
        "staff_name": "Priya Verma",
        "staff_position": "Math Teacher",
    },
    {
        "username": "transport_provider",
        "email": "transport.provider@example.com",
        "phone": "9876500005",
        "business_name": "EasyMove Transport",
        "category": "Transportation",
        "subcategory": "Car Taxi",
        "description": "Transport booking for bike taxi, car taxi, bus service, and truck service.",
        "address": "Station Road, Patna",
        "upi_id": "easymove@upi",
        "booking_amount": "99.00",
        "staff_name": "Rohit Raj",
        "staff_position": "Driver",
    },
]

print("Populating categories and subcategories...")

for cat_name, subcats in categories.items():
    category, created = Category.objects.get_or_create(name=cat_name)
    if created:
        print(f"Created category: {cat_name}")

    for sub_name in subcats:
        sub, sub_created = SubCategory.objects.get_or_create(category=category, name=sub_name)
        if sub_created:
            print(f"  Created subcategory: {sub_name}")

print("Populating provider demo data...")

for item in providers:
    category = Category.objects.get(name=item["category"])
    subcategory = SubCategory.objects.get(category=category, name=item["subcategory"])

    user, user_created = User.objects.get_or_create(
        username=item["username"],
        defaults={
            "email": item["email"],
            "role": "PROVIDER",
            "phone": item["phone"],
        },
    )
    user.email = item["email"]
    user.role = "PROVIDER"
    user.phone = item["phone"]
    user.set_password(DEMO_PASSWORD)
    user.save()

    if user_created:
        print(f"Created provider user: {item['username']}")

    profile, profile_created = ProviderProfile.objects.update_or_create(
        user=user,
        defaults={
            "business_name": item["business_name"],
            "category": category,
            "subcategory": subcategory,
            "description": item["description"],
            "address": item["address"],
            "upi_id": item["upi_id"],
            "booking_amount": item["booking_amount"],
        },
    )

    if profile_created:
        print(f"Created provider profile: {item['business_name']}")
    else:
        print(f"Updated provider profile: {item['business_name']}")

    staff, staff_created = Staff.objects.update_or_create(
        email=item["email"],
        defaults={
            "provider": profile,
            "name": item["staff_name"],
            "phone": item["phone"],
            "position": item["staff_position"],
            "is_active": True,
        },
    )

    if staff_created:
        print(f"  Created staff member: {staff.name}")
    else:
        print(f"  Updated staff member: {staff.name}")

print("Done populating categories and providers.")
print(f"Demo provider password: {DEMO_PASSWORD}")
