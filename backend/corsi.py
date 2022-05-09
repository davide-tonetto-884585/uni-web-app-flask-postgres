import os
from flask import Blueprint, jsonify, request, current_app

from . import PreLoginSession, SessionDocenti
from .marshmallow_models import CorsoSchema, DocenteSchema
from .auth import token_required
from .models import Corso, Docente
from .utils import load_file

corsi = Blueprint('corsi', __name__)

preLoginSession = PreLoginSession()
sessionDocenti = SessionDocenti()

corsi_schemas = CorsoSchema(many=True) # converte un array di oggetti corsi in un array di json
corsi_schema = CorsoSchema() # converte un singolo oggetto corso in json
docenti_schemas = DocenteSchema(many=True)


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
def add_corso(user): #su tutte token_required bisogna mettere user (per reperire i dati di chi è loggato)
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


# /corsi/:id                                                               PUT           Modify course
@corsi.route('/corsi/<id>', methods=['PUT'])
@token_required(restrict_to_roles=['amministratore', 'docente'])
def modify_corso(id, user):
    corso = sessionDocenti.query(Corso).filter(Corso.id == id).first()
    
    # Campi del form
    titolo = request.form.get('titolo')
    descrizione = request.form.get('descrizione')
    lingua = request.form.get('lingua')
    abilitato = request.form.get('abilitato')

    # DA CHIEDERE SE REPERISCE CORRETTAMENTE IL PATH DELL'IMMAGINE DAL FORM
    path_to_immagine_copertina = load_file('immagine_copertina')
    path_to_file_certificato = load_file('file_certificato')

    if titolo is not None:
        corso.titolo = titolo

    if abilitato is not None:
        corso.abilitato = abilitato

    corso.descrizione = descrizione
    corso.lingua = lingua
    corso.immagine_copertina = path_to_immagine_copertina
    corso.file_certificato = path_to_file_certificato

    try:
        sessionDocenti.commit()
    except Exception as e:
        sessionDocenti.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore aggiornamento informazioni del corso: ' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200

@corsi.route('/corsi/<id>/docenti', methods=['GET'])
def get_docenti_corsi(id):
    #corso = preLoginSession.query(Corso).filter(Corso.id == id)
    #docenti = preLoginSession.query(Docente).join(Corso).all()
    #docenti = preLoginSession.query(Docente, Corso).filter(Corso.id == id)

    try:
        docenti = preLoginSession.query(Docente, Corso).filter(Corso.id == id)
        docenti = docenti.all()
    except Exception as e:
        return jsonify({'error': True, 'errormessage': 'Impossibile reperire docenti del corso: ' + str(e)}), 404

    if docenti is None:
        return jsonify({'error': True, 'errormessage': 'Corso senza docenti attualmente assegnati'}), 404
    else:
        return jsonify(docenti_schemas.dump(docenti)), 200


@corsi.route('/corsi/<id>/docenti', methods=['POST'])
@token_required(restrict_to_roles=['amministratore'])
def modify_corso(id, user):
    #TODO