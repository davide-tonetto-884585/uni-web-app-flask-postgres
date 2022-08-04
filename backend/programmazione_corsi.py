from datetime import date
import json
from flask import Blueprint, jsonify, request
from sqlalchemy import Date, Time, cast

from . import PreLoginSession, SessionDocenti, SessionAmministratori, SessionStudenti
from .marshmallow_models import ProgrammazioneCorsoSchema, ProgrammazioneLezioniSchema, CorsoSchema
from .auth import token_required
from .models import Docente, DocenteCorso, Utente, ProgrammazioneCorso, ProgrammazioneLezioni, PresenzeLezione, Studente, IscrizioniCorso, Aula, Corso

prog_corsi = Blueprint('programmazione_corsi', __name__)

""" sessionDocenti = SessionDocenti()
preLoginSession = PreLoginSession()
sessionAmministratori = SessionAmministratori()
sessionStudenti = SessionStudenti() """

programmazione_corsi_schema = ProgrammazioneCorsoSchema(many=True)
programmazione_corso_schema = ProgrammazioneCorsoSchema()
programmazione_lezioni_schema = ProgrammazioneLezioniSchema(many=True)
programmazione_lezione_schema = ProgrammazioneLezioniSchema()
corsi_schema = CorsoSchema(many=True)


# aggiunge una programmazione del corso indicato nella route
@prog_corsi.route('/corsi/<id>/programmazione_corso', methods=['POST'])
# ruoli che possono eseguire questa funzione
@token_required(restrict_to_roles=['amministratore', 'docente'])
def add_prog_corso(user, id):
    with SessionDocenti() as sessionDocenti:
        sessionDocenti.begin()

        # query per reperire tutti i docenti di un corso
        if 'amministratore' not in user['roles']:
            try:
                docenti = sessionDocenti.\
                    query(Docente.id).\
                    join(Utente, Utente.id == Docente.id).\
                    join(DocenteCorso, DocenteCorso.id_docente == Docente.id).\
                    filter(DocenteCorso.id_corso == id).all()
            except Exception as e:
                return jsonify({'error': True, 'errormessage': 'Errore nel reperire docenti del corso: ' + str(e)}), 500

            # controllo che il docente sia nei docenti che detiene il corso
            if ((user['id'],) not in docenti):
                return jsonify({'error': True, 'errormessage': 'Non sei autorizzato a programmare un corso a te non appartenente.'}), 401

        # controllo che i campi obbligatori siano stati inseriti nel form
        if request.form.get('modalita') is None or request.form.get('password_certificato') is None:
            return jsonify({'error': True, 'errormessage': 'Dati mancanti'}), 400

        limite_iscrizioni = None if request.form.get(
            'limite_iscrizioni') == 'null' else request.form.get('limite_iscrizioni')

        # creazione del nuovo oggetto da inserire
        new_prog_corso = ProgrammazioneCorso(modalita=request.form.get('modalita'),
                                             limite_iscrizioni=limite_iscrizioni,
                                             password_certificato=request.form.get(
            'password_certificato'),
            id_corso=id)

        # prova di inserimento della nuova programmazione del corso
        try:
            sessionDocenti.add(new_prog_corso)
            sessionDocenti.commit()
        except Exception as e:
            sessionDocenti.rollback()
            return jsonify({'error': True, 'errormessage': 'Errore inserimento programmazione corso' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': '', 'id': new_prog_corso.id}), 200


@prog_corsi.route('/corsi/<id_corso>/programmazione_corso/<id_prog_corso>', methods=['PUT'])
# ruoli che possono eseguire questa funzione
@token_required(restrict_to_roles=['amministratore', 'docente'])
def modify_prog_corso(user, id_corso, id_prog_corso):
    with SessionAmministratori() as sessionAmministratori:
        sessionAmministratori.begin()

        # query per reperire tutti i docenti di un corso
        if 'amministratore' not in user['roles']:
            try:
                docenti = sessionAmministratori.\
                    query(Docente.id).\
                    join(Utente, Utente.id == Docente.id).\
                    join(DocenteCorso, DocenteCorso.id_docente == Docente.id).\
                    filter(DocenteCorso.id_corso == id_corso).all()
            except Exception as e:
                return jsonify({'error': True, 'errormessage': 'Errore nel reperire docenti del corso: ' + str(e)}), 500

            # controllo che il docente sia nei docenti che detiene il corso
            if ((user['id'],) not in docenti):
                return jsonify({'error': True, 'errormessage': 'Non sei autorizzato a programmare un corso a te non appartenente.'}), 401

        prog_corso = sessionAmministratori.query(ProgrammazioneCorso).filter(
            ProgrammazioneCorso.id == id_prog_corso).first()

        if request.form.get('modalita') is not None:
            prog_corso.modalita = request.form.get('modalita')

        if request.form.get('password_certificato') is not None:
            prog_corso.password_certificato = request.form.get(
                'password_certificato')

        prog_corso.limite_iscrizioni = None if request.form.get(
            'limite_iscrizioni') == 'null' else request.form.get('limite_iscrizioni')

        # prova di inserimento della nuova programmazione del corso
        try:
            sessionAmministratori.commit()
        except Exception as e:
            sessionAmministratori.rollback()
            return jsonify({'error': True, 'errormessage': 'Errore aggiornamento programmazione corso' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200


# ritorna la programmazione di un corso specifico in base all'id
@prog_corsi.route('/corsi/<id>/programmazione_corso', methods=['GET'])
def get_progs_corso(id):
    with PreLoginSession() as preLoginSession, preLoginSession.begin():

        # Parametri del form
        skip = request.args.get('skip')
        limit = request.args.get('limit')
        modality = request.args.get('modalita')
        subscriptions_limit = request.args.get('limite_iscrizioni')
        current = request.args.get('in_corso')

        try:
            # Query per recuperare tutte le programmazioni del corso
            progs_corso = preLoginSession.query(ProgrammazioneCorso).filter(
                ProgrammazioneCorso.id_corso == id)

            # Filtri per specializzare la ricerca e/o la visualizzazione delle programmazioni del corso
            if modality is not None:
                progs_corso = progs_corso.filter(
                    ProgrammazioneCorso.modalita == modality)
            if subscriptions_limit is not None:
                progs_corso = progs_corso.filter(
                    ProgrammazioneCorso.limite_iscrizioni == subscriptions_limit)
            if current is not None and current != 'false':
                progs_corso = progs_corso.join(ProgrammazioneLezioni, ProgrammazioneLezioni.id_programmazione_corso == ProgrammazioneCorso.id).\
                    filter(ProgrammazioneLezioni.data >= date.today()).\
                    group_by(ProgrammazioneCorso.id)
            if skip is not None:
                progs_corso = progs_corso.offset(skip)
            if limit is not None:
                progs_corso = progs_corso.limit(limit)

            progs_corso = progs_corso.all()

        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Errore nel reperire programmazione corso: ' + str(e)}), 500

        return jsonify(programmazione_corsi_schema.dump(progs_corso)), 200


# ritorna una programmazione specifica di un corso specifico in base al loro id
@prog_corsi.route('/corsi/<id_corso>/programmazione_corso/<id_prog>', methods=['GET'])
def get_prog_corso(id_corso, id_prog):
    with PreLoginSession() as preLoginSession, preLoginSession.begin():

        # prova a recuperare la programmazione del corso
        try:
            prog_corso = preLoginSession.query(ProgrammazioneCorso).\
                filter(ProgrammazioneCorso.id_corso == id_corso,
                       ProgrammazioneCorso.id == id_prog).first()

        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Errore nel reperire il corso: ' + str(e)}), 500

        if prog_corso is None:
            # Se non trova alcuna programmazione, ritorna uno status code 404
            return jsonify({'error': True, 'errormessage': 'Programmazione del corso inesistente'}), 404
        else:
            # Per ogni entry, aggiunge il limite di iscrizione sulla base dell'aula più piccola
            if prog_corso.modalita == 'presenza' or prog_corso.modalita == 'duale' and prog_corso.limite_iscrizioni is None:
                prog_corso.limite_iscrizioni = preLoginSession.query(Aula.capienza).\
                    join(ProgrammazioneLezioni, ProgrammazioneLezioni.id_aula == Aula.id).\
                    filter(ProgrammazioneLezioni.id_programmazione_corso == prog_corso.id).\
                    order_by(Aula.capienza).limit(1).first()

            return jsonify(programmazione_corso_schema.dump(prog_corso)), 200


# ritorna le lezioni di una programmazione specifica di un corso specifico in base al loro id
@prog_corsi.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/lezioni', methods=['GET'])
def get_lezioni_progs_corso(id_corso, id_prog):
    with PreLoginSession() as preLoginSession, preLoginSession.begin():

        # Parametri del form
        skip = request.args.get('skip')
        limit = request.args.get('limit')
        date = request.args.get('date')
        start_time = request.args.get('start_time')
        finish_time = request.args.get('finish_time')

        try:
            # Query per recuperare tutte le programmazioni delle lezioni
            progs_lezioni = preLoginSession.query(ProgrammazioneLezioni).filter(
                ProgrammazioneLezioni.id_programmazione_corso == id_prog)

            # Filtri per specializzare la ricerca e/o la visualizzazione delle programmazioni delle lezioni
            if date is not None:
                progs_lezioni = progs_lezioni.filter(
                    cast(ProgrammazioneLezioni.data, Date) == cast(date, Date))
            if start_time is not None:
                progs_lezioni = progs_lezioni.filter(
                    cast(ProgrammazioneLezioni.orario_inizio, Time) == cast(start_time, Time))
            if finish_time is not None:
                progs_lezioni = progs_lezioni.filter(
                    cast(ProgrammazioneLezioni.orario_fine, Time) == cast(finish_time, Time))
            if skip is not None:
                progs_lezioni = progs_lezioni.offset(skip)
            if limit is not None:
                progs_lezioni = progs_lezioni.limit(limit)

            progs_lezioni = progs_lezioni.all()

        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Errore nel reperimento delle lezioni: ' + str(e)}), 500

        return jsonify(programmazione_lezioni_schema.dump(progs_lezioni)), 200


# aggiunge una nuova lezione
@prog_corsi.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/lezioni', methods=['POST'])
# ruoli che possono eseguire questa funzione
@token_required(restrict_to_roles=['amministratore', 'docente'])
def add_lezione_prog_corso(user, id_corso, id_prog):
    with SessionAmministratori() as sessionAmministratori:
        sessionAmministratori.begin()

        # Parametri del form
        date = request.form.get('data')
        start_time = request.form.get('orario_inizio')
        finish_time = request.form.get('orario_fine')
        link_virtual_class = request.form.get('link_stanza_virtuale')
        passcode_virtual_class = request.form.get('passcode_stanza_virtuale')
        presence_code = request.form.get('codice_verifica_presenza')
        id_aula = request.form.get('id_aula')

        # query per reperire tutti i docenti di un corso
        if 'amministratore' not in user['roles']:
            try:
                docenti = sessionAmministratori.\
                    query(Docente.id).\
                    join(Utente, Utente.id == Docente.id).\
                    join(DocenteCorso, DocenteCorso.id_docente == Docente.id).\
                    filter(DocenteCorso.id_corso == id_corso).all()
            except Exception as e:
                return jsonify({'error': True, 'errormessage': 'Errore nel reperimento dei docenti del corso: ' + str(e)}), 500

            # controllo che il docente sia nei docenti che detiene il corso
            if (user['id'], ) not in docenti:
                return jsonify({'error': True, 'errormessage': 'Errore, non puoi programmare una lezione di un corso a te non appartenente.'}), 401

        # controllo che i campi obbligatori siano stati inseriti nel form
        if date is None:
            return jsonify({'error': True, 'errormessage': 'Data mancante'}), 400

        if start_time is None:
            return jsonify({'error': True, 'errormessage': 'Orario inizio mancante'}), 400

        if finish_time is None:
            return jsonify({'error': True, 'errormessage': 'Orario fine mancante'}), 400

        # controllo che i link e la password siano necessari nel caso siano online o duale
        prog_corso = sessionAmministratori.query(ProgrammazioneCorso).filter(
            ProgrammazioneCorso.id == id_prog).first()
        if prog_corso.modalita == 'online' or prog_corso.modalita == 'duale':
            if link_virtual_class is None:
                return jsonify({'error': True, 'errormessage': 'Link stanza virtuale mancante'}), 400

            if passcode_virtual_class is None:
                return jsonify({'error': True, 'errormessage': 'Passcode stanza virtuale mancante'}), 400

        if presence_code is None:
            return jsonify({'error': True, 'errormessage': 'Codice verifica presenza mancante'}), 400

        # Controlla che la lezione non vada a sovrapporsi ad un'altra
        if sessionAmministratori.query(ProgrammazioneLezioni).\
                join(ProgrammazioneCorso, ProgrammazioneLezioni.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(
                    ProgrammazioneLezioni.data == date,
                    ProgrammazioneLezioni.orario_inizio >= start_time,
                    ProgrammazioneLezioni.orario_inizio <= finish_time,
                    ProgrammazioneCorso.id == id_prog
        ).count() > 1:
            return jsonify({'error': True, 'errormessage': 'Lezione sovrapposta ad un\'altra'}), 409

        # creazione nuovo oggetto con i campi da inserire nella tabella
        new_lezione = ProgrammazioneLezioni(data=date, orario_inizio=start_time, orario_fine=finish_time,
                                            link_stanza_virtuale=link_virtual_class, passcode_stanza_virtuale=passcode_virtual_class,
                                            codice_verifica_presenza=presence_code, id_programmazione_corso=id_prog, id_aula=id_aula)

        # prova inserimento della nuova lezione
        try:
            sessionAmministratori.add(new_lezione)
            sessionAmministratori.commit()
        except Exception as e:
            sessionAmministratori.rollback()
            return jsonify({'error': True, 'errormessage': 'Errore nell\'inserimento della lezione' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200


@prog_corsi.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/lezioni/<id_lezione>', methods=['PUT'])
# ruoli che possono eseguire questa funzione
@token_required(restrict_to_roles=['amministratore', 'docente'])
def modify_lezione_prog_corso(user, id_corso, id_prog, id_lezione):
    with SessionDocenti() as sessionDocenti:
        sessionDocenti.begin()

        # Parametri del form
        date = request.form.get('data')
        start_time = request.form.get('orario_inizio')
        finish_time = request.form.get('orario_fine')
        link_virtual_class = request.form.get('link_stanza_virtuale')
        passcode_virtual_class = request.form.get('passcode_stanza_virtuale')
        presence_code = request.form.get('codice_verifica_presenza')
        id_aula = request.form.get('id_aula')

        # query per reperire tutti i docenti di un corso
        if 'amministratore' not in user['roles']:
            try:
                docenti = sessionDocenti.\
                    query(Docente.id).\
                    join(Utente, Utente.id == Docente.id).\
                    join(DocenteCorso, DocenteCorso.id_docente == Docente.id).\
                    filter(DocenteCorso.id_corso == id_corso).all()
            except Exception as e:
                return jsonify({'error': True, 'errormessage': 'Errore nel reperimento dei docenti del corso: ' + str(e)}), 500

            # controllo che il docente sia nei docenti che detiene il corso
            if (user['id'], ) not in docenti:
                return jsonify({'error': True, 'errormessage': 'Errore, non puoi programmare una lezione di un corso a te non appartenente.'}), 401

        # controllo che i campi obbligatori siano stati inseriti nel form
        if date is None:
            return jsonify({'error': True, 'errormessage': 'Data mancante'}), 400

        if start_time is None:
            return jsonify({'error': True, 'errormessage': 'Orario inizio mancante'}), 400

        if finish_time is None:
            return jsonify({'error': True, 'errormessage': 'Orario fine mancante'}), 400

        # controllo che i link e la password siano necessari nel caso siano online o duale
        prog_corso = sessionDocenti.query(ProgrammazioneCorso).filter(
            ProgrammazioneCorso.id == id_prog).first()
        if prog_corso.modalita == 'online' or prog_corso.modalita == 'duale':
            if link_virtual_class is None:
                return jsonify({'error': True, 'errormessage': 'Link stanza virtuale mancante'}), 400

            if passcode_virtual_class is None:
                return jsonify({'error': True, 'errormessage': 'Passcode stanza virtuale mancante'}), 400

        if presence_code is None:
            return jsonify({'error': True, 'errormessage': 'Codice verifica presenza mancante'}), 400

        # Controlla che la lezione non vada a sovrapporsi ad un'altra
        if sessionDocenti.query(ProgrammazioneLezioni).\
                join(ProgrammazioneCorso, ProgrammazioneLezioni.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(
                    ProgrammazioneLezioni.data == date,
                    ProgrammazioneLezioni.orario_inizio >= start_time,
                    ProgrammazioneLezioni.orario_inizio <= finish_time,
                    ProgrammazioneCorso.id == id_prog
        ).count() > 1:
            return jsonify({'error': True, 'errormessage': 'Lezione sovrapposta ad un\'altra'}), 409

        # creazione nuovo oggetto con i campi da inserire nella tabella
        lezione = sessionDocenti.query(ProgrammazioneLezioni).filter(
            ProgrammazioneLezioni.id == id_lezione).first()

        lezione.data = date
        lezione.orario_inizio = start_time
        lezione.orario_fine = finish_time
        lezione.link_stanza_virtuale = None if link_virtual_class == 'null' else link_virtual_class
        lezione.passcode_stanza_virtuale = None if passcode_virtual_class == 'null' else passcode_virtual_class
        lezione.codice_verifica_presenza = presence_code
        lezione.id_aula = id_aula

        # prova inserimento della nuova lezione
        try:
            sessionDocenti.commit()
        except Exception as e:
            sessionDocenti.rollback()
            return jsonify({'error': True, 'errormessage': 'Errore nell\'aggiornamento della lezione ' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200


# ritorna una lezione specifica di una programmazione del corso specifica di un corso specifico in base all'id
@prog_corsi.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/lezioni/<id_lezione>', methods=['GET'])
def get_lezione_prog_corso(id_corso, id_prog, id_lezione):
    with PreLoginSession() as preLoginSession, preLoginSession.begin():

        # prova a recuperare la programmazione della lezione
        try:
            prog_lezione = preLoginSession.query(ProgrammazioneLezioni).filter(
                ProgrammazioneLezioni.id_programmazione_corso == id_prog, ProgrammazioneLezioni.id == id_lezione).first()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Errore nel reperimento della lezione: ' + str(e)}), 500

        if prog_lezione is None:
            # Se non trova alcuna programmazione, ritorna uno status code 404
            return jsonify({'error': True, 'errormessage': 'Programmazione della lezione inesistente'}), 404
        else:
            return jsonify(programmazione_lezione_schema.dump(prog_lezione)), 200


# ritorna le presenze di una specifica lezione
@prog_corsi.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/lezioni/<id_lezione>/presenze', methods=['GET'])
# ruoli che possono eseguire questa funzione
@token_required(restrict_to_roles=['amministratore', 'docente'])
def get_presenze_lezione(user, id_corso, id_prog, id_lezione):
    with SessionDocenti() as sessionDocenti, sessionDocenti.begin():

        # Parametri del form
        skip = request.args.get('skip')
        limit = request.args.get('limit')
        name = request.args.get('name')
        lastname = request.args.get('lastname')

        try:
            # query per reperire le presenze degli studenti in una lezione
            presenze = sessionDocenti.query(Utente.id, Utente.nome, Utente.cognome).\
                filter(Utente.id == PresenzeLezione.id_studente,
                       PresenzeLezione.id_programmazione_lezioni == id_lezione)

            # Filtri per specializzare la ricerca e/o la visualizzazione delle presenze
            if name is not None:
                presenze = presenze.filter(Utente.nome.like('%' + name + '%'))
            if lastname is not None:
                presenze = presenze.filter(
                    Utente.cognome.like('%' + lastname + '%'))
            if skip is not None:
                presenze = presenze.offset(skip)
            if limit is not None:
                presenze = presenze.limit(limit)

            presenze = presenze.all()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Errore durante il reperimento delle presenze: ' + str(e)}), 500

        return jsonify(json.loads(json.dumps([dict(studente._mapping) for studente in presenze]))), 200


@prog_corsi.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/lezioni/<id_lezione>/presenze', methods=['POST'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def add_presenza(user, id_corso, id_prog, id_lezione):
    with SessionStudenti() as sessionStudenti:
        sessionStudenti.begin()

        if request.form.get('id_studente') is None or request.form.get('codice_verifica_presenza') is None:
            return jsonify({'error': True, 'errormessage': 'Dati mancanti'}), 400

        # Controlla che lo studente esista
        studente = sessionStudenti.query(Studente).filter(
            studente.id == request.form.get('id_studente')).first()
        if studente is None:
            return jsonify({'error': True, 'errormessage': 'Studente inesistente'}), 404

        if ('studente' in user['roles'] and user['id'] != int(request.form.get('id_studente'))):
            return jsonify({'error': True, 'errormessage': 'Permesso negato'}), 400

        # Controlla che lo studente sia iscritto al corso
        if sessionStudenti.query(IscrizioniCorso).\
                join(ProgrammazioneCorso, ProgrammazioneCorso.id == IscrizioniCorso.id_programmazione_corso).\
                filter(IscrizioniCorso.id_studente == studente.id and ProgrammazioneCorso.id == id_prog).count() == 0:

            return jsonify({'error': True, 'errormessage': 'Studente non iscritto al corso'}), 404

        # Controlla che il codice di verifica (per la presenza) sia valido
        lezione = sessionStudenti.query(ProgrammazioneLezioni).filter(
            ProgrammazioneLezioni.id == id_lezione).first()
        if lezione.codice_verifica_presenza != request.form.get('codice_verifica_presenza'):
            return jsonify({'error': True, 'errormessage': 'Codice verifica non valido'}), 400

        new_presenza = PresenzeLezione(id_studente=studente.id,
                                       id_programmazione_lezioni=id_lezione)

        try:
            sessionStudenti.add(new_presenza)
            sessionStudenti.commit()
        except Exception as e:
            sessionStudenti.rollback()
            return jsonify({'error': True, 'errormessage': 'Errore nell\'inserimento lezione' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200


@prog_corsi.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/iscrizioni', methods=['POST'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def add_iscrizione(user, id_corso, id_prog):
    with SessionStudenti() as sessionStudenti:
        sessionStudenti.begin()

        if request.form.get('id_studente') is None:
            return jsonify({'error': True, 'errormessage': 'Dati mancanti'}), 400

        # Controlla che lo studente esista
        studente = sessionStudenti.query(Studente).filter(
            Studente.id == request.form.get('id_studente')).first()
        if studente is None:
            return jsonify({'error': True, 'errormessage': 'Studente inesistente'}), 404

        if ('studente' in user['roles'] and user['id'] != int(request.form.get('id_studente'))):
            return jsonify({'error': True, 'errormessage': 'Non puoi iscrivere altri studenti al corso'}), 400

        # Controlla che lo studente non sia già iscritto al corso
        if sessionStudenti.query(IscrizioniCorso).\
                join(ProgrammazioneCorso, ProgrammazioneCorso.id == IscrizioniCorso.id_programmazione_corso).\
                filter(IscrizioniCorso.id_studente == studente.id and ProgrammazioneCorso.id == id_prog).count() != 0:

            return jsonify({'error': True, 'errormessage': 'Studente già iscritto al corso'}), 409

        prog_corso = sessionStudenti.query(ProgrammazioneCorso).filter(
            ProgrammazioneCorso.id == id_prog).first()
        in_presenza = None

        # Se lo studente ha scelto "duale" e non sceglie se in presenza od online, allora lo setta a True di default
        if prog_corso.modalita == 'duale':
            if request.form.get('inPresenza') is not None:
                in_presenza = request.form.get('inPresenza')
            else:
                in_presenza = True
        elif prog_corso.modalita == 'presenza':
            in_presenza = True

        # Recupera il numero di iscritti
        num_iscritti = sessionStudenti.query(IscrizioniCorso).filter(
            IscrizioniCorso.id_programmazione_corso == id_prog).count()

        # Recupera la capienza dell'aula più piccola
        capienza_aula_piu_piccola = sessionStudenti.query(Aula.capienza).\
            join(ProgrammazioneLezioni, ProgrammazioneLezioni.id_aula == Aula.id).\
            filter(ProgrammazioneLezioni.id_programmazione_corso == prog_corso.id).\
            order_by(Aula.capienza).limit(1).first()[0]

        # Si puo' indicare un limite di iscrizioni, se non e' indicato viene scelto come limite la capienza dell'aula piu' piccola
        # Nota: ogni lezione ha una sola aula
        if prog_corso.modalita == 'duale' or prog_corso.modalita == 'presenza':
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


@prog_corsi.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/iscrizioni', methods=['GET'])
# @token_required(restrict_to_roles=['amministratore', 'docente'])
def get_iscrizioni(id_corso, id_prog):
    with PreLoginSession() as preLoginSession, preLoginSession.begin():

        # Campi del form
        skip = request.args.get('skip')
        limit = request.args.get('limit')
        inPresenza = request.args.get('inPresenza')
        name = request.args.get('nome')
        lastname = request.args.get('cognome')

        try:
            # Query per recurepare le iscrizioni dal programma del corso
            iscrizioni = preLoginSession.query(Utente.id, Utente.nome, Utente.cognome, IscrizioniCorso.inPresenza).\
                join(Studente, Utente.id == Studente.id).\
                join(IscrizioniCorso, Studente.id == IscrizioniCorso.id_studente).\
                filter(IscrizioniCorso.id_programmazione_corso == id_prog).\
                order_by(Utente.cognome, Utente.nome)

            # Filtri per migliorare la ricerca e/o visualizzazione
            if inPresenza is not None:
                iscrizioni = iscrizioni.filter(
                    IscrizioniCorso.inPresenza == inPresenza)
            if name is not None:
                iscrizioni = iscrizioni.filter(
                    Utente.nome.like('%' + name + '%'))
            if lastname is not None:
                iscrizioni = iscrizioni.filter(
                    Utente.cognome.like('%' + lastname + '%'))
            if skip is not None:
                iscrizioni = iscrizioni.offset(skip)
            if limit is not None:
                iscrizioni = iscrizioni.limit(limit)

            iscrizioni = iscrizioni.all()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Errore durante il reperimento delle iscrizioni del corso: ' + str(e)}), 500

        return jsonify(json.loads(json.dumps([dict(studente._mapping) for studente in iscrizioni]))), 200


@prog_corsi.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/iscrizioni/<id_studente>', methods=['DELETE'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def remove_subscription(user, id_corso, id_prog, id_studente):
    with SessionStudenti() as sessionStudenti:
        sessionStudenti.begin()

        # Controlla che lo studente non stia cercando di eliminare altri studenti al di fuori di sé stesso
        if ('studente' in user['roles'] and user['id'] != int(id_studente)):
            return jsonify({'error': True, 'errormessage': 'Non sei autorizzato a eliminare uno studente dal corso al di fuori di te stesso'}), 400

        # Controlla che il docente non stia cercando di eliminare uno studente da un corso che non gli appartiene
        if ('docente' in user['roles'] and 'amministratore' not in user['roles']):
            if (sessionStudenti.query(DocenteCorso.id_docente).
                    filter(DocenteCorso.id_corso == id_corso, DocenteCorso.id_docente == user['id']).count() == 0):

                return jsonify({'error': True, 'errormessage': 'Non sei autorizzato a eliminare uno studente da un corso che non ti appartiene'}), 401

        try:
            iscrizione = sessionStudenti.query(IscrizioniCorso).\
                filter(IscrizioniCorso.id_studente == id_studente,
                       IscrizioniCorso.id_programmazione_corso == id_prog).first()

            sessionStudenti.delete(iscrizione)
            sessionStudenti.commit()
        except Exception as e:
            sessionStudenti.rollback()
            return jsonify({'error': True, 'errormessage': 'Impossibile eliminare l\'iscrizione: ' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200


@prog_corsi.route('/utenti/studenti/<id>/iscrizioni', methods=['GET'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def get_student_inscriptions(user, id):
    with SessionStudenti() as sessionStudenti, sessionStudenti.begin():

        if 'studente' in user['roles'] and user['id'] != int(id):
            return jsonify({'error': True, 'errormessage': 'Non puoi vedere le iscrizioni di altri studenti'}), 401

        try:
            inscriptions = sessionStudenti.query(Corso.id, Corso.titolo, Corso.descrizione, Corso.lingua, Corso.immagine_copertina, Corso.file_certificato, Corso.abilitato,
                                                 ProgrammazioneCorso.id.label('id_programmazione_corso'))\
                .join(ProgrammazioneCorso, Corso.id == ProgrammazioneCorso.id_corso)\
                .join(IscrizioniCorso, IscrizioniCorso.id_programmazione_corso == ProgrammazioneCorso.id)\
                .filter(IscrizioniCorso.id_studente == id).all()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Errore nel reperire le iscrizioni dello studente: ' + str(e)}), 500

        return jsonify(json.loads(json.dumps([dict(inscription._mapping) for inscription in inscriptions]))), 200
