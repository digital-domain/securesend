import os
import uuid
import smtplib
import zipfile
from datetime import datetime
from os.path import basename
from django.conf import settings
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def get_unique_upload_path(file_name):
    initial_path = settings.UPLOAD_PATH + '' + file_name + ''
    if os.path.exists(initial_path):
        return settings.UPLOAD_PATH + '' + uuid.uuid4().hex[:10] + '-' + file_name + ''
    return initial_path


def handle_uploaded_file(f):
    path = get_unique_upload_path(f.name)
    with open(path, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return path

def handle_multiple_uploaded_files(files):
    path = settings.UPLOAD_PATH + '' + settings.CLINIC_NAME.replace(' ','').lower() + '_' + datetime.now().strftime('%d%m%Y') + '_' + str(uuid.uuid4().hex[:10]) + '.zip'
    zip_file = zipfile.ZipFile(path, 'w')
    for f in files:
        file_path = handle_uploaded_file(f)
        zip_file.write(file_path, f.name)
        os.remove(file_path)
    zip_file.close()
    return path


def handle_form_submission(expire_downloads, expire_time, file_path):
    command_string = "ffsend upload --copy --host " + settings.FILE_SEND_HOST + " --downloads " + expire_downloads + " --expiry-time " + expire_time + " " + "'" + file_path + "'"
    share_path = os.popen(command_string).read()
    print(command_string)
    os.remove(file_path)
    return share_path

def send_share_link(name, email, share_link, email_subject, email_body, expire_downloads, expire_time, client_name=None, email_from=None):
    subject = email_subject
    message = email_body
    if client_name:
        subject = client_name + email_subject
        message = client_name + email_body
    from_email = settings.EMAIL_FROM
    if email_from:
        from_email = email_from
    html_message = render_to_string('clinic/email_template.html', {'subject':subject, 'name':name, 'message':message, 'expire_downloads':expire_downloads, 'expire_time':expire_time, 'share_link' :share_link, 'header':settings.EMAIL_HEADER,})
    plain_message = strip_tags(html_message)
    print(from_email)
    print(email, from_email, subject)
    if isinstance(email, list):
        for entry in email:
            send_email(entry, from_email, subject, plain_message, html_message)
    else:
        send_email(email, from_email, subject, plain_message, html_message)

def get_clinic_to_emails(choices):
    to_addresses = [settings.CLINIC_EMAIL,]
    if 'admin' in choices:
        to_addresses.append(settings.CLINIC_ADMIN_EMAIL)
    if 'reception' in choices:
        to_addresses.append(settings.CLINIC_RECEPTION_EMAIL)
    if 'consultation' in choices:
        to_addresses.append(settings.CLINIC_CONSULTATION_EMAIL)
    if 'doctor' in choices:
        to_addresses.append(settings.CLINIC_DOCTOR_EMAIL)
    if 'lab' in choices:
        to_addresses.append(settings.CLINIC_LAB_EMAIL)
    to_addresses = list(dict.fromkeys(to_addresses))
    print(to_addresses)
    return to_addresses

def send_email(to_address, from_address, subject, message, html=None, files=None):
    #https://stackoverflow.com/questions/3362600/how-to-send-email-attachments
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(html,'html'))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(fil.read(),Name=basename(f))
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)

    s = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
    s.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
    s.sendmail(msg['From'], msg['To'], msg.as_string())
    print('s.sendmail', msg['From'], msg['To'])
    s.quit()
