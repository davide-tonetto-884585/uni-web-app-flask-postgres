import json
from flask import Blueprint, jsonify, request
from sqlalchemy import Date, Time, cast

from . import PreLoginSession, SessionDocenti, SessionAmministratori
from .marshmallow_models import CorsoSchema, DocenteSchema, ProgrammazioneCorsoSchema, ProgrammazioneLezioniSchema
from .auth import token_required
from .models import Corso, Docente, DocenteCorso, Utente, ProgrammazioneCorso, ProgrammazioneLezioni
from .utils import load_file

prog_corsi = Blueprint('programmazione_corsi', __name__)

preLoginSession = PreLoginSession()
sessionDocenti = SessionDocenti()
sessionAmministratori = SessionAmministratori()

programmazione_corsi_schema = ProgrammazioneCorsoSchema(many=True)
programmazione_corso_schema = ProgrammazioneCorsoSchema()
programmazione_lezioni_schema = ProgrammazioneLezioniSchema(many=True)
programmazione_lezione_schema = ProgrammazioneLezioniSchema()


# aggiunge una programmazione del corso indicato nella route
@prog_corsi.route('/corso/<id>/programmazione_corso', methods=['POST'])
@token_required(restrict_to_roles=['amministratore', 'docente'])
def add_prog_corso(user, id):
    if 'amministratore' not in user['roles']:
        try:
            docenti = preLoginSession.\
            query(Docente.id).\
            join(Utente, Utente.id == Docente.id).\
            join(DocenteCorso, DocenteCorso.id_docente == Docente.id).\
            filter(DocenteCorso.id_corso == id).all()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Impossibile reperire docenti del corso: ' + str(e)}), 404
     
        if (user['id'], ) not in docenti:
            return jsonify({'error': True, 'errormessage': 'Errore, non puoi programmare un corso a te non appartenente.'}), 401

    if request.form.get('modalita') is None or request.form.get('password_certificato') is None:
        return jsonify({'error': True, 'errormessage': 'Dati mancanti'}), 404
    
    new_prog_corso = ProgrammazioneCorso(modalità=request.form.get('modalita'),
                                         limite_iscrizioni=request.form.get('limite_iscrizioni'),
                                         password_certificato=request.form.get('password_certificato'),
                                         id_corso=id)
    
    try:
        sessionAmministratori.add(new_prog_corso)
        sessionAmministratori.commit()
    except Exception as e:
        sessionAmministratori.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore inserimento programmazione corso' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200


@prog_corsi.route('/corso/<id>/programmazione_corso', methods=['GET'])
def get_progs_corso(id):
    skip = request.args('skip')
    limit = request.args('limit')
    modality = request.args('modality')
    subscriptions_limit = request.args('subscriptions_limit')

    progs_corso = preLoginSession.query(ProgrammazioneCorso).filter(ProgrammazioneCorso.id_corso == id)


    # TODO: COME SI DEVE CONTROLLARE UN CAMPO ENUM? SI DEVE FARE UNA QUERY SULL'ENUM? DEVO CREARLO SUL SERVER?
    if modality is not None:
        progs_corso = progs_corso.filter(ProgrammazioneCorso.modalità.like('%' + modality + '%'))     # Accentato ?


    if subscriptions_limit is not None:
        progs_corso = progs_corso.filter(ProgrammazioneCorso.limite_iscrizioni == subscriptions_limit)
    if skip is not None:
        progs_corso = progs_corso.offset(skip)
    if limit is not None:
        progs_corso = progs_corso.limit(limit)

    if progs_corso is None:
        return jsonify({'error': True, 'errormessage': 'Impossibile recuperare alcun corso'}), 404
    else:
        return jsonify(programmazione_corsi_schema.dump(progs_corso.all())), 200


@prog_corsi.route('/corso/<id_corso>/programmazione_corso/<id_prog>', methods=['GET'])
def get_prog_corso(id_corso, id_prog):
    try:
        progr_corso = preLoginSession.query(ProgrammazioneCorso).filter(ProgrammazioneCorso.id_corso == id_corso, ProgrammazioneCorso.id == id_prog).first()
    except Exception as e:
        return jsonify({'error': True, 'errormessage': 'Impossibile reperire il corso: ' + str(e)}), 500

    if progr_corso is None:
        return jsonify({'error': True, 'errormessage': 'Programmazione del corso inesistente'}), 404
    else:
        return jsonify(programmazione_corso_schema.dump(progr_corso)), 200


@prog_corsi.route('/corso/<id_corso>/programmazione_corso/<id_prog>/lezioni', methods=['GET'])
def get_progs_corso(id_corso, id_prog):
    skip = request.args('skip')
    limit = request.args('limit')
    date = request.args('date')
    start_time = request.args('start_time')
    finish_time = request.args('finish_time')

    progs_lezioni = preLoginSession.query(ProgrammazioneLezioni).filter(ProgrammazioneLezioni.id_programmazione_corso == id_prog)

    if date is not None:
        progs_lezioni = progs_lezioni.filter(cast(ProgrammazioneLezioni.data, Date) == cast(date, Date))
    if start_time is not None:
        progs_lezioni = progs_lezioni.filter(cast(ProgrammazioneLezioni.orario_inizio, Time) == cast(start_time, Time))
    if finish_time is not None:
        progs_lezioni = progs_lezioni.filter(cast(ProgrammazioneLezioni.orario_fine, Time) == cast(finish_time, Time))
    if skip is not None:
        progs_lezioni = progs_lezioni.offset(skip)
    if limit is not None:
        progs_lezioni = progs_lezioni.limit(limit)

    if progs_lezioni is None:
        return jsonify({'error': True, 'errormessage': 'Impossibile recuperare alcuna lezione programmata'}), 404
    else:
        return jsonify(programmazione_lezioni_schema.dump(progs_lezioni.all())), 200


@prog_corsi.route('/corso/<id_corso>/programmazione_corso/<id_prog>/lezioni/<id_lezione>', methods=['GET'])
def get_prog_corso(id_corso, id_prog, id_lezione):
    try:
        progs_lezione = preLoginSession.query(ProgrammazioneLezioni).filter(ProgrammazioneLezioni.id_programmazione_corso == id_prog, ProgrammazioneLezioni.id == id_lezione).first()
    except Exception as e:
        return jsonify({'error': True, 'errormessage': 'Impossibile reperire la lezione: ' + str(e)}), 500

    if progs_lezione is None:
        return jsonify({'error': True, 'errormessage': 'Programmazione della lezione inesistente'}), 404
    else:
        return jsonify(programmazione_lezione_schema.dump(progs_lezione)), 200


# aggiunge una nuova lezione
@prog_corsi.route('/corso/<id_corso>/programmazione_corso/<id_prog>/lezioni', methods=['POST'])
@token_required(restrict_to_roles=['amministratore', 'docente'])
def get_progs_corso(user, id_corso, id_prog):
    date = request.form.get('date')
    start_time = request.form.get('start_time')
    finish_time = request.form.get('finish_time')
    link_virtual_class = request.form.get('link_virtual_class')
    passcode_virtual_class = request.form.get('passcode_virtual_class')
    presence_code = request.form.get('presence_code')
    
    if 'amministratore' not in user['roles']:
        try:
            docenti = preLoginSession.\
            query(Docente.id).\
            join(Utente, Utente.id == Docente.id).\
            join(DocenteCorso, DocenteCorso.id_docente == Docente.id).\
            filter(DocenteCorso.id_corso == id_corso).all()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Impossibile reperire docenti del corso: ' + str(e)}), 500
     
        if (user['id'], ) not in docenti:
            return jsonify({'error': True, 'errormessage': 'Errore, non puoi programmare una lezione di un corso a te non appartenente.'}), 401

    if date is None:
        return jsonify({'error': True, 'errormessage': 'Data mancante'}), 404

    if start_time is None:
        return jsonify({'error': True, 'errormessage': 'Orario inizio mancante'}), 404

    if finish_time is None:
        return jsonify({'error': True, 'errormessage': 'Orario fine mancante'}), 404



    # TODO: CONTROLLARE DALL'ENUM DI PROGRAMMAZIONE CORSO SE SI TRATTA DI DUALE OPPURE ONLINE (però stesso problema di prima)
    if link_virtual_class is None:
        return jsonify({'error': True, 'errormessage': 'Link stanza virtuale mancante'}), 404

    if passcode_virtual_class is None:
        return jsonify({'error': True, 'errormessage': 'Passcode stanza virtuale mancante'}), 404



    if presence_code is None:
        return jsonify({'error': True, 'errormessage': 'Codice verifica presenza mancante'}), 404


    # TODO: MODIFICARE OPPURTUNATAMENTE ANCHE QUESTO NEL CASO SIANO IN PRESENZA (filtrerebbe su valore Null altrimenti) E LA CREAZIONE DELL'OGGETTO
    if sessionAmministratori.query(ProgrammazioneCorso).filter(ProgrammazioneCorso.data == date, ProgrammazioneCorso.orario_inizio == start_time, ProgrammazioneCorso.orario_fine == finish_time, ProgrammazioneCorso.link_stanza_virtuale == link_virtual_class, ProgrammazioneCorso.passcode_stanza_virtuale == passcode_virtual_class, ProgrammazioneCorso.codice_verifica_presenza == presence_code).first():
        return jsonify({'error': True, 'errormessage': 'Lezione gia\' esistente con le stesse informazioni'}), 404

    new_lezione = ProgrammazioneCorso(data=date, orario_inizio=start_time, orario_fine=finish_time, link_stanza_virtuale=link_virtual_class, passcode_stanza_virtuale=passcode_virtual_class, codice_verifica_presenza=presence_code)

    try:
        sessionAmministratori.add(new_lezione)
        sessionAmministratori.commit()
    except Exception as e:
        sessionAmministratori.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore inserimento lezione' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200
