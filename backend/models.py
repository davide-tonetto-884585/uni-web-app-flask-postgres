from flask_login import UserMixin
from . import db

class Utente(db.Model, UserMixin):
    __tablename__ = 'utenti'
    
    id = db.Column(db.Integer, primary_key=True)
    