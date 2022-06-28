import os
from flask import current_app, request
from flask_mail import Message
from werkzeug.utils import secure_filename

from . import ALLOWED_EXTENSIONS
from . import mail


def send_mail(subjects, object, body):
    msg = Message(object, sender='pigeonline.project@gmail.com',
                  recipients=subjects)
    msg.html = body
    mail.send(msg)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_file(request_parameter_name):
    path = None
    if request_parameter_name in request.files:
        file = request.files[request_parameter_name]
        # controllo se il file è valido
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(
                current_app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            path = path[1:].replace('\\', '/')
            
    return path
