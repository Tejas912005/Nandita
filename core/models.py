"""
Models for Telemedicine Platform
Includes: User Profiles, Appointments, Medical Records, Hospitals, Beds
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class PatientProfile(models.Model):
    """Extended profile for patients"""
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    full_name = models.CharField(max_length=200)
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    profile_image = models.ImageField(upload_to='patients/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.full_name
    
    class Meta:
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'


class Hospital(models.Model):
    """Hospital/Clinic information"""
    name = models.CharField(max_length=300)
    address = models.TextField()
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    description = models.TextField(blank=True)
    facilities = models.TextField(blank=True, help_text="Comma separated list of facilities")
    image = models.ImageField(upload_to='hospitals/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def available_beds_count(self):
        return self.beds.filter(is_available=True).count()
    
    @property
    def total_beds_count(self):
        return self.beds.count()


class DoctorProfile(models.Model):
    """Extended profile for doctors"""
    SPECIALIZATIONS = [
        ('general', 'General Physician'),
        ('cardiology', 'Cardiology'),
        ('dermatology', 'Dermatology'),
        ('neurology', 'Neurology'),
        ('orthopedics', 'Orthopedics'),
        ('pediatrics', 'Pediatrics'),
        ('psychiatry', 'Psychiatry'),
        ('gynecology', 'Gynecology'),
        ('ophthalmology', 'Ophthalmology'),
        ('ent', 'ENT Specialist'),
        ('dentistry', 'Dentistry'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    full_name = models.CharField(max_length=200)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATIONS)
    qualification = models.CharField(max_length=200)
    license_number = models.CharField(max_length=50, unique=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True, related_name='doctors')
    experience_years = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    phone = models.CharField(max_length=15)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='doctors/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dr. {self.full_name} - {self.get_specialization_display()}"
    
    class Meta:
        verbose_name = 'Doctor Profile'
        verbose_name_plural = 'Doctor Profiles'


class Bed(models.Model):
    """Hospital bed tracking"""
    WARD_TYPES = [
        ('general', 'General Ward'),
        ('icu', 'ICU'),
        ('emergency', 'Emergency'),
        ('private', 'Private Room'),
        ('semi_private', 'Semi-Private'),
        ('pediatric', 'Pediatric Ward'),
        ('maternity', 'Maternity Ward'),
    ]
    
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='beds')
    bed_number = models.CharField(max_length=20)
    ward_type = models.CharField(max_length=20, choices=WARD_TYPES)
    is_available = models.BooleanField(default=True)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        status = "Available" if self.is_available else "Occupied"
        return f"{self.hospital.name} - Bed {self.bed_number} ({status})"
    
    class Meta:
        unique_together = ['hospital', 'bed_number']


class Appointment(models.Model):
    """Appointment management"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    TYPE_CHOICES = [
        ('video', 'Video Consultation'),
        ('chat', 'Chat Consultation'),
        ('in_person', 'In-Person Visit'),
        ('mobile_clinic', 'Mobile Clinic'),
    ]
    
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    appointment_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='video')
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    symptoms = models.TextField(blank=True, help_text="Describe your symptoms")
    notes = models.TextField(blank=True)
    booking_id = models.CharField(max_length=20, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = f"APT{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.booking_id} - {self.patient.full_name} with Dr. {self.doctor.full_name}"
    
    class Meta:
        ordering = ['-scheduled_date', '-scheduled_time']


class Consultation(models.Model):
    """Consultation details for each appointment"""
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='consultation')
    diagnosis = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    consultation_notes = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Consultation for {self.appointment.booking_id}"


class MedicalRecord(models.Model):
    """Patient medical records with QR code support"""
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.SET_NULL, null=True, related_name='medical_records')
    record_id = models.CharField(max_length=20, unique=True, editable=False)
    diagnosis = models.CharField(max_length=500)
    treatment = models.TextField()
    visit_date = models.DateField()
    attachments = models.FileField(upload_to='records/', null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.record_id:
            self.record_id = f"MR{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.record_id} - {self.patient.full_name}"
    
    class Meta:
        ordering = ['-visit_date']


class Prescription(models.Model):
    """Digital prescriptions"""
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.SET_NULL, null=True, related_name='prescriptions')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescriptions')
    prescription_id = models.CharField(max_length=20, unique=True, editable=False)
    medications = models.TextField(help_text="List of medications with dosage")
    instructions = models.TextField(help_text="Special instructions for the patient")
    issue_date = models.DateField(auto_now_add=True)
    valid_until = models.DateField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='prescription_qr/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.prescription_id:
            self.prescription_id = f"RX{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.prescription_id} - {self.patient.full_name}"
    
    class Meta:
        ordering = ['-issue_date']


class ChatMessage(models.Model):
    """Messages for consultations"""
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_from_doctor = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.timestamp}"
    
    class Meta:
        ordering = ['timestamp']


class Notification(models.Model):
    """Notification system"""
    NOTIFICATION_TYPES = [
        ('appointment', 'Appointment'),
        ('reminder', 'Reminder'),
        ('prescription', 'Prescription'),
        ('general', 'General'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']


class MobileClinic(models.Model):
    """Mobile clinic scheduling"""
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=500)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    scheduled_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    services = models.TextField(help_text="Available services")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.location} on {self.scheduled_date}"
    
    class Meta:
        ordering = ['scheduled_date', 'start_time']
