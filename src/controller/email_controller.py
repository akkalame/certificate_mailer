import base64
import smtplib
import yagmail
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email import encoders
import mimetypes
import os


def create_message_with_attachment(to,subject, sender=None,body="",attachments=[], get_raw=True):
    message = MIMEMultipart()
    message['To'] = to
    if sender:
        message['From'] = sender
    message['Subject'] = subject
    #message["Importance"] = "high"

    message.attach(MIMEText(body, 'html'))
    for attach in attachments:
        message.attach(attach)

    if get_raw:
        raw_message = base64.urlsafe_b64encode(message.as_string().encode('utf-8'))
        return {'raw': raw_message.decode('utf-8')}
    else:
        message.as_string()

def get_attachment(filePath):
    (content_type, encoding) = mimetypes.guess_type(filePath)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'

    (main_type, sub_type) = content_type.split('/', 1)
    if main_type == 'text':
        with open(filePath, 'rb') as f:
            attachmentFile = MIMEText(f.read().decode('utf-8'), _subtype=sub_type)

    elif main_type == 'image':
        with open(filePath, 'rb') as f:
            attachmentFile = MIMEImage(f.read(), _subtype=sub_type)
        
    elif main_type == 'audio':
        with open(filePath, 'rb') as f:
            attachmentFile = MIMEAudio(f.read(), _subtype=sub_type)
        
    else:
        with open(filePath, 'rb') as f:
            attachmentFile= MIMEBase(main_type, sub_type)
            attachmentFile.set_payload(f.read())

            encoders.encode_base64(attachmentFile)

    filename = os.path.basename(filePath)
    attachmentFile.add_header('Content-Disposition', 'attachment',filename=filename)
    return attachmentFile

def send_gmail(service, sender,to,subject,body,attachments=[]):
    attachments = []
    for path in attachments:
        attachments.append(get_attachment(path))
   
    msg = create_message_with_attachment(to=to, subject=subject, body=body,attachments=attachments)
    return service.users().messages().send(userId='me',body=msg).execute()

def send_smtp(service, sender_email, to, subject, body, attachments=[]):
    #attachments = []
    # Adjuntar archivos
    #for attachment_path in attachments:
    #    attachment = get_attachment(attachment_path)

    #msg = create_message_with_attachment(to=to, subject=subject, body=body,attachments=attachments)
    # Enviar correo electrónico
    r = service.send(to=to, subject=subject, contents=body, attachments=attachments)

def smtp_service(sender_email, sender_password, smtp_server, smtp_port, use_tls=True):
    # Iniciar conexión SMTP
    try:
        service = yagmail.SMTP(sender_email, sender_password, smtp_server, int(smtp_port))
        # Establecer conexión segura si se especifica TLS
        #if use_tls:
        #    server.starttls()
        # Iniciar sesión en el servidor SMTP
        #service = server.login(sender_email, sender_password)
        return service
    except Exception as e:
        raise e
    


