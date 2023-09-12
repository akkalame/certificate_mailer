import base64
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email import encoders
import mimetypes
import os


def create_message_with_attachment(sender,to,subject,body,attachments=[]):
    message = MIMEMultipart()
    message['to'] = to
    #message['from'] = sender
    message['subject'] = subject
    message["Importance"] = "high"

    message.attach(MIMEText(body, 'html'))
    #print(message.as_string())
    for attach in attachments:
        message.attach(attach)
    #print(message.as_string())
    raw_message = base64.urlsafe_b64encode(message.as_string().encode('utf-8'))
    return {'raw': raw_message.decode('utf-8')}

def get_attachment(filePath):
    (content_type, encoding) = mimetypes.guess_type(filePath)
    #print((content_type, encoding))
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'

    (main_type, sub_type) = content_type.split('/', 1)
    #print((main_type, sub_type))
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
            #print(attachmentFile)

    filename = os.path.basename(filePath)
    #print(filename)
    attachmentFile.add_header('Content-Disposition', 'attachment',filename=filename)
    return attachmentFile

def send_gmail(service, sender,to,subject,body,filePath=[]):
    attachments = []
    for path in filePath:
        attachments.append(get_attachment(path))
   
    msg = create_message_with_attachment(sender,to, subject,body,attachments)
    return service.users().messages().send(userId='me',body=msg).execute()

    #print('Message Id: {}'.format(message['id']))



