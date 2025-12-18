"""
Views for Telemedicine Platform
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
import json

from .models import (
    PatientProfile, DoctorProfile, Hospital, Bed,
    Appointment, Consultation, MedicalRecord, Prescription,
    Notification, MobileClinic, ChatMessage
)
from .forms import (
    PatientRegistrationForm, DoctorRegistrationForm, LoginForm,
    AppointmentForm, PrescriptionForm, MedicalRecordForm,
    ProfileUpdateForm, DoctorProfileUpdateForm, ContactForm
)
from .utils.qr_generator import generate_qr_code


# ==================== PUBLIC VIEWS ====================

def home(request):
    """Landing page"""
    doctors = DoctorProfile.objects.filter(is_verified=True, is_available=True)[:6]
    hospitals = Hospital.objects.filter(is_active=True)[:6]
    
    stats = {
        'doctors': DoctorProfile.objects.filter(is_verified=True).count(),
        'patients': PatientProfile.objects.count(),
        'hospitals': Hospital.objects.filter(is_active=True).count(),
        'appointments': Appointment.objects.filter(status='completed').count(),
    }
    
    context = {
        'doctors': doctors,
        'hospitals': hospitals,
        'stats': stats,
    }
    return render(request, 'index.html', context)


def about(request):
    """About page"""
    return render(request, 'about.html')


def services(request):
    """Services page"""
    return render(request, 'services.html')


def contact(request):
    """Contact page"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Your message has been sent. We will get back to you soon!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


# ==================== AUTHENTICATION ====================

def register_patient(request):
    """Patient registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()
            
            # Create patient profile
            PatientProfile.objects.create(
                user=user,
                full_name=form.cleaned_data['full_name'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                date_of_birth=form.cleaned_data.get('date_of_birth'),
                blood_group=form.cleaned_data.get('blood_group', ''),
                emergency_contact=form.cleaned_data.get('emergency_contact', ''),
            )
            
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to TeleMed.')
            return redirect('patient_dashboard')
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'auth/register_patient.html', {'form': form})


def register_doctor(request):
    """Doctor registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()
            
            # Create doctor profile
            DoctorProfile.objects.create(
                user=user,
                full_name=form.cleaned_data['full_name'],
                phone=form.cleaned_data['phone'],
                specialization=form.cleaned_data['specialization'],
                qualification=form.cleaned_data['qualification'],
                license_number=form.cleaned_data['license_number'],
                experience_years=form.cleaned_data['experience_years'],
                consultation_fee=form.cleaned_data['consultation_fee'],
                hospital=form.cleaned_data.get('hospital'),
                bio=form.cleaned_data.get('bio', ''),
                is_verified=False,
            )
            
            login(request, user)
            messages.info(request, 'Registration successful! Your profile is pending verification.')
            return redirect('doctor_dashboard')
    else:
        form = DoctorRegistrationForm()
    
    return render(request, 'auth/register_doctor.html', {'form': form})


def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')


def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard(request):
    """Redirect to appropriate dashboard based on user type"""
    if hasattr(request.user, 'doctor_profile'):
        return redirect('doctor_dashboard')
    elif hasattr(request.user, 'patient_profile'):
        return redirect('patient_dashboard')
    else:
        return redirect('home')


# ==================== PATIENT VIEWS ====================

@login_required
def patient_dashboard(request):
    """Patient dashboard"""
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, 'Access denied. Patient account required.')
        return redirect('home')
    
    patient = request.user.patient_profile
    upcoming_appointments = Appointment.objects.filter(
        patient=patient,
        scheduled_date__gte=timezone.now().date(),
        status__in=['pending', 'confirmed']
    ).order_by('scheduled_date', 'scheduled_time')[:5]
    
    recent_records = MedicalRecord.objects.filter(patient=patient)[:5]
    recent_prescriptions = Prescription.objects.filter(patient=patient)[:5]
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    
    context = {
        'patient': patient,
        'upcoming_appointments': upcoming_appointments,
        'recent_records': recent_records,
        'recent_prescriptions': recent_prescriptions,
        'notifications': notifications,
    }
    return render(request, 'patient/dashboard.html', context)


@login_required
def book_appointment(request):
    """Book new appointment"""
    if not hasattr(request.user, 'patient_profile'):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user.patient_profile
            appointment.save()
            
            # Create notification for doctor
            Notification.objects.create(
                user=appointment.doctor.user,
                notification_type='appointment',
                title='New Appointment Request',
                message=f'{appointment.patient.full_name} has requested an appointment.',
                link=f'/doctor/appointments/{appointment.id}/'
            )
            
            messages.success(request, f'Appointment booked successfully! Booking ID: {appointment.booking_id}')
            return redirect('patient_appointments')
    else:
        form = AppointmentForm()
    
    doctors = DoctorProfile.objects.filter(is_verified=True, is_available=True)
    context = {'form': form, 'doctors': doctors}
    return render(request, 'patient/book_appointment.html', context)


@login_required
def patient_appointments(request):
    """View patient appointments"""
    if not hasattr(request.user, 'patient_profile'):
        return redirect('home')
    
    appointments = Appointment.objects.filter(patient=request.user.patient_profile)
    paginator = Paginator(appointments, 10)
    page = request.GET.get('page')
    appointments = paginator.get_page(page)
    
    return render(request, 'patient/appointments.html', {'appointments': appointments})


@login_required
def patient_records(request):
    """View medical records"""
    if not hasattr(request.user, 'patient_profile'):
        return redirect('home')
    
    records = MedicalRecord.objects.filter(patient=request.user.patient_profile)
    return render(request, 'patient/records.html', {'records': records})


@login_required
def patient_prescriptions(request):
    """View prescriptions"""
    if not hasattr(request.user, 'patient_profile'):
        return redirect('home')
    
    prescriptions = Prescription.objects.filter(patient=request.user.patient_profile)
    return render(request, 'patient/prescriptions.html', {'prescriptions': prescriptions})


@login_required
def patient_profile(request):
    """Update patient profile"""
    if not hasattr(request.user, 'patient_profile'):
        return redirect('home')
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.patient_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('patient_profile')
    else:
        form = ProfileUpdateForm(instance=request.user.patient_profile)
    
    return render(request, 'patient/profile.html', {'form': form})


@login_required
def consultation_room(request, appointment_id):
    """Consultation room for patient"""
    if not hasattr(request.user, 'patient_profile'):
        return redirect('home')
    
    appointment = get_object_or_404(
        Appointment, id=appointment_id, patient=request.user.patient_profile
    )
    
    consultation, created = Consultation.objects.get_or_create(appointment=appointment)
    chat_messages = ChatMessage.objects.filter(consultation=consultation)
    
    context = {
        'appointment': appointment,
        'consultation': consultation,
        'chat_messages': chat_messages,
    }
    return render(request, 'patient/consultation.html', context)


# ==================== DOCTOR VIEWS ====================

@login_required
def doctor_dashboard(request):
    """Doctor dashboard"""
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Access denied. Doctor account required.')
        return redirect('home')
    
    doctor = request.user.doctor_profile
    today = timezone.now().date()
    
    todays_appointments = Appointment.objects.filter(
        doctor=doctor,
        scheduled_date=today,
        status__in=['pending', 'confirmed', 'in_progress']
    ).order_by('scheduled_time')
    
    pending_appointments = Appointment.objects.filter(
        doctor=doctor, status='pending'
    ).count()
    
    total_patients = Appointment.objects.filter(
        doctor=doctor, status='completed'
    ).values('patient').distinct().count()
    
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    
    context = {
        'doctor': doctor,
        'todays_appointments': todays_appointments,
        'pending_appointments': pending_appointments,
        'total_patients': total_patients,
        'notifications': notifications,
    }
    return render(request, 'doctor/dashboard.html', context)


@login_required
def doctor_appointments(request):
    """View doctor appointments"""
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('home')
    
    status_filter = request.GET.get('status', '')
    appointments = Appointment.objects.filter(doctor=request.user.doctor_profile)
    
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    paginator = Paginator(appointments, 10)
    page = request.GET.get('page')
    appointments = paginator.get_page(page)
    
    return render(request, 'doctor/appointments.html', {'appointments': appointments})


@login_required
def doctor_patients(request):
    """View doctor's patients"""
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('home')
    
    patient_ids = Appointment.objects.filter(
        doctor=request.user.doctor_profile
    ).values_list('patient_id', flat=True).distinct()
    
    patients = PatientProfile.objects.filter(id__in=patient_ids)
    return render(request, 'doctor/patients.html', {'patients': patients})


@login_required
def doctor_profile(request):
    """Update doctor profile"""
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('home')
    
    if request.method == 'POST':
        form = DoctorProfileUpdateForm(request.POST, request.FILES, instance=request.user.doctor_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('doctor_profile')
    else:
        form = DoctorProfileUpdateForm(instance=request.user.doctor_profile)
    
    return render(request, 'doctor/profile.html', {'form': form})


@login_required
def update_appointment_status(request, appointment_id):
    """Update appointment status (doctor only)"""
    if not hasattr(request.user, 'doctor_profile'):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    appointment = get_object_or_404(
        Appointment, id=appointment_id, doctor=request.user.doctor_profile
    )
    
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['confirmed', 'in_progress', 'completed', 'cancelled']:
            appointment.status = status
            appointment.save()
            
            # Notify patient
            Notification.objects.create(
                user=appointment.patient.user,
                notification_type='appointment',
                title='Appointment Update',
                message=f'Your appointment ({appointment.booking_id}) has been {status}.',
                link=f'/patient/appointments/'
            )
            
            messages.success(request, f'Appointment {status} successfully!')
    
    return redirect('doctor_appointments')


@login_required
def create_prescription(request, appointment_id):
    """Create prescription for an appointment"""
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('home')
    
    appointment = get_object_or_404(
        Appointment, id=appointment_id, doctor=request.user.doctor_profile
    )
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.doctor = request.user.doctor_profile
            prescription.patient = appointment.patient
            prescription.appointment = appointment
            prescription.save()
            
            # Generate QR code
            generate_qr_code(prescription)
            
            messages.success(request, 'Prescription created successfully!')
            return redirect('doctor_appointments')
    else:
        form = PrescriptionForm()
    
    context = {'form': form, 'appointment': appointment}
    return render(request, 'doctor/create_prescription.html', context)


@login_required
def doctor_consultation(request, appointment_id):
    """Doctor consultation room"""
    if not hasattr(request.user, 'doctor_profile'):
        return redirect('home')
    
    appointment = get_object_or_404(
        Appointment, id=appointment_id, doctor=request.user.doctor_profile
    )
    
    consultation, created = Consultation.objects.get_or_create(appointment=appointment)
    if created:
        consultation.started_at = timezone.now()
        consultation.save()
        appointment.status = 'in_progress'
        appointment.save()
    
    chat_messages = ChatMessage.objects.filter(consultation=consultation)
    
    context = {
        'appointment': appointment,
        'consultation': consultation,
        'chat_messages': chat_messages,
    }
    return render(request, 'doctor/consultation.html', context)


@login_required
def end_consultation(request, appointment_id):
    """End consultation and mark as completed"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Verify user is either the doctor or patient
    is_doctor = hasattr(request.user, 'doctor_profile') and appointment.doctor == request.user.doctor_profile
    is_patient = hasattr(request.user, 'patient_profile') and appointment.patient == request.user.patient_profile
    
    if not (is_doctor or is_patient):
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Mark appointment as completed
    appointment.status = 'completed'
    appointment.save()
    
    # Update consultation end time
    try:
        consultation = appointment.consultation
        consultation.ended_at = timezone.now()
        consultation.save()
    except:
        pass
    
    messages.success(request, 'Consultation ended successfully.')
    
    if is_doctor:
        return redirect('doctor_appointments')
    else:
        return redirect('patient_appointments')


# ==================== HOSPITAL & LOCATION VIEWS ====================

def find_hospitals(request):
    """Find nearby hospitals with map"""
    hospitals = Hospital.objects.filter(is_active=True)
    
    hospitals_data = [{
        'id': h.id,
        'name': h.name,
        'address': h.address,
        'lat': h.latitude,
        'lng': h.longitude,
        'phone': h.phone,
        'available_beds': h.available_beds_count,
        'total_beds': h.total_beds_count,
    } for h in hospitals]
    
    context = {
        'hospitals': hospitals,
        'hospitals_json': json.dumps(hospitals_data),
    }
    return render(request, 'find_hospitals.html', context)


def hospital_detail(request, hospital_id):
    """Hospital detail page"""
    hospital = get_object_or_404(Hospital, id=hospital_id)
    beds = hospital.beds.all()
    doctors = hospital.doctors.filter(is_verified=True)
    
    context = {
        'hospital': hospital,
        'beds': beds,
        'doctors': doctors,
    }
    return render(request, 'hospital_detail.html', context)


def bed_availability(request):
    """View bed availability across hospitals"""
    hospitals = Hospital.objects.filter(is_active=True).prefetch_related('beds')
    
    ward_filter = request.GET.get('ward', '')
    if ward_filter:
        hospitals = hospitals.filter(beds__ward_type=ward_filter, beds__is_available=True).distinct()
    
    context = {
        'hospitals': hospitals,
        'ward_types': Bed.WARD_TYPES,
        'selected_ward': ward_filter,
    }
    return render(request, 'bed_availability.html', context)


def mobile_clinics(request):
    """View mobile clinic schedules"""
    clinics = MobileClinic.objects.filter(
        scheduled_date__gte=timezone.now().date(),
        is_active=True
    )
    
    clinics_data = [{
        'id': c.id,
        'name': c.name,
        'location': c.location,
        'lat': c.latitude,
        'lng': c.longitude,
        'date': str(c.scheduled_date),
        'start_time': str(c.start_time),
        'end_time': str(c.end_time),
        'services': c.services,
    } for c in clinics]
    
    context = {
        'clinics': clinics,
        'clinics_json': json.dumps(clinics_data),
    }
    return render(request, 'mobile_clinics.html', context)


# ==================== CHATBOT API ====================

@require_POST
def chatbot_response(request):
    """Handle chatbot messages"""
    data = json.loads(request.body)
    message = data.get('message', '').lower()
    
    # Simple rule-based responses
    responses = {
        'symptoms': get_symptom_response(message),
        'appointment': "To book an appointment, please visit our 'Book Appointment' page or log in to your account. Would you like me to guide you there?",
        'emergency': "🚨 For emergencies, please call 108 (Ambulance) or 112 (Emergency). You can also use our 'Find Hospitals' feature to locate the nearest hospital.",
        'doctor': "We have qualified doctors across various specializations. You can browse our doctors on the 'Find Doctors' page and book a consultation.",
        'bed': "You can check real-time bed availability on our 'Bed Availability' page. Would you like me to help you find a bed?",
        'mobile clinic': "Mobile clinics bring healthcare to your village. Check the schedule on our 'Mobile Clinics' page to find one near you.",
        'prescription': "Your prescriptions are available in your patient dashboard. Each prescription has a QR code for easy sharing with pharmacies.",
        'record': "Your medical records are securely stored in your dashboard. You can view, download, or share them via QR code.",
    }
    
    response = "Hello! I'm C_Bot, your healthcare assistant. How can I help you today? You can ask me about appointments, symptoms, finding hospitals, bed availability, or mobile clinics."
    
    for key, value in responses.items():
        if key in message:
            response = value
            break
    
    return JsonResponse({'response': response})


def get_symptom_response(message):
    """Get response based on symptoms mentioned"""
    symptom_advice = {
        'fever': "For fever, rest well, stay hydrated, and monitor your temperature. If it persists beyond 3 days or exceeds 103°F, please consult a doctor.",
        'headache': "For headaches, try resting in a quiet, dark room. Stay hydrated and avoid screens. If headaches are severe or frequent, please book a consultation.",
        'cold': "For cold symptoms, get plenty of rest, drink warm fluids, and try steam inhalation. If symptoms worsen, consider booking an appointment.",
        'cough': "For cough, try warm water with honey, stay hydrated, and avoid irritants. If cough persists beyond 2 weeks or you have difficulty breathing, seek medical attention.",
        'stomach': "For stomach issues, stay hydrated, eat light foods, and avoid spicy or oily meals. If symptoms persist, please consult a doctor.",
    }
    
    for symptom, advice in symptom_advice.items():
        if symptom in message:
            return advice
    
    return "I understand you're experiencing some symptoms. For accurate diagnosis, I recommend booking a consultation with one of our doctors. Shall I help you book an appointment?"


# ==================== API ENDPOINTS ====================

@login_required
def send_chat_message(request):
    """Send chat message in consultation"""
    if request.method == 'POST':
        data = json.loads(request.body)
        consultation_id = data.get('consultation_id')
        message_text = data.get('message')
        
        consultation = get_object_or_404(Consultation, id=consultation_id)
        
        is_doctor = hasattr(request.user, 'doctor_profile')
        
        message = ChatMessage.objects.create(
            consultation=consultation,
            sender=request.user,
            message=message_text,
            is_from_doctor=is_doctor
        )
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'text': message.message,
                'is_from_doctor': message.is_from_doctor,
                'timestamp': message.timestamp.strftime('%H:%M'),
            }
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def get_chat_messages(request, consultation_id):
    """Get chat messages for consultation"""
    consultation = get_object_or_404(Consultation, id=consultation_id)
    messages_list = ChatMessage.objects.filter(consultation=consultation)
    
    data = [{
        'id': m.id,
        'text': m.message,
        'is_from_doctor': m.is_from_doctor,
        'timestamp': m.timestamp.strftime('%H:%M'),
    } for m in messages_list]
    
    return JsonResponse({'messages': data})


@login_required
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})


def get_doctors_by_specialization(request):
    """API to get doctors by specialization"""
    specialization = request.GET.get('specialization', '')
    
    doctors = DoctorProfile.objects.filter(
        is_verified=True, is_available=True
    )
    
    if specialization:
        doctors = doctors.filter(specialization=specialization)
    
    data = [{
        'id': d.id,
        'name': d.full_name,
        'specialization': d.get_specialization_display(),
        'hospital': d.hospital.name if d.hospital else 'Independent',
        'fee': str(d.consultation_fee),
        'experience': d.experience_years,
    } for d in doctors]
    
    return JsonResponse({'doctors': data})


def view_record_qr(request, record_id):
    """View medical record via QR code"""
    record = get_object_or_404(MedicalRecord, record_id=record_id)
    return render(request, 'view_record.html', {'record': record})


def view_prescription_qr(request, prescription_id):
    """View prescription via QR code"""
    prescription = get_object_or_404(Prescription, prescription_id=prescription_id)
    return render(request, 'view_prescription.html', {'prescription': prescription})
