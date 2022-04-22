from flask_mail import Message

from . import mail

def send_mail(subjects, object, body):
    msg = Message(object, sender = 'pigeonline.project@gmail.com', recipients = subjects,)
    msg.body = body
    mail.send(msg)