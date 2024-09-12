from django.conf import settings
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required

from .forms import ClinicForm, PatientForm
from .utils import handle_uploaded_file, handle_form_submission, send_share_link, get_clinic_to_emails

def index(request):
    #context = {}
    #context['user'] = request.user
    #return TemplateResponse(request, "clinic/index.html", context)
    if request.user.is_authenticated:
        return redirect('/clinic-send-file/')
    return redirect('/accounts/login/')

@login_required
def clinic_send_file(request):
    context = {}
    form = ClinicForm(request.POST or None, request.FILES or None)
    if request.POST:
        if form.is_valid():
            file_path = handle_uploaded_file(request.FILES["upload"])
            share_link = handle_form_submission(str(form.cleaned_data['expire_downloads']), str(form.cleaned_data['expire_time']), file_path)
            send_share_link(form.cleaned_data['name'], form.cleaned_data['email'], share_link, form.cleaned_data['mail_subject'], form.cleaned_data['mail_body'], settings.FILE_DEFAULT_EXPIRE_DOWNLOADS, settings.FILE_DEFAULT_EXPIRE_TIME,None, form.cleaned_data['email_from'])
            return TemplateResponse(request, "clinic/clinic_form_success.html", {'share_link':share_link})
        else:
            context['form'] = form
            return TemplateResponse(request, "clinic/clinic_form.html", context)
        return TemplateResponse(request, "clinic/clinic_form.html", context)
    else:
        context['form'] = form
        return TemplateResponse(request, "clinic/clinic_form.html", context)

def patient_send_file(request):
    context = {}
    form = PatientForm(request.POST or None, request.FILES or None)
    if request.POST:
        if form.is_valid():
            file_path = handle_uploaded_file(request.FILES["upload"])
            share_link = handle_form_submission(settings.FILE_DEFAULT_EXPIRE_DOWNLOADS, settings.FILE_DEFAULT_EXPIRE_TIME, file_path)
            mail_to = get_clinic_to_emails(form.cleaned_data['send_choices'])
            send_share_link(settings.CLINIC_NAME, mail_to, share_link, settings.DEFAULT_PATIENT_TO_CLINIC_SUBJECT, settings.DEFAULT_PATIENT_TO_CLINIC_SUBJECT, settings.FILE_DEFAULT_EXPIRE_DOWNLOADS, settings.FILE_DEFAULT_EXPIRE_TIME, form.cleaned_data['name'])
            return TemplateResponse(request, "clinic/patient_form_success.html", {'share_link':share_link})
        else:
            context['form'] = form
            return TemplateResponse(request, "clinic/patient_form.html", context)
        return TemplateResponse(request, "clinic/patient_form.html", context)
    else:
        context['form'] = form
        return TemplateResponse(request, "clinic/patient_form.html", context)
