"""
Forms for Telemedicine Platform
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    PatientProfile, DoctorProfile, Appointment, 
    MedicalRecord, Prescription, Hospital
)


class PatientRegistrationForm(UserCreationForm):
    """Registration form for patients"""
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=200)
    phone = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    blood_group = forms.ChoiceField(
        choices=[('', 'Select Blood Group')] + list(PatientProfile.BLOOD_GROUPS),
        required=False
    )
    emergency_contact = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'


class DoctorRegistrationForm(UserCreationForm):
    """Registration form for doctors"""
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=200)
    phone = forms.CharField(max_length=15)
    specialization = forms.ChoiceField(choices=DoctorProfile.SPECIALIZATIONS)
    qualification = forms.CharField(max_length=200)
    license_number = forms.CharField(max_length=50)
    experience_years = forms.IntegerField(min_value=0)
    consultation_fee = forms.DecimalField(max_digits=10, decimal_places=2)
    hospital = forms.ModelChoiceField(
        queryset=Hospital.objects.filter(is_active=True),
        required=False
    )
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'


class LoginForm(forms.Form):
    """Login form"""
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'


class AppointmentForm(forms.ModelForm):
    """Appointment booking form"""
    scheduled_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
    )
    scheduled_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'})
    )
    
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_type', 'scheduled_date', 'scheduled_time', 'symptoms']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-input'}),
            'appointment_type': forms.Select(attrs={'class': 'form-input'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = DoctorProfile.objects.filter(
            is_verified=True, is_available=True
        )


class PrescriptionForm(forms.ModelForm):
    """Prescription form for doctors"""
    valid_until = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        required=False
    )
    
    class Meta:
        model = Prescription
        fields = ['medications', 'instructions', 'valid_until']
        widgets = {
            'medications': forms.Textarea(attrs={'class': 'form-input', 'rows': 5}),
            'instructions': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
        }


class MedicalRecordForm(forms.ModelForm):
    """Medical record form"""
    visit_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
    )
    
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'treatment', 'visit_date', 'attachments']
        widgets = {
            'diagnosis': forms.TextInput(attrs={'class': 'form-input'}),
            'treatment': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
        }


class ProfileUpdateForm(forms.ModelForm):
    """Patient profile update form"""
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        required=False
    )
    
    class Meta:
        model = PatientProfile
        fields = ['full_name', 'date_of_birth', 'phone', 'address', 'blood_group', 'emergency_contact', 'profile_image']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'blood_group': forms.Select(attrs={'class': 'form-input'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-input'}),
        }


class DoctorProfileUpdateForm(forms.ModelForm):
    """Doctor profile update form"""
    class Meta:
        model = DoctorProfile
        fields = ['full_name', 'phone', 'specialization', 'qualification', 'experience_years', 'consultation_fee', 'bio', 'profile_image', 'is_available']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'specialization': forms.Select(attrs={'class': 'form-input'}),
            'qualification': forms.TextInput(attrs={'class': 'form-input'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-input'}),
            'consultation_fee': forms.NumberInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
        }


class ContactForm(forms.Form):
    """Contact form for inquiries"""
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'
