"""
Database initialization script with sample data
Run: python init_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telemedicine.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import (
    PatientProfile, DoctorProfile, Hospital, Bed,
    Appointment, MobileClinic
)
from datetime import date, time, timedelta


def create_sample_data():
    """Create sample data for demonstration"""
    print("Creating sample data...")
    
    # Create Hospitals
    hospitals_data = [
        {
            'name': 'District General Hospital',
            'address': 'Main Road, District Center, State - 123001',
            'latitude': 28.6139,
            'longitude': 77.2090,
            'phone': '+91 1234567890',
            'email': 'dgh@example.com',
            'description': 'A multi-specialty government hospital serving the district.',
            'facilities': 'Emergency, ICU, Surgery, Pediatrics, Maternity, X-Ray, Blood Bank',
        },
        {
            'name': 'Community Health Center',
            'address': 'Village Road, Block HQ, State - 123002',
            'latitude': 28.6200,
            'longitude': 77.2150,
            'phone': '+91 9876543210',
            'email': 'chc@example.com',
            'description': 'Primary healthcare center for rural communities.',
            'facilities': 'OPD, Pharmacy, Lab, Vaccination',
        },
        {
            'name': 'Rural Medical Center',
            'address': 'Main Street, Town Area, State - 123003',
            'latitude': 28.6050,
            'longitude': 77.2000,
            'phone': '+91 9988776655',
            'email': 'rmc@example.com',
            'description': 'Modern medical facility with telemedicine support.',
            'facilities': 'Telemedicine, OPD, Pharmacy, Diagnostics',
        },
    ]
    
    hospitals = []
    for h_data in hospitals_data:
        hospital, created = Hospital.objects.get_or_create(
            name=h_data['name'],
            defaults=h_data
        )
        hospitals.append(hospital)
        if created:
            print(f"  Created hospital: {hospital.name}")
    
    # Create Beds for hospitals
    ward_types = ['general', 'icu', 'emergency', 'private', 'maternity']
    for hospital in hospitals:
        for ward in ward_types[:3]:  # First 3 ward types
            for i in range(1, 6):  # 5 beds per ward
                bed, created = Bed.objects.get_or_create(
                    hospital=hospital,
                    bed_number=f"{ward[0].upper()}{i:02d}",
                    defaults={
                        'ward_type': ward,
                        'is_available': i % 2 == 0,  # Alternate availability
                        'daily_rate': 500 if ward == 'general' else 2000,
                    }
                )
    print(f"  Created beds for {len(hospitals)} hospitals")
    
    # Create Admin User
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@telemed.com',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("  Created admin user (admin/admin123)")
    
    # Create Sample Doctors
    doctors_data = [
        {
            'username': 'dr_sharma',
            'email': 'sharma@telemed.com',
            'full_name': 'Rajesh Sharma',
            'specialization': 'general',
            'qualification': 'MBBS, MD (General Medicine)',
            'license_number': 'MED001234',
            'experience_years': 15,
            'consultation_fee': 300,
            'bio': 'Experienced general physician with 15 years of practice.',
            'is_verified': True,
        },
        {
            'username': 'dr_patel',
            'email': 'patel@telemed.com',
            'full_name': 'Priya Patel',
            'specialization': 'pediatrics',
            'qualification': 'MBBS, DCH (Pediatrics)',
            'license_number': 'MED005678',
            'experience_years': 10,
            'consultation_fee': 350,
            'bio': 'Specialized in child healthcare and vaccination.',
            'is_verified': True,
        },
        {
            'username': 'dr_khan',
            'email': 'khan@telemed.com',
            'full_name': 'Ahmed Khan',
            'specialization': 'cardiology',
            'qualification': 'MBBS, DM (Cardiology)',
            'license_number': 'MED009012',
            'experience_years': 12,
            'consultation_fee': 500,
            'bio': 'Expert cardiologist with focus on preventive care.',
            'is_verified': True,
        },
        {
            'username': 'dr_gupta',
            'email': 'gupta@telemed.com',
            'full_name': 'Sneha Gupta',
            'specialization': 'gynecology',
            'qualification': 'MBBS, MS (OB-GYN)',
            'license_number': 'MED003456',
            'experience_years': 8,
            'consultation_fee': 400,
            'bio': 'Womens health specialist with expertise in maternal care.',
            'is_verified': True,
        },
    ]
    
    for d_data in doctors_data:
        user, created = User.objects.get_or_create(
            username=d_data['username'],
            defaults={'email': d_data['email']}
        )
        if created:
            user.set_password('doctor123')
            user.save()
            
            DoctorProfile.objects.create(
                user=user,
                full_name=d_data['full_name'],
                specialization=d_data['specialization'],
                qualification=d_data['qualification'],
                license_number=d_data['license_number'],
                experience_years=d_data['experience_years'],
                consultation_fee=d_data['consultation_fee'],
                bio=d_data['bio'],
                phone='+91 9999900000',
                is_verified=d_data['is_verified'],
                hospital=hospitals[0],
            )
            print(f"  Created doctor: Dr. {d_data['full_name']}")
    
    # Create Sample Patients
    patients_data = [
        {
            'username': 'rahul_patient',
            'email': 'rahul@example.com',
            'full_name': 'Rahul Kumar',
            'phone': '+91 8888800001',
            'address': 'Village Rampur, Block A, District - 123001',
            'blood_group': 'O+',
        },
        {
            'username': 'meera_patient',
            'email': 'meera@example.com',
            'full_name': 'Meera Devi',
            'phone': '+91 8888800002',
            'address': 'Village Shyampur, Block B, District - 123002',
            'blood_group': 'B+',
        },
    ]
    
    for p_data in patients_data:
        user, created = User.objects.get_or_create(
            username=p_data['username'],
            defaults={'email': p_data['email']}
        )
        if created:
            user.set_password('patient123')
            user.save()
            
            PatientProfile.objects.create(
                user=user,
                full_name=p_data['full_name'],
                phone=p_data['phone'],
                address=p_data['address'],
                blood_group=p_data['blood_group'],
            )
            print(f"  Created patient: {p_data['full_name']}")
    
    # Create Mobile Clinics
    clinics_data = [
        {
            'name': 'Health on Wheels - Unit 1',
            'location': 'Village Rampur, Block A',
            'latitude': 28.6100,
            'longitude': 77.2050,
            'scheduled_date': date.today() + timedelta(days=3),
            'start_time': time(9, 0),
            'end_time': time(14, 0),
            'services': 'General Checkup, Blood Pressure, Diabetes Screening, Vaccination',
        },
        {
            'name': 'Health on Wheels - Unit 2',
            'location': 'Village Shyampur, Block B',
            'latitude': 28.6150,
            'longitude': 77.2100,
            'scheduled_date': date.today() + timedelta(days=5),
            'start_time': time(10, 0),
            'end_time': time(15, 0),
            'services': 'Eye Checkup, Dental Care, Child Health, Nutrition Counseling',
        },
        {
            'name': 'Women Health Camp',
            'location': 'Community Center, Block HQ',
            'latitude': 28.6080,
            'longitude': 77.2020,
            'scheduled_date': date.today() + timedelta(days=7),
            'start_time': time(9, 30),
            'end_time': time(16, 0),
            'services': 'Maternal Health, Gynecology Consultation, Family Planning',
        },
    ]
    
    for c_data in clinics_data:
        clinic, created = MobileClinic.objects.get_or_create(
            name=c_data['name'],
            scheduled_date=c_data['scheduled_date'],
            defaults=c_data
        )
        if created:
            print(f"  Created mobile clinic: {clinic.name}")
    
    print("\nSample data creation complete!")
    print("\n--- Login Credentials ---")
    print("Admin: admin / admin123")
    print("Doctors: dr_sharma, dr_patel, dr_khan, dr_gupta / doctor123")
    print("Patients: rahul_patient, meera_patient / patient123")


if __name__ == '__main__':
    create_sample_data()
