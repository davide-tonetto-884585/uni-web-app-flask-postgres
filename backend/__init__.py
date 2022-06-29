"""
	Endpoints            Attributes                 Description              Method        Description
	-------------------------------------------------------------------------------------------------------------------------------
	BLUEPRINT auth:

	/utenti/studenti            ...                                          GET           List all students


	/utenti/studenti/           -                                            POST          Add a new student
	/utenti/studenti/:id        -                                            POST          Complete student registration


	/utenti/docenti             ...                                          GET           List all teachers


	/utenti/docenti             -                                            POST          Add a new teacher
	/utenti/docenti/:id         -                                            POST          Complete teacher registration
	/utenti/amministratori/:id  -                                            POST          Add a new administrator
	/login               -                                                   GET           Login an existing user, returning a JWT
	/utenti/studenti                                                         GET           List all students
					?name=nome                  cerca per nome
					?surname=cognome            cerca per cognome
					?skip=n                     salta i primi n stud
					?limit=m                    restituisce m stud
	/utenti/studenti/:id													 GET           Get student by id
	/utenti/studenti/:id/iscrizioni											 GET
    /utenti/docenti/:id/corsi												 GET
	/utenti/docenti															 GET           List all teachers
						?name=nome                  cerca per nome
						?surname=cognome            cerca per cognome
						?skip=n                     salta i primi n utenti
						?limit=m                    restituisce m utenti
	/utenti/docenti/:id                                                      GET           Get docente by id
	/utenti																	 GET           List all users
						?name=nome                  cerca per nome
						?surname=cognome            cerca per cognome
						?birthdate=birthdate		cerca per data di nascita (precisa)
						?skip=n						salta i primi n utenti
						?limit=m					restituisce m utenti
	/utenti/:id                                                              GET           Get user by id

	-------------------------------------------------------------------------------------------------------------------------------
	BLUEPRINT main:

	/                    -                                                   GET           Returns the version and a list of
																						   available endpoint

	/scuole              ?nome                      filtra per nome          GET           List all schools
						 ?skip=n                    salta i primi n ris
						 ?limit=m                   restituisce m ris

	------------------------------------------------------------------------------------------------------------------------------
	BLUEPRINT corsi:

	/corsi               ?lingua                                             GET           List all courses
						 ?name=nome                  prende i corsi per nome
						 ?skip=n                     salta i primi n corsi
						 ?limit=m                    restituisce m corsi
	/corsi/:id            -                                                  GET           Get course by id
	/corsi                -                                                  POST          Insert new course
	/corsi/:id/docenti                                                       GET           Get docenti del corso
	/corsi/:id                                                               PUT           Modify course
	/corsi/:id																 PUT           Modify course
	/corsi/:id/docenti														 POST          add docente al corso
	/corsi/:id/docenti                                                       DELETE        remove docente from course
	/corsi/:id                                                               DELETE        remove course
	/corsi/:id/studenti                                                      GET           Get all students registred to course :id

	------------------------------------------------------------------------------------------------------------------------------
	BLUEPRINT aule:

	/aule                                                                    POST          Add aula
	/aule                                                                    GET           Get aula
                  ?name=nome                  cerca per nome
                  ?building=edificio          cerca per edificio
                  ?campus=campus      		cerca per campus
                  ?skip=n						salta le prime n aule
                  ?limit=m					restituisce m aule
	/aule/:id                                                                GET           Get aula by id

	------------------------------------------------------------------------------------------------------------------------------
	BLUEPRINT programmazione_corso

	/corso/:id/programmazione_corso                                          POST          Add prog corso
	/corso/:id/programmazione_corso/                                         GET
	/corso/:id/programmazione_corso/:id                                      GET

	/corso/:id/programmazione_corso/:id/lezioni                              POST          add lezione
	/corso/:id/programmazione_corso/:id/lezioni                              GET
	/corso/:id/programmazione_corso/:id/lezioni/:id                          GET

	/corso/:id/programmazione_corso/:id/lezioni/:id/presenze                 GET
	/corso/:id/programmazione_corso/:id/lezioni/:id/presenze                 POST
 	/corso/:id/programmazione_corso/:id/iscrizioni                           POST
	/corso/:id/programmazione_corso/:id/iscrizioni                           GET
	/corso/:id/programmazione_corso/:id/iscrizioni/:id_studente              DELETE

	------------------------------------------------------------------------------------------------------------------------------
	BLUEPRINT risorse:

	/corsi/:id/risorse                                                       GET           Get risorse del corso
	/corsi/:id/risorse                                                       POST          Add risorsa del corso
	/corsi/:id/risorse/:id                                                   DELETE        Remove risorsa del corso
	/corsi/:id/risorse/:id                                                   PUT           Modify risorsa del corso

	-------------------------------------------------------------------------------------------------------------------------------
	BLUEPRINT domande:

    /corsi/:id/domande                                                      GET           Get domande corso
                        ?testo=testi               cerca per il testo
                        ?chiusa=chiusa             trova le domande chiuse
                        ?skip=n                    salta i primi n doc
                        ?limit=m                   restituisce m doc
	/corsi/:id/domande                                                       POST          Add domanda corso

	-------------------------------------------------------------------------------------------------------------------------------
	DA CONTROLLARE

	/corsi/:id/domande                                                       DELETE        remove domanda corso


	DA IMPLEMENTARE:

	TODO: Fare in modo che all'eliminazione di una risorsa o di un corso vengano eliminate anche le immagini o file dal server


	/corsi/:id/domande/:id/like                                              GET           Get number of like of the question
	/corsi/:id/domande/:id/like                                              POST          Add like to question
	/corsi/:id/domande/:id/like                                              DELETE        Remove like from question

   -------------------------------------------------------------------------------------------------------------------------------
"""

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

    # blueprint per i corsi
    from .corsi import corsi as corsi_blueprint
    app.register_blueprint(corsi_blueprint)

    # blueprint per programmazione corsi e lezioni
    from .programmazione_corsi import prog_corsi as prog_corsi_blueprint
    app.register_blueprint(prog_corsi_blueprint)

    # blueprint per le aule
    from .aule import aule as aule_blueprint
    app.register_blueprint(aule_blueprint)

	# blueprint per le risorse del corso
    from .risorse import risorse as risorse_blueprint
    app.register_blueprint(risorse_blueprint)

    from .domande import domande as domande_corso_blueprint
    app.register_blueprint(domande_corso_blueprint)

    return app
