"""
URL patterns for core app
"""
from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication
    path('register/', views.register_patient, name='register'),
    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/doctor/', views.register_doctor, name='register_doctor'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Patient routes
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('patient/book-appointment/', views.book_appointment, name='book_appointment'),
    path('patient/appointments/', views.patient_appointments, name='patient_appointments'),
    path('patient/records/', views.patient_records, name='patient_records'),
    path('patient/prescriptions/', views.patient_prescriptions, name='patient_prescriptions'),
    path('patient/profile/', views.patient_profile, name='patient_profile'),
    path('patient/consultation/<int:appointment_id>/', views.consultation_room, name='consultation_room'),
    
    # Doctor routes
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    path('doctor/patients/', views.doctor_patients, name='doctor_patients'),
    path('doctor/profile/', views.doctor_profile, name='doctor_profile'),
    path('doctor/appointment/<int:appointment_id>/update/', views.update_appointment_status, name='update_appointment_status'),
    path('doctor/appointment/<int:appointment_id>/prescription/', views.create_prescription, name='create_prescription'),
    path('doctor/consultation/<int:appointment_id>/', views.doctor_consultation, name='doctor_consultation'),
    path('consultation/<int:appointment_id>/end/', views.end_consultation, name='end_consultation'),
    
    # Hospital & Location
    path('find-hospitals/', views.find_hospitals, name='find_hospitals'),
    path('hospital/<int:hospital_id>/', views.hospital_detail, name='hospital_detail'),
    path('bed-availability/', views.bed_availability, name='bed_availability'),
    path('mobile-clinics/', views.mobile_clinics, name='mobile_clinics'),
    
    # Chatbot API
    path('api/chatbot/', views.chatbot_response, name='chatbot_response'),
    
    # Other APIs
    path('api/send-message/', views.send_chat_message, name='send_chat_message'),
    path('api/messages/<int:consultation_id>/', views.get_chat_messages, name='get_chat_messages'),
    path('api/notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('api/doctors/', views.get_doctors_by_specialization, name='get_doctors'),
    
    # QR Code views
    path('record/<str:record_id>/', views.view_record_qr, name='view_record_qr'),
    path('prescription/<str:prescription_id>/', views.view_prescription_qr, name='view_prescription_qr'),
]
