import json
from flask import Blueprint, jsonify, request

from . import PreLoginSession, SessionDocenti, SessionAmministratori
from .marshmallow_models import AulaSchema, CorsoSchema, DocenteSchema
from .auth import token_required
from .models import Corso, Docente, DocenteCorso, Utente, Aula
from .utils import load_file

corsi = Blueprint('corsi', __name__)

preLoginSession = PreLoginSession()
sessionDocenti = SessionDocenti()
sessionAmministratori = SessionAmministratori()

# converte un array di oggetti corsi in un array di json
corsi_schemas = CorsoSchema(many=True)
corsi_schema = CorsoSchema()  # converte un singolo oggetto corso in json
docenti_schemas = DocenteSchema(many=True)
aule_schema = AulaSchema(many=True)
aula_schema = AulaSchema()


@corsi.route('/corsi', methods=['GET'])
def get_corsi():
    name = request.args.get('name')
    skip = request.args.get('skip')
    limit = request.args.get('limit')
    lingua = request.args.get('lingua')

    corsi = preLoginSession.query(Corso).order_by(Corso.titolo)
    if name is not None:
        corsi = corsi.filter(Corso.titolo.like('%' + name + '%'))
    if skip is not None:
        corsi = corsi.offset(skip)
    if limit is not None:
        corsi = corsi.limit(limit)
    if lingua is not None:
        corsi = corsi.filter(Corso.lingua.like('%' + lingua + '%'))

    return jsonify(corsi_schemas.dump(corsi.all())), 200


@corsi.route('/corsi/<id>', methods=['GET'])
def get_corso(id):
    corso = preLoginSession.query(Corso).filter(Corso.id == id)

    try:
        corso = corso.first()
    except Exception as e:
        return jsonify({'error': True, 'errormessage': 'Impossibile reperire corso: ' + str(e)}), 404

    if corso is None:
        return jsonify({'error': True, 'errormessage': 'Corso inesistente'}), 404
    else:
        return jsonify(corsi_schema.dump(corso)), 200


@corsi.route('/corsi', methods=['POST'])
@token_required(restrict_to_roles=['amministratore', 'docente'])
def add_corso(user):  # su tutte token_required bisogna mettere user (per reperire i dati di chi è loggato)
    if request.form.get('titolo') is None:
        return jsonify({'error': True, 'errormessage': 'Titolo mancante'}), 404

    if sessionDocenti.query(Corso).filter(Corso.titolo == request.form.get('titolo')).first():
        return jsonify({'error': True, 'errormessage': 'corso gia\' esistente con lo stesso titolo'}), 404

    path_to_immagine_copertina = load_file('immagine_copertina')
    path_to_file_certificato = load_file('file_certificato')

    abilitato = request.form.get('abilitato') if not None else True

    new_corso = Corso(titolo=request.form.get('titolo'),
                      descrizione=request.form.get('descrizione'),
                      lingua=request.form.get('lingua'),
                      immagine_copertina=path_to_immagine_copertina,
                      file_certificato=path_to_file_certificato,
                      abilitato=abilitato)

    try:
        sessionDocenti.add(new_corso)
        sessionDocenti.commit()
    except Exception as e:
        sessionDocenti.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore inserimento corso' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200


@corsi.route('/corsi/<id>', methods=['PUT'])
@token_required(restrict_to_roles=['amministratore', 'docente'])
def modify_corso(user, id):  # invertire
    corso = sessionDocenti.query(Corso).filter(Corso.id == id).first()

    # Campi del form
    titolo = request.form.get('titolo')
    descrizione = request.form.get('descrizione')
    lingua = request.form.get('lingua')
    abilitato = request.form.get('abilitato')

    # TODO permetter modifica dell'imagine di copertina e file certificato
    # path_to_immagine_copertina = load_file('immagine_copertina')
    # path_to_file_certificato = load_file('file_certificato')

    # corso.immagine_copertina = path_to_immagine_copertina
    # corso.file_certificato = path_to_file_certificato

    if titolo is not None:
        corso.titolo = titolo

    if abilitato is not None:
        corso.abilitato = abilitato

    corso.descrizione = descrizione
    corso.lingua = lingua

    try:
        sessionDocenti.commit()
    except Exception as e:
        sessionDocenti.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore aggiornamento informazioni del corso: ' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200


@corsi.route('/corsi/<id>/docenti', methods=['GET'])
def get_docenti_corsi(id):
    try:
        docenti = preLoginSession.\
            query(Utente.id, Utente.nome, Utente.cognome, Docente.immagine_profilo, Docente.link_pagina_docente, Docente.descrizione_docente).\
            join(Utente, Utente.id == Docente.id).\
            join(DocenteCorso, DocenteCorso.id_docente == Docente.id).\
            filter(DocenteCorso.id_corso == id).all()
    except Exception as e:
        return jsonify({'error': True, 'errormessage': 'Impossibile reperire docenti del corso: ' + str(e)}), 404

    if docenti is None:
        return jsonify({'error': True, 'errormessage': 'Corso senza docenti assegnati'}), 404
    else:
        return jsonify(json.loads(json.dumps([dict(docente._mapping) for docente in docenti]))), 200


@corsi.route('/corsi/<id>/docenti', methods=['POST'])
@token_required(restrict_to_roles=['amministratore'])
def add_docente_corso(user, id):
	id_docenti_to_add = set(request.post.get('id_docenti'))		# è già un array?   (Assumiamo che lo sia)

	try:
		for id_docente in id_docenti_to_add:
			sessionAmministratori.add(DocenteCorso(id_docente=id_docente, id_corso=id))

		sessionAmministratori.commit()
	except Exception as e:
		sessionAmministratori.rollback()
		return jsonify({'error': True, 'errormessage': 'Impossibile aggiungere uno (o più) docenti al corso'}), 500

	return jsonify({'error': False, 'errormessage': ''}), 200


"""
	/aule                                                                    POST           add aula
"""
@corsi.route('/aule', methods=['GET'])
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


@corsi.route('/aule/<id>', methods=['GET'])
def get_aula(id):
    aula = preLoginSession.query(Aula).filter(Aula.id == id)

    try:
        aula = aula.first()
    except Exception as e:
        return jsonify({'error': True, 'errormessage': 'Impossibile reperire l\'aula: ' + str(e)}), 404

    if aula is None:
        return jsonify({'error': True, 'errormessage': 'Aula inesistente'}), 404
    else:
        return jsonify(aula_schema.dump(aula)), 200


@corsi.route('/corsi', methods=['POST'])
@token_required(restrict_to_roles=['amministratore'])
def add_corso(user):
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
        sessionDocenti.add(new_aula)
        sessionDocenti.commit()
    except Exception as e:
        sessionDocenti.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore inserimento aula' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200