import json
from flask import Blueprint, jsonify, request
from sqlalchemy import Date, Time, cast

from . import PreLoginSession, SessionDocenti, SessionAmministratori, SessionStudenti
from .marshmallow_models import ProgrammazioneCorsoSchema, ProgrammazioneLezioniSchema
from .auth import token_required
from .models import Docente, DocenteCorso, Utente, ProgrammazioneCorso, ProgrammazioneLezioni, PresenzeLezione, Studente, IscrizioniCorso

prog_corsi = Blueprint('programmazione_corsi', __name__)

preLoginSession = PreLoginSession()
sessionDocenti = SessionDocenti()
sessionAmministratori = SessionAmministratori()
sessionStudenti = SessionStudenti()

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

    if modality is not None:
        progs_corso = progs_corso.filter(ProgrammazioneCorso.modalità == modality)  

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
def get_lezioni_progs_corso(id_corso, id_prog):
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
def get_lezione_prog_corso(id_corso, id_prog, id_lezione):
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
def add_lezione_prog_corso(user, id_corso, id_prog):
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

    prog_corso = preLoginSession.query(ProgrammazioneCorso).filter(ProgrammazioneCorso.id == id_prog).first()
    if prog_corso.modalità == 'online' or prog_corso.modalità == 'duale':
        if link_virtual_class is None:
            return jsonify({'error': True, 'errormessage': 'Link stanza virtuale mancante'}), 404

        if passcode_virtual_class is None:
            return jsonify({'error': True, 'errormessage': 'Passcode stanza virtuale mancante'}), 404

    if presence_code is None:
        return jsonify({'error': True, 'errormessage': 'Codice verifica presenza mancante'}), 404

    # TODO: Volevate controllare questo?
    if sessionAmministratori.\
        query(ProgrammazioneLezioni).\
        join(ProgrammazioneCorso, ProgrammazioneLezioni.id_programmazione_corso == ProgrammazioneCorso.id).\
        filter(
            ProgrammazioneLezioni.data == date, 
            ProgrammazioneLezioni.orario_inizio >= start_time, 
            ProgrammazioneLezioni.orario_inizio <= finish_time, 
            ProgrammazioneCorso.id == id_prog
        ).first():
        return jsonify({'error': True, 'errormessage': 'Lezione sovrapposta ad un\'altra'}), 404

    new_lezione = ProgrammazioneLezioni(data=date, orario_inizio=start_time, orario_fine=finish_time, link_stanza_virtuale=link_virtual_class, passcode_stanza_virtuale=passcode_virtual_class, codice_verifica_presenza=presence_code, id_corso=id_corso)

    try:
        sessionAmministratori.add(new_lezione)
        sessionAmministratori.commit()
    except Exception as e:
        sessionAmministratori.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore inserimento lezione' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200


"""
	/corso/:id/programmazione_corso/:id/lezioni/:id/presenze                 POST
"""
@prog_corsi.route('/corso/<id_corso>/programmazione_corso/<id_prog>/lezioni/<id_lezione>/presenze', methods=['GET'])
def get_presenze_lezione(id_corso, id_prog, id_lezione):
    skip = request.args('skip')
    limit = request.args('limit')
    name = request.args('name')
    lastname = request.args('lastname')

    presenze = preLoginSession.query(Utente.id, Utente.nome, Utente.cognome).filter(Utente.id == PresenzeLezione.id_studente, PresenzeLezione.id_programmazione_lezioni == id_lezione)

    if name is not None:
        presenze = presenze.filter(Utente.nome.like('%' + name + '%'))
    if lastname is not None:
        presenze = presenze.filter(Utente.cognome.like('%' + lastname + '%'))
    if skip is not None:
        presenze = presenze.offset(skip)
    if limit is not None:
        presenze = presenze.limit(limit)

    if presenze is None:
        return jsonify({'error': True, 'errormessage': 'Nessuna presenza per quella lezione'}), 404
    else:
        return jsonify(json.loads(json.dumps([dict(studente._mapping) for studente in presenze]))), 200
    
# /corso/:id/programmazione_corso/:id/lezioni/:id/presenze
@prog_corsi.route('/corso/<id_corso>/programmazione_corso/<id_prog>/lezioni/<id_lezione>/presenze', methods=['POST'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def add_presenza(user, id_corso, id_prog, id_lezione):
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

    new_presenza = PresenzeLezione(id_studente=studente.id,
                                   id_lezione=id_lezione)
    
    try:
        sessionStudenti.add(new_presenza)
        sessionStudenti.commit()
    except Exception as e:
        sessionStudenti.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore inserimento lezione' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200