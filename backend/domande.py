import json
from flask import Blueprint, jsonify, request
from sqlalchemy import func

from . import PreLoginSession, SessionDocenti, SessionAmministratori, SessionStudenti
from .marshmallow_models import DomandeCorsoSchema, LikeDomandaSchema
from .auth import token_required
from .models import DomandeCorso, LikeDomanda, DocenteCorso, Utente, IscrizioniCorso

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
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def get_domande(user, id):
    # Parametri del form
    testo = request.args.get('testo')
    chiusa = request.args.get('chiusa')
    skip = request.args.get('skip')
    limit = request.args.get('limit')

    # Query per reperire le domande con il relativo numero dei like
    domande = sessionStudenti.query(Utente.nome, Utente.cognome, Utente.id, DomandeCorso.id,
        DomandeCorso.testo, func.count(DomandeCorso.id).label('total_likes')).\
        join(Utente, DomandeCorso.id_utente == Utente.id).\
        join(LikeDomanda, DomandeCorso.id == LikeDomanda.id_domanda_corso).\
        group_by(DomandeCorso.id, Utente.id, Utente.cognome, Utente.nome, DomandeCorso.testo)

    # Filtri per la specializzazione della ricerca o visualizzazione dei corsi
    if testo is not None:
        domande = domande.filter(DomandeCorso.testo.like('%' + testo + '%'))
    if skip is not None:
        domande = domande.offset(skip)
    if limit is not None:
        domande = domande.limit(limit)
    if chiusa is not None:
        domande = domande.filter(DomandeCorso.chiusa == chiusa)

    domande = domande.all()

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

    # prova di inserimento della nuova domanda
    try:
        sessionStudenti.add(new_domanda_corso)
        sessionStudenti.commit()
    except Exception as e:
        sessionStudenti.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore nell\'inserimento della domanda: ' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200


@domande.route('/corsi/<id>/domande', methods=['DELETE'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def remove_domanda(user, id):
    id_domanda = request.form.get('id_domanda')

    if (id_domanda is None):
        return jsonify({'error': True, 'errormessage': 'Dati mancanti'}), 400

    try:
        domanda_to_remove = sessionStudenti.query(DomandeCorso).filter(DomandeCorso.id == id_domanda).first()
    except Exception as e:
        return jsonify({'error': True, 'errormessage': 'Errore durante il reperimento della domanda: ' + str(e)}), 500

    # Controlliamo che lo studente che vuole eliminare la domanda sia effettivamente quello che l'ha posta
    if ('studente' in user['roles'] and domanda_to_remove.id_utente != user['id']):
        return jsonify({'error': True, 'errormessage': 'Non puoi rimuovere una domanda che non hai posto tu stesso'}), 401

    # Controlliamo che il docente sia proprietario del corso, altrimenti non permettiamo la rimozione delle domande
    if('docente' in user['roles'] and 'amministratore' not in user['roles']):
        try:
            if(sessionDocenti.query(DocenteCorso.id_docente).filter(DocenteCorso.id_corso == id).first() != user['id']):
                return jsonify({'error': True, 'errormessage': 'Non puoi rimuovere una domanda da un corso che non ti appartiene'}), 401
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Errore durante la verifica dei permessi: ' + str(e)}), 500

    try:
        sessionStudenti.delete(domanda_to_remove)
        sessionStudenti.commit()
    except Exception as e:
        sessionStudenti.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore nell\'eliminazione della domanda dal corso: ' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200


@domande.route('/corsi/<id_corso>/domande/<id_domanda>/like', methods=['GET'])
def get_likes_domanda(id_corso, id_domanda):
    skip = request.args.get('skip')
    limit = request.args.get('limit')
    name = request.args.get('nome')
    lastname = request.args.get('cognome')

    likes = preLoginSession.query(Utente.id, Utente.nome, Utente.cognome).\
        join(LikeDomanda, LikeDomanda.id_utente == Utente.id).\
        filter(LikeDomanda.id_domanda_corso == id_domanda)

    if skip is not None:
        likes = likes.offset(skip)
    if limit is not None:
        likes = likes.limit(limit)
    if name is not None:
        likes = likes.filter(Utente.nome.like('%' + name + '%'))
    if lastname is not None:
        likes = likes.filter(Utente.cognome.like('%' + lastname + '%'))

    likes = likes.all()

    return jsonify(json.loads(json.dumps([dict(like._mapping) for like in likes]))), 200


@domande.route('/corsi/<id_corso>/domande/<id_domanda>/like', methods=['POST'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def add_like_domanda(user, id_corso, id_domanda):

    try:
        if (sessionStudenti.query(DomandeCorso.id).filter(DomandeCorso.id == id_domanda).count() == 0):
            return jsonify({'error': True, 'errormessage': 'Domanda inesistente'}), 404
    except Exception as e:
        return jsonify({'error': True, 'errormessage': 'Errore nel reperimento della domanda: '  + str(e)}), 500

    try:
        if(sessionStudenti.query(LikeDomanda.id_utente).\
            filter(LikeDomanda.id_utente == user['id'], LikeDomanda.id_domanda_corso == id_domanda).count() != 0):

            return jsonify({'error': True, 'errormessage': 'Hai già messo like a questa domanda'}), 409
    except Exception as e:
        return jsonify({'error': True, 'errormessage': 'Errore nel controllo dei like duplicati: '  + str(e)}), 500

    # creazione del nuovo oggetto da inserire
    new_like_domanda = LikeDomanda(id_utente = user['id'], id_domanda_corso = id_domanda)

    # prova di inserimento del nuovo like alla domanda
    try:
        sessionStudenti.add(new_like_domanda)
        sessionStudenti.commit()
    except Exception as e:
        sessionStudenti.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore nell\'inserimento del like alla domanda: ' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200


@domande.route('/corsi/<id_corso>/domande/<id_domanda>/like', methods=['DELETE'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def delete_like_domanda(user, id_corso, id_domanda):
    # NOTA: Lasciamo la possibilità di eliminare i like indipendentemente da chi li ha messi solo all'amministratore
    # per questioni di sicurezza; i docenti non possono eliminare i like (W LA LIBERTà DI ESPRESSIONE!)

    id_utente = user['id']
    if ('amministratore' in user['roles']):
        id_utente = request.form.get('id_utente') if (request.form.get('id_utente') is not None) else user['id']

    try:
        # Recupera il like posto a quella domanda dell'utente corrente
        like_to_remove = sessionStudenti.query(LikeDomanda).\
            filter(LikeDomanda.id_utente == id_utente, LikeDomanda.id_domanda_corso == id_domanda).first()

        if (like_to_remove is None):
            return jsonify({'error': True, 'errormessage': 'Like inesistente'}), 404

        sessionStudenti.delete(like_to_remove)
        sessionStudenti.commit()
    except Exception as e:
        sessionStudenti.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore durante l\'eliminazione del like alla domanda: ' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200