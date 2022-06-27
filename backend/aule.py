import json
from flask import Blueprint, jsonify, request

from . import PreLoginSession, SessionAmministratori
from .marshmallow_models import AulaSchema
from .auth import token_required
from .models import Aula

aule = Blueprint('aule', __name__)

preLoginSession = PreLoginSession()
sessionAmministratori = SessionAmministratori()

# converte un array di oggetti corsi in un array di json
aule_schema = AulaSchema(many=True)
aula_schema = AulaSchema()


@aule.route('/aule', methods=['GET'])
def get_aule():
    # Parametri del form
    skip = request.args.get('skip')
    limit = request.args.get('limit')
    name = request.args.get('name')
    building = request.args.get('building')
    campus = request.args.get('campus')

    # Query per recuperare tutte le aule
    aule = preLoginSession.query(Aula).order_by(Aula.campus, Aula.edificio, Aula.nome)

    # Filtri per specializzazre la ricerca e/o la visualizzazione delle aule
    if name is not None:
        aule = aule.filter(Aula.nome.like('%' + name + '%'))
    if building is not None:
        aule = aule.filter(Aula.building.like('%' + building + '%'))
    if campus is not None:
        aule = aule.filter(Aula.campus.like('%' + campus + '%'))
    if skip is not None:
        aule = aule.offset(skip)
    if limit is not None:
        aule = aule.limit(limit)

    if aule is None:
        # Se non trova alcun'aula, ritorna uno status code 404
        return jsonify({'error': True, 'errormessage': 'Impossibile recuperare la/e aula/e'}), 404
    else:
        return jsonify(aule_schema.dump(aule.all())), 200


@aule.route('/aule', methods=['POST'])
@token_required(restrict_to_roles=['amministratore'])
def add_aule(user):
    name = request.form.get('nome')
    building = request.form.get('edificio')
    campus = request.form.get('campus')
    capacity = request.form.get('capienza')

    # Controlla i campi necessari per l'inserimento dell'aula
    if name is None:
        return jsonify({'error': True, 'errormessage': 'Nome mancante'}), 400

    if building is None:
        return jsonify({'error': True, 'errormessage': 'Edificio mancante'}), 400
    
    if campus is None:
        return jsonify({'error': True, 'errormessage': 'Campus mancante'}), 400

    if capacity is None:
        return jsonify({'error': True, 'errormessage': 'Capienza mancante'}), 400

    # Controlla che l'aula non sia già presente nello stesso campus e nello stesso edificio
    if sessionAmministratori.query(Aula).filter(Aula.nome == name, Aula.campus == campus, Aula.edificio == building).first():
        return jsonify({'error': True, 'errormessage': 'Aula gia\' esistente con le stesse informazioni'}), 404

    # Crea un nuovo oggetto di tipo Aula da inserire
    new_aula = Aula(nome=name, edificio=building, campus=campus, capienza=capacity)

    try:
        # Aggiunge l'aula nel DB
        sessionAmministratori.add(new_aula)
        sessionAmministratori.commit()
    except Exception as e:
        sessionAmministratori.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore inserimento aula' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200


@aule.route('/aule/<id>', methods=['GET'])
def get_aula(id):
    try:
        # Query per recuperare l'aula tramite id
        aula = preLoginSession.query(Aula).filter(Aula.id == id).one()
    except Exception as e:
        return jsonify({'error': True, 'errormessage': 'Impossibile reperire l\'aula: ' + str(e)}), 500

    if aula is None:
        return jsonify({'error': True, 'errormessage': 'Aula inesistente'}), 404
    else:
        return jsonify(aula_schema.dump(aula)), 200