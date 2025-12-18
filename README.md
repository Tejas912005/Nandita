# TeleMed - Telemedicine Access for Rural Healthcare

A comprehensive telemedicine platform designed to provide easy access to healthcare for rural patients through online consultations, AI chatbot assistance, digital records, and hospital-patient communication.

## Features

- **Video/Chat Consultations** - Connect with doctors online
- **AI Chatbot (C_Bot)** - 24/7 health assistance
- **Appointment Booking** - Easy scheduling system
- **Digital Medical Records** - With QR code sharing
- **E-Prescriptions** - Digital prescriptions with QR codes
- **Hospital Finder** - Google Maps integration ready
- **Bed Availability Tracker** - Real-time bed status
- **Mobile Clinic Scheduling** - Healthcare that comes to you

## Tech Stack

- **Backend**: Django 4.2+ (Python)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Icons**: Font Awesome
- **Fonts**: Inter, Outfit (Google Fonts)

## Setup Instructions

### 1. Install Python

Download and install Python 3.10+ from [python.org](https://www.python.org/downloads/)

During installation, **check "Add Python to PATH"**

### 2. Install Dependencies

Open Command Prompt/Terminal in the project directory:

```bash
cd c:\xampp\htdocs\Nandita
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
python manage.py makemigrations core
python manage.py migrate
```

### 4. Create Sample Data (Optional)

```bash
python init_data.py
```

This creates sample hospitals, doctors, patients, and mobile clinics.

### 5. Create Admin User (if not using init_data.py)

```bash
python manage.py createsuperuser
```

### 6. Run the Server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

## Login Credentials (after running init_data.py)

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Doctor | dr_sharma | doctor123 |
| Doctor | dr_patel | doctor123 |
| Patient | rahul_patient | patient123 |
| Patient | meera_patient | patient123 |

## Project Structure

```
Nandita/
├── manage.py               # Django entry point
├── requirements.txt        # Python dependencies
├── init_data.py           # Sample data script
├── telemedicine/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                  # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── forms.py           # Form definitions
│   ├── urls.py            # URL patterns
│   ├── admin.py           # Admin configuration
│   └── utils/
│       └── qr_generator.py  # QR code utility
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── auth/
│   ├── patient/
│   ├── doctor/
│   └── ...
└── static/                # Static assets
    ├── css/styles.css
    └── js/
        ├── main.js
        └── chatbot.js
```

## Configuration

### Google Maps API (Optional)

To enable the hospital map feature:

1. Get an API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Add to `telemedicine/settings.py`:
   ```python
   GOOGLE_MAPS_API_KEY = 'your-api-key-here'
   ```

### Email Configuration (Optional)

For email notifications, update `telemedicine/settings.py`:

```python
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

## Admin Panel

Access the Django admin at: http://127.0.0.1:8000/admin/

Manage:
- Users & Profiles
- Hospitals & Beds
- Appointments
- Medical Records
- Prescriptions
- Mobile Clinics

## License

This project is for educational purposes.

## Support

For issues or questions, contact: support@telemed.com
