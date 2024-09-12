from django.conf import settings
from django.core.exceptions import ValidationError

def validate_passcode(value):
    if not value == settings.PATIENT_FORM_PASSCODE:
        raise ValidationError('Incorrect passcode.')
