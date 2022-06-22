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


@aule.route('/aule', methods=['POST'])
@token_required(restrict_to_roles=['amministratore'])
def add_aule(user):
    name = request.form.get('name')
    building = request.form.get('building')
    campus = request.form.get('campus')
    capacity = request.form.get('capacity')

    if name is None:
        return jsonify({'error': True, 'errormessage': 'Nome mancante'}), 404

    if building is None:
        return jsonify({'error': True, 'errormessage': 'Edificio mancante'}), 404

    if campus is None:
        return jsonify({'error': True, 'errormessage': 'Campus mancante'}), 404

    if capacity is None:
        return jsonify({'error': True, 'errormessage': 'Capienza mancante'}), 404

    if sessionAmministratori.query(Aula).filter(Aula.nome == name, Aula.campus == campus, Aula.edificio == building).first():
        return jsonify({'error': True, 'errormessage': 'Aula gia\' esistente con le stesse informazioni'}), 404

    new_aula = Aula(nome=name, edificio=building, campus=campus, capienza=capacity)

    try:
        sessionAmministratori.add(new_aula)
        sessionAmministratori.commit()
    except Exception as e:
        sessionAmministratori.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore inserimento aula' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200


@aule.route('/aule', methods=['GET'])
def get_aule():
    skip = request.args('skip')
    limit = request.args('limit')
    name = request.args('name')
    building = request.args('building')
    campus = request.args('campus')

    aule = preLoginSession.query(Aula).order_by(Aula.campus, Aula.edificio, Aula.nome, Aula.capienza)

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
        return jsonify({'error': True, 'errormessage': 'Impossibile recuperare alcun utente'}), 404
    else:
        return jsonify(aule_schema.dump(aule.all())), 200


@aule.route('/aule/<id>', methods=['GET'])
def get_aula(id):
    try:
        aula = preLoginSession.query(Aula).filter(Aula.id == id).first()
    except Exception as e:
        return jsonify({'error': True, 'errormessage': 'Impossibile reperire l\'aula: ' + str(e)}), 404

    if aula is None:
        return jsonify({'error': True, 'errormessage': 'Aula inesistente'}), 404
    else:
        return jsonify(aula_schema.dump(aula)), 200