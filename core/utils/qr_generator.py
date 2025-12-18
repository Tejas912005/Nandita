"""
QR Code generation utility for medical records and prescriptions
"""
import qrcode
from io import BytesIO
from django.core.files import File
from django.conf import settings


def generate_qr_code(instance, base_url='http://localhost:8000'):
    """
    Generate QR code for a medical record or prescription
    
    Args:
        instance: MedicalRecord or Prescription model instance
        base_url: Base URL for the QR code link
    """
    # Determine the type and create appropriate URL
    if hasattr(instance, 'record_id'):
        # MedicalRecord
        url = f"{base_url}/record/{instance.record_id}/"
        filename = f"qr_{instance.record_id}.png"
    elif hasattr(instance, 'prescription_id'):
        # Prescription
        url = f"{base_url}/prescription/{instance.prescription_id}/"
        filename = f"qr_{instance.prescription_id}.png"
    else:
        return None
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Save to model
    instance.qr_code.save(filename, File(buffer), save=True)
    
    return instance.qr_code.url


def generate_qr_for_data(data, size=10):
    """
    Generate QR code for arbitrary data
    
    Args:
        data: String data to encode
        size: Box size for the QR code
    
    Returns:
        BytesIO buffer containing the QR code image
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return buffer
