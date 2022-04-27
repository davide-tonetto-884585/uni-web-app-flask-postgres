from flask_mail import Message

from . import ALLOWED_EXTENSIONS
from . import mail

def send_mail(subjects, object, body):
    msg = Message(object, sender = 'pigeonline.project@gmail.com', recipients = subjects,)
    msg.body = body
    mail.send(msg)
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS