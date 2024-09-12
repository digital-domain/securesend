from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("clinic-send-file/", views.clinic_send_file, name="clinic_send_file"),
    path("patient-send-file/", views.patient_send_file, name="patient_send_file"),
]
