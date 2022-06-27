from flask import Blueprint, jsonify, current_app, request

# Mettere "." (punto) prende in automatico "__init__.py", altrimenti si specifica dopo
from . import PreLoginSession
from .auth import token_required
from .models import Scuola
from .marshmallow_models import ScuolaSchema

main = Blueprint('main', __name__)

preLoginSession = PreLoginSession()
scuola_schemas = ScuolaSchema(many=True) #istanzia un oggetto che è scuola_schemas che serve a convertire gli oggetti Scuola in JSON


@main.route('/')
def index():
    return jsonify({"api_version": "1.0", "endpoints": ["/studenti", "/docenti", "/login"]}), 200

# http://localhost:5000/scuole?limit=10?skip=10?nome=levi
# Accedere da utenti loggati oppure no?  Quali ruoli possono accedervi (da loggati)?
@main.route('/scuole', methods=['GET'])
def get_scuole():

    # Campi del form
    name = request.args.get('nome')
    skip = request.args.get('skip')
    limit = request.args.get('limit')
    
    # Query per reperire tutte le scuole
    scuole = preLoginSession.query(Scuola).order_by(Scuola.denominazione)

    # Filtri per specializzare la ricerca delle scuole o la loro visualizzazione
    if name is not None:
        scuole = scuole.filter(Scuola.denominazione.like('%' + name + '%'))
    if skip is not None:
        scuole = scuole.offset(skip)
    if limit is not None:
        scuole = scuole.limit(limit) 

    return jsonify(scuola_schemas.dump(scuole.all())), 200
