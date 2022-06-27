import json
from flask import Blueprint, jsonify, request

from . import PreLoginSession, SessionDocenti, SessionAmministratori, SessionStudenti
from .marshmallow_models import RisorseCorsoSchema
from .auth import token_required
from .models import ProgrammazioneCorso, Corso, Studente, IscrizioniCorso, RisorseCorso

risorse = Blueprint('risorse_corso', __name__)

preLoginSession = PreLoginSession()
sessionDocenti = SessionDocenti()
sessionAmministratori = SessionAmministratori()
sessionStudenti = SessionStudenti()

risorsa_corso_schema = RisorseCorsoSchema()
risorse_corso_schema = RisorseCorsoSchema(many=True)


@risorse.route('/corso/<id>/risorse', methods=['GET'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def get_risorse(user, id):
    skip = request.args.get('skip')
    limit = request.args.get('limit')
    name = request.args.get('nome')
    visible = request.args.get('visibile')

    # TODO: CAPIRE SE 'user' EFFETTIVAMENTE HA ANCHE LA CHIAVE 'id'
    if (user['role'] == 'studente'):

        # Controlliamo che lo studente sia iscritto al corso, altrimento non mostriamo le risorse
        if(sessionDocenti.query(IscrizioniCorso.id_studente).\
            join(ProgrammazioneCorso, ProgrammazioneCorso.id == IscrizioniCorso.id_programmazione_corso).\
            filter(ProgrammazioneCorso.id_corso == id, IscrizioniCorso.id_studente == user['id']).count() == 0):

            return jsonify({'error': True, 'errormessage': 'Non puoi vedere la/e risorsa/e di questo corso'}), 401

        # Se per qualche motivo è impostato (e lo studente è iscritto al corso), allora forza la visualizzazione a True
        else:
            if (visible is not None): visible = True

    elif(False):     # TODO: Contrllo del docente che deve avere il corso (DA FARE)
        visibile = true

    
    if (user['role'] == 'studente' and visible is not None):
        visible = True

    risorse = sessionStudenti.query(RisorseCorso).\
        filter(RisorseCorso.id_corso == id).\
        order_by(RisorseCorso.nome, RisorseCorso.visibile)

    if visible is not None:
        risorse = risorse.filter(RisorseCorso.visibile == visible)
    if name is not None:
        risorse = risorse.filter(RisorseCorso.nome.like('%' + name + '%'))
    if skip is not None:
        risorse = risorse.offset(skip)
    if limit is not None:
        risorse = risorse.limit(limit)

    if risorse is None:
        return jsonify({'error': True, 'errormessage': 'Nessuna risorsa del corso disponibile'}), 404
    else:
        return jsonify(risorse_corso_schema.dump(risorse)), 200


"""	
	/corsi/:id/risorse                                                       POST          Add risorsa del corso
"""
@risorse.route('/corso/<id>/risorse', methods=['POST'])
@token_required(restrict_to_roles=['amministratore', 'docente'])
def add_risorsa(user, id):
    # TODO: Controllare docente abbia corso

    if request.form.get('id_studente') is None or request.form.get('codice_verifica_presenza') is None:
        return jsonify({'error': True, 'errormessage': 'Dati mancanti'}), 404
    
    studente = sessionStudenti.query(Studente).filter(studente.id == request.form.get('id_studente')).first()
    if studente is None:
        return jsonify({'error': True, 'errormessage': 'Studente inesistente'}), 401

    if sessionStudenti.query(IscrizioniCorso).\
        join(ProgrammazioneCorso, ProgrammazioneCorso.id == IscrizioniCorso.id_programmazione_corso).\
        filter(IscrizioniCorso.id_studente == studente.id and ProgrammazioneCorso.id == id_prog).count() == 0:
        return jsonify({'error': True, 'errormessage': 'Studente non iscritto al corso'}), 401
    
    lezione = sessionStudenti.query(ProgrammazioneLezioni).filter(ProgrammazioneLezioni.id == id_lezione).first()
    if lezione.codice_verifica_presenza != request.form.get('codice_verifica_presenza'):
        return jsonify({'error': True, 'errormessage': 'Codice verifica non valido'}), 401

    new_presenza = PresenzeLezione(id_studente=studente.id, id_lezione=id_lezione)
    
    try:
        sessionStudenti.add(new_presenza)
        sessionStudenti.commit()
    except Exception as e:
        sessionStudenti.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore inserimento lezione' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200