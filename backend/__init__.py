#  Endpoints            Attributes                 Description              Method        Description
#
#  /                    -                                                   GET           Returns the version and a list of available endpoint
#
#  BLUEPRINT auth:
#  /studenti            ...                                                 GET           List all students
#  /studenti/           -                                                   POST          Add a new student
#  /studenti/:id        -                                                   POST          Complete student registration
#  /docenti             ...                                                 GET           List all teachers
#  /docenti             -                                                   POST          Add a new teacher
#  /docenti/:id         -                                                   POST          Complete teacher registration
#  /amministratori/:id  -                                                   POST          Add a new administrator
#  /login               -                                                   GET           Login an existing user, returning a JWT
#
#  DA IMPLEMENTARE:
#  /corsi               ... (pensare a possibili filtri)                    GET           List all courses
#                       ?skip=n                    salta i primi n corsi
#                       ?limit=m                   restituisce m corsi
#
#  /corsi               -                                                   POST          Insert new course
#
#  /studenti            ... (pensare a possibili filtri)                    GET           List all students
#                       ?skip=n                    salta i primi n stud
#                       ?limit=m                   restituisce m stud
#
#  /docenti             ... (pensare a possibili filtri)                    GET           List all teachers
#                       ?skip=n                    salta i primi n doc
#                       ?limit=m                   restituisce m doc
#
# ------------------------------------------------------------------------------------

import os
from dotenv import load_dotenv
from flask import Flask
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from flask_mail import Mail
from flask_cors import CORS

# inizalizzo la libreria dotenv
load_dotenv()

# inizializzo SQLAlchemy
Base = declarative_base()

root_engine = create_engine(
    os.environ.get('SQLALCHEMY_DATABASE_URI'),
)
RootSession = sessionmaker(bind=root_engine)

preLogin_engine = create_engine(
    os.environ.get('SQLALCHEMY_DATABASE_URI_PRELOGIN'),
)
PreLoginSession = sessionmaker(bind=preLogin_engine)

engine_amministratori = create_engine(
    os.environ.get('SQLALCHEMY_DATABASE_URI_AMMINISTRATORI'),
)
SessionAmministratori = sessionmaker(bind=engine_amministratori)

engine_docenti = create_engine(
    os.environ.get('SQLALCHEMY_DATABASE_URI_DOCENTI'),
)
SessionDocenti = sessionmaker(bind=engine_docenti)

engine_studenti = create_engine(
    os.environ.get('SQLALCHEMY_DATABASE_URI_STUDENTI'),
)
SessionStudenti = sessionmaker(bind=engine_studenti)

# inizializzo flask_mail
mail = Mail()

# esetnsioni di file caricabili sul server
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER')

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'pigeonline.project@gmail.com'
    app.config['MAIL_PASSWORD'] = 'Chatta_Con_Piccioni'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    mail.init_app(app)

    app.config['CORS_HEADERS'] = 'Content-Type'

    CORS(app)

    # faccio reperire informazioni sul db da sqlalchemy
    Base.metadata.reflect(root_engine)

    # blueprint che gestisce la registrazione e autenticazione degli utenti
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
