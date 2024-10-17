from django import forms
from django_recaptcha.fields import ReCaptchaField 
from django_recaptcha.widgets import ReCaptchaV2Checkbox 
from .validators import validate_passcode
from django.conf import settings


#https://docs.djangoproject.com/en/5.1/topics/http/file-uploads/#uploading-multiple-files
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class ClinicForm(forms.Form):
    EXPIRE_DOWNLOADS_CHOICES = [
        ('1','1 download'),
        ('2', '2 downloads'),
        ('3', '3 downloads'), 
        ('4', '4 downloads'),
        ('5', '5 downloads'),
        ('20', '20 downloads'),
        ('50', '50 downloads'),
        ('100', '100 downloads'),
    ]

    EXPIRE_TIME_CHOICES = [
        ('5m', '5 minutes'),
        ('1h', '1 hour'),
        ('1d', '1 day'),
        ('7d', '7 days'),
    ]
    name = forms.CharField(required=True)
    email = forms.CharField(required=True)
    multiple_upload = MultipleFileField()
    #upload = forms.FileField()
    expire_downloads = forms.ChoiceField(choices=EXPIRE_DOWNLOADS_CHOICES)
    expire_time = forms.ChoiceField(choices=EXPIRE_TIME_CHOICES)
    email_from = forms.ChoiceField(choices=settings.FROM_CHOICES)
    mail_subject = forms.CharField(required=False, initial=settings.DEFAULT_CLINIC_TO_PATIENT_SUBJECT)
    mail_body = forms.CharField(widget=forms.Textarea, required=False, initial=settings.DEFAULT_CLINIC_TO_PATIENT_BODY)

class PatientForm(forms.Form):
    SEND_OPTIONS = [
        ('admin','Admin'),
        ('reception','Reception'),
        ('consultation','Consultation'),
        ('doctor','Doctor'),
        ('lab','Laboratory'),
    ]
    name = forms.CharField(required=True)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    upload = forms.FileField()
    passcode = forms.CharField(required=True, validators=[validate_passcode])
    send_choices = forms.CharField(widget=forms.CheckboxSelectMultiple(choices=SEND_OPTIONS), required=True)
    
