from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# inizializzo SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'provaChiaveSegreta'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:@localhost:5432/orientamento_dais'