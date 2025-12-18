"""
Django Admin configuration for Telemedicine Platform
"""
from django.contrib import admin
from .models import (
    PatientProfile, DoctorProfile, Hospital, Bed,
    Appointment, Consultation, MedicalRecord, Prescription,
    ChatMessage, Notification, MobileClinic
)

# Customize Admin Site Branding
admin.site.site_header = "TeleMed Administration"
admin.site.site_title = "TeleMed Admin Portal"
admin.site.index_title = "Welcome to TeleMed Admin Panel"

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'blood_group', 'created_at']
    search_fields = ['full_name', 'phone', 'user__email']
    list_filter = ['blood_group', 'created_at']


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'specialization', 'hospital', 'is_verified', 'is_available']
    search_fields = ['full_name', 'license_number', 'user__email']
    list_filter = ['specialization', 'is_verified', 'is_available', 'hospital']
    list_editable = ['is_verified', 'is_available']


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'is_active', 'available_beds_count', 'total_beds_count']
    search_fields = ['name', 'address', 'email']
    list_filter = ['is_active']


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ['hospital', 'bed_number', 'ward_type', 'is_available', 'daily_rate']
    search_fields = ['hospital__name', 'bed_number']
    list_filter = ['hospital', 'ward_type', 'is_available']
    list_editable = ['is_available']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'patient', 'doctor', 'appointment_type', 'scheduled_date', 'status']
    search_fields = ['booking_id', 'patient__full_name', 'doctor__full_name']
    list_filter = ['status', 'appointment_type', 'scheduled_date']
    date_hierarchy = 'scheduled_date'


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'diagnosis', 'follow_up_date']
    search_fields = ['appointment__booking_id', 'diagnosis']


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['record_id', 'patient', 'doctor', 'diagnosis', 'visit_date']
    search_fields = ['record_id', 'patient__full_name', 'diagnosis']
    list_filter = ['visit_date']
    date_hierarchy = 'visit_date'


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['prescription_id', 'patient', 'doctor', 'issue_date', 'valid_until']
    search_fields = ['prescription_id', 'patient__full_name', 'doctor__full_name']
    list_filter = ['issue_date']
    date_hierarchy = 'issue_date'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'is_from_doctor', 'timestamp', 'is_read']
    list_filter = ['is_from_doctor', 'is_read', 'timestamp']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['title', 'message', 'user__username']


@admin.register(MobileClinic)
class MobileClinicAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'scheduled_date', 'start_time', 'end_time', 'is_active']
    search_fields = ['name', 'location']
    list_filter = ['is_active', 'scheduled_date']
    date_hierarchy = 'scheduled_date'
