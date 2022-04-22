from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# inizializzo SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'provaChiaveSegreta'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:@localhost:5432/orientamento_dais'
    
    db.init_app(app)
    
    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
