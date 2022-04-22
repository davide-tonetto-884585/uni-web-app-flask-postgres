from flask_login import UserMixin
from . import db

class Utente(db.Model, UserMixin):
    __table__ = db.Model.metadata.tables['utenti']
    
class Studente(db.Model):
    __table__ = db.Model.metadata.tables['studenti']

class Docente(db.Model):
    __table__ = db.Model.metadata.tables['docenti']
    
    