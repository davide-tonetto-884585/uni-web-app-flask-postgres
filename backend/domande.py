"""


	/corsi/:id/domande                                                       DELETE        remove domanda corso

	/corsi/:id/domande/:id/like                                              GET           Get number of like of the question
	/corsi/:id/domande/:id/like                                              POST          Add like to question
	/corsi/:id/domande/:id/like                                              DELETE        Remove like from question
"""

import json
from flask import Blueprint, jsonify, request
from sqlalchemy import func

from . import PreLoginSession, SessionDocenti, SessionAmministratori, SessionStudenti
from .marshmallow_models import DomandeCorsoSchema, LikeDomandaSchema
from .auth import token_required
from .models import DomandeCorso, LikeDomanda, Docente, DocenteCorso, Utente, ProgrammazioneCorso, ProgrammazioneLezioni, PresenzeLezione, Studente, IscrizioniCorso, Aula, Corso

domande = Blueprint('domande_corso', __name__)

preLoginSession = PreLoginSession()
sessionDocenti = SessionDocenti()
sessionAmministratori = SessionAmministratori()
sessionStudenti = SessionStudenti()

domande_corso_schema = DomandeCorsoSchema(many=True)
domanda_corso_schema = DomandeCorsoSchema()
likes_domanda_schema = LikeDomandaSchema(many=True)
like_domanda_schema = LikeDomandaSchema()


@domande.route('/corsi/<id>/domande', methods=['GET'])
def get_domande(id):
    # Parametri del form
    testo = request.args.get('testo')
    chiusa = request.args.get('chiusa')
    skip = request.args.get('skip')
    limit = request.args.get('limit')

    # Query per reperire le domande con il relativo numero dei like
    domande = preLoginSession.query(Utente.nome, Utente.cognome, Utente.id, DomandeCorso.id,
        DomandeCorso.testo, func.count(DomandeCorso.id).label('total_likes')).\
        join(Utente, DomandeCorso.id_utente == Utente.id).\
        join(LikeDomanda, DomandeCorso.id == LikeDomanda.id_domanda_corso).\
        group_by(DomandeCorso.id, Utente.nome, Utente.cognome, Utente.id, DomandeCorso.testo)

    # Filtri per la specializzazione della ricerca o visualizzazione dei corsi
    if testo is not None:
        domande = domande.filter(DomandeCorso.testo.like('%' + testo + '%'))
    if skip is not None:
        domande = domande.offset(skip)
    if limit is not None:
        domande = domande.limit(limit)
    if chiusa is not None:
        domande = domande.filter(DomandeCorso.chiusa == chiusa)

    return jsonify(json.loads(json.dumps([dict(domanda._mapping) for domanda in domande]))), 200


@domande.route('/corsi/<id>/domande', methods=['POST'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def add_domande(user, id):

    # Controlliamo che gli studenti siano iscritti al corso prima di porre domande
    if 'studente' in user['roles']:
        try:
            id_studenti_corso = sessionDocenti.query(IscrizioniCorso.id_studente).\
                filter(IscrizioniCorso.id_corso == id).all()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Errore nel reperire studenti del corso: ' + str(e)}), 500

        # controllo che lo studente sia nella lista degli studenti iscritti al corso
        if (user['id'] not in id_studenti_corso):
            return jsonify({'error': True, 'errormessage': 'Devi essere iscritto al corso per poter porre delle domande'}), 401

    # controllo che i campi obbligatori siano stati inseriti nel form (id_domanda_corso non è obbligatorio)
    testo = request.form.get('testo')
    id_domanda_corso = request.form.get('id_domanda_corso')     # ID della domanda da rispondere
    chiusa = False

    # Controlla che i campi obbligatori siano stati inseriti nel form
    # NOTA: Solo i docenti del corso possono "chiudere le domande"
    if testo is None:
        return jsonify({'error': True, 'errormessage': 'Dati mancanti'}), 400

    if ('docenti' in user['roles']):
        id_docenti_corso = sessionDocenti.query(DocenteCorso.id_docente).filter(DocenteCorso.id_corso == id).all()

        if (user['id'] in id_docenti_corso or 'amministratore' in user['roles']):
            chiusa = False if request.form.get('chiusa') is None else request.form.get('chiusa')

    # Controlla che la domanda a cui si vuole rispondere esista
    if id_domanda_corso is not None:
        try:
            id_domande_corso = sessionDocenti.query(DomandeCorso.id).\
                    filter(DomandeCorso.id_corso == id).all()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Errore nell\'inserimento della risposta: '  + str(e)}), 500

        if (id_domanda_corso not in id_domande_corso):
            return jsonify({'error': True, 'errormessage': 'Domanda inesistente'}), 400

    # creazione del nuovo oggetto da inserire
    new_domanda_corso = DomandeCorso(testo = testo, chiusa = chiusa, id_corso = id,
                                    id_utente = user['id'], id_domanda_corso = id_domanda_corso)

    # prova di inserimento della nuova programmazione del corso
    try:
        sessionAmministratori.add(new_domanda_corso)
        sessionAmministratori.commit()
    except Exception as e:
        sessionAmministratori.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore nell\'inserimento della domanda: ' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200
