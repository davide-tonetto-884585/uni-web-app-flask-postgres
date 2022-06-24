import json
from flask import Blueprint, jsonify, request
from sqlalchemy import Date, Time, cast

from . import PreLoginSession, SessionDocenti, SessionAmministratori, SessionStudenti
from .marshmallow_models import ProgrammazioneCorsoSchema, ProgrammazioneLezioniSchema
from .auth import token_required
from .models import Docente, DocenteCorso, Utente, ProgrammazioneCorso, ProgrammazioneLezioni, PresenzeLezione, Studente, IscrizioniCorso, Aula

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

    # Controlla che la lezione non vada a sovrapporsi ad un'altra
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


# Reperisce le presenze della lezione del corso
@prog_corsi.route('/corso/<id_corso>/programmazione_corso/<id_prog>/lezioni/<id_lezione>/presenze', methods=['GET'])
@token_required(restrict_to_roles=['amministratore', 'docente'])
def get_presenze_lezione(user, id_corso, id_prog, id_lezione):
    skip = request.args('skip')
    limit = request.args('limit')
    name = request.args('name')
    lastname = request.args('lastname')

    presenze = sessionDocenti.query(Utente.id, Utente.nome, Utente.cognome).filter(Utente.id == PresenzeLezione.id_studente, PresenzeLezione.id_programmazione_lezioni == id_lezione)

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
    

# Inserisce la presenza
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

    new_presenza = PresenzeLezione(id_studente=studente.id, id_lezione=id_lezione)
    
    try:
        sessionStudenti.add(new_presenza)
        sessionStudenti.commit()
    except Exception as e:
        sessionStudenti.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore inserimento lezione' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200


# Agguinge l'iscrizione
@prog_corsi.route('/corso/<id_corso>/programmazione_corso/<id_prog>/iscrizioni', methods=['POST'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def add_iscrizione(user, id_corso, id_prog):
    if request.form.get('id_studente') is None:
        return jsonify({'error': True, 'errormessage': 'Dati mancanti'}), 404
    
    studente = sessionStudenti.query(Studente).filter(studente.id == request.form.get('id_studente')).first()
    if studente is None:
        return jsonify({'error': True, 'errormessage': 'Studente inesistente'}), 401
    
    if sessionStudenti.query(IscrizioniCorso).\
        join(ProgrammazioneCorso, ProgrammazioneCorso.id == IscrizioniCorso.id_programmazione_corso).\
        filter(IscrizioniCorso.id_studente == studente.id and ProgrammazioneCorso.id == id_prog).count() != 0:
        return jsonify({'error': True, 'errormessage': 'Studente già iscritto al corso'}), 401
    
    prog_corso = sessionStudenti.query(ProgrammazioneCorso).filter(ProgrammazioneCorso.id == id_prog).first() 
    in_presenza = None

    #e' dello studente questo, setta la variabile in base alla scelta, se duale e non sceglie nulla lo mette di default in presenza
    if prog_corso.modalità == 'duale':
        if request.form.get('inPresenza') is not None:
            in_presenza = request.form.get('inPresenza')
        else: 
            in_presenza = True
    elif prog_corso.modalità == 'presenza':
        in_presenza = True
        
    num_iscritti = sessionStudenti.query(IscrizioniCorso).filter(IscrizioniCorso.id_programmazione_corso == id_prog).count()
    capienza_aula_piu_piccola = sessionStudenti.query(Aula.capienza).\
        join(ProgrammazioneLezioni, ProgrammazioneLezioni.id_aula == Aula.id).\
        filter(ProgrammazioneLezioni.id_programmazione_corso == prog_corso.id).\
        order_by(Aula.capienza).limit(1).first()
        
    #si puo' indicare un limite di iscrizioni, se non e' indicato viene scelto come limite la capienza dell'aula piu' piccola
    #nota: ogni lezione ha una sola aula
    if prog_corso.modalità == 'duale' or prog_corso.modalità == 'presenza':
        if (prog_corso.limite_iscrizioni is not None and num_iscritti >= prog_corso.limite_iscrizioni) \
            or (num_iscritti >= capienza_aula_piu_piccola):
            return jsonify({'error': True, 'errormessage': 'Limite iscrizioni raggiunto.'}), 401
    
    new_iscrizione = IscrizioniCorso(id_studente=studente.id,
                                     id_programmazione_corso=prog_corso.id,
                                     inPresenza=in_presenza)
    
    try:
        sessionStudenti.add(new_iscrizione)
        sessionStudenti.commit()
    except Exception as e:
        sessionStudenti.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore inserimento iscrizione' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200


@prog_corsi.route('/corso/<id_corso>/programmazione_corso/<id_prog>/iscrizioni', methods=['GET'])
@token_required(restrict_to_roles=['amministratore', 'docente'])
def get_iscrizioni(user, id_corso, id_prog):
    skip = request.args('skip')
    limit = request.args('limit')
    inPresenza = request.args('inPresenza')
    name = request.args('nome')
    lastname = request.args('cognome')

    iscrizioni = sessionDocenti.query(Utente.id, Utente.nome, Utente.cognome, IscrizioniCorso.inPresenza).\
        join(Studente, Utente.id == Studente.id).\
        join(IscrizioniCorso, Studente.id == IscrizioniCorso.id).\
        filter(IscrizioniCorso.id_programmazione_corso == id_prog).\
        order_by(Utente.cognome, Utente.nome)

    if inPresenza is not None:
        iscrizioni = iscrizioni.filter(IscrizioniCorso.inPresenza == inPresenza)
    if name is not None:
        iscrizioni = iscrizioni.filter(Utente.nome.like('%' + name + '%'))
    if lastname is not None:
        iscrizioni = iscrizioni.filter(Utente.cognome.like('%' + lastname + '%'))
    if skip is not None:
        iscrizioni = iscrizioni.offset(skip)
    if limit is not None:
        iscrizioni = iscrizioni.limit(limit)

    if iscrizioni is None:
        return jsonify({'error': True, 'errormessage': 'Nessuno studente si è iscritto a quel programma del corso'}), 404
    else:
        return jsonify(json.loads(json.dumps([dict(studente._mapping) for studente in iscrizioni]))), 200


# TODO: è corretto lasciare l'id dello studente nella route, visto che poi verrà utilizzato per eliminarlo?
# Esempio: potrei accedere come studente e poi inserire degli id di studenti per cancellarli da un corso, semplicemente
# cambiando l'id dalla route.   Sembrerebbe non essere così tanto sicuro (stesso vale per la delete in corsi.py)
@prog_corsi.route('/corso/<id_corso>/programmazione_corso/<id_prog>/iscrizioni/<id_studente>', methods=['DELETE'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def remove_subscription(user, id_corso, id_prog, id_studente):
    try:
        sessionStudenti.delete(IscrizioniCorso(id_studente = id_studente, id_programmazione_corso = id_prog))
        sessionStudenti.commit()
    except Exception as e:
        sessionStudenti.rollback()
        return jsonify({'error': True, 'errormessage': 'Impossibile eliminare l\'iscrizione'}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200