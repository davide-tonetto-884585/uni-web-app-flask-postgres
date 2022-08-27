from flask import Blueprint, jsonify, request
from sqlalchemy import Date, Time, cast

from .. import PreLoginSession, SessionDocenti, SessionAmministratori, SessionStudenti
from ..model.marshmallow_models import ProgrammazioneCorsoSchema, ProgrammazioneLezioniSchema, CorsoSchema
from .auth import token_required
from ..model.models import Docente, DocenteCorso, Utente, ProgrammazioneCorso, ProgrammazioneLezioni, PresenzeLezione, Studente, IscrizioniCorso, Aula, Corso

lezioni = Blueprint('lezioni', __name__)

programmazione_corsi_schema = ProgrammazioneCorsoSchema(many=True)
programmazione_corso_schema = ProgrammazioneCorsoSchema()
programmazione_lezioni_schema = ProgrammazioneLezioniSchema(many=True)
programmazione_lezione_schema = ProgrammazioneLezioniSchema()
corsi_schema = CorsoSchema(many=True)


# ritorna le lezioni di una programmazione specifica di un corso specifico in base al loro id
@lezioni.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/lezioni', methods=['GET'])
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

            progs_lezioni = progs_lezioni.order_by(ProgrammazioneLezioni.data)
            progs_lezioni = progs_lezioni.all()

        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Errore nel reperimento delle lezioni: ' + str(e)}), 500

        return jsonify(programmazione_lezioni_schema.dump(progs_lezioni)), 200


# aggiunge una nuova lezione
@lezioni.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/lezioni', methods=['POST'])
# ruoli che possono eseguire questa funzione
@token_required(restrict_to_roles=['amministratore', 'docente'])
def add_lezione_prog_corso(user, id_corso, id_prog):
    with SessionAmministratori() as sessionAmministratori:
        sessionAmministratori.begin()

        # Parametri del form
        date = request.form.get('data')
        start_time = request.form.get('orario_inizio')
        finish_time = request.form.get('orario_fine')
        link_virtual_class = None if request.form.get(
            'link_stanza_virtuale') == 'null' else request.form.get('link_stanza_virtuale')
        passcode_virtual_class = None if request.form.get(
            'passcode_stanza_virtuale') == 'null' else request.form.get('passcode_stanza_virtuale')
        presence_code = request.form.get('codice_verifica_presenza')
        id_aula = None if request.form.get(
            'id_aula') == 'null' else request.form.get('id_aula')

        # query per reperire tutti i docenti di un corso
        if 'amministratore' not in user['roles']:
            try:
                docenti = sessionAmministratori.\
                    query(Docente.id).\
                    join(Utente, Utente.id == Docente.id).\
                    join(DocenteCorso, DocenteCorso.id_docente == Docente.id).\
                    filter(DocenteCorso.id_corso == id_corso).all()
            except Exception as e:
                return jsonify({'error': True, 'errormessage': 'Error in finding the course teachers: ' + str(e)}), 500

            # controllo che il docente sia nei docenti che detiene il corso
            if (user['id'], ) not in docenti:
                return jsonify({'error': True, 'errormessage': 'Error, you cannot schedule a lesson of a course that does not belong to you.'}), 401

        # controllo che i campi obbligatori siano stati inseriti nel form
        if date is None:
            return jsonify({'error': True, 'errormessage': 'Missing data'}), 400

        if start_time is None:
            return jsonify({'error': True, 'errormessage': 'Missing start time'}), 400

        if finish_time is None:
            return jsonify({'error': True, 'errormessage': 'Missing end time'}), 400

        # controllo che i link e la password siano necessari nel caso siano online o duale
        prog_corso = sessionAmministratori.query(ProgrammazioneCorso).filter(
            ProgrammazioneCorso.id == id_prog).first()
        if prog_corso.modalita == 'online' or prog_corso.modalita == 'duale':
            if link_virtual_class is None:
                return jsonify({'error': True, 'errormessage': 'Virtual room link missing'}), 400

        if presence_code is None:
            return jsonify({'error': True, 'errormessage': 'Missing presence check code'}), 400

        # Controlla che la lezione non vada a sovrapporsi ad un'altra
        if sessionAmministratori.query(ProgrammazioneLezioni).\
                join(ProgrammazioneCorso, ProgrammazioneLezioni.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(
                    ProgrammazioneLezioni.data == date,
                    ProgrammazioneLezioni.orario_fine >= start_time,
                    ProgrammazioneCorso.id == id_prog
        ).count() > 1:
            return jsonify({'error': True, 'errormessage': 'Lesson superimposed on another'}), 409

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
            return jsonify({'error': True, 'errormessage': 'Error in inserting the lesson' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200


@lezioni.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/lezioni/<id_lezione>', methods=['PUT'])
# ruoli che possono eseguire questa funzione
@token_required(restrict_to_roles=['amministratore', 'docente'])
def modify_lezione_prog_corso(user, id_corso, id_prog, id_lezione):
    with SessionDocenti() as sessionDocenti:
        sessionDocenti.begin()

        # Parametri del form
        date = request.form.get('data')
        start_time = request.form.get('orario_inizio')
        finish_time = request.form.get('orario_fine')
        link_virtual_class = None if request.form.get('link_stanza_virtuale') == 'null' or request.form.get('link_stanza_virtuale') == ''\
            else request.form.get('link_stanza_virtuale')
        passcode_virtual_class = None if request.form.get('passcode_stanza_virtuale') == 'null' or\
            request.form.get('passcode_stanza_virtuale') == '' else request.form.get('passcode_stanza_virtuale')
        presence_code = request.form.get('codice_verifica_presenza')
        id_aula = None if request.form.get('id_aula') == 'null' or request.form.get(
            'id_aula') == '' else request.form.get('id_aula')

        # query per reperire tutti i docenti di un corso
        if 'amministratore' not in user['roles']:
            try:
                docenti = sessionDocenti.\
                    query(Docente.id).\
                    join(Utente, Utente.id == Docente.id).\
                    join(DocenteCorso, DocenteCorso.id_docente == Docente.id).\
                    filter(DocenteCorso.id_corso == id_corso).all()
            except Exception as e:
                return jsonify({'error': True, 'errormessage': 'Error in finding the course teachers: ' + str(e)}), 500

            # controllo che il docente sia nei docenti che detiene il corso
            if (user['id'], ) not in docenti:
                return jsonify({'error': True, 'errormessage': 'Error, you cannot schedule a lesson of a course that does not belong to you.'}), 401

        # controllo che i campi obbligatori siano stati inseriti nel form
        if date is None:
            return jsonify({'error': True, 'errormessage': 'Missing date'}), 400

        if start_time is None:
            return jsonify({'error': True, 'errormessage': 'Missing start time'}), 400

        if finish_time is None:
            return jsonify({'error': True, 'errormessage': 'Missing end time'}), 400

        # controllo che i link e la password siano necessari nel caso siano online o duale
        prog_corso = sessionDocenti.query(ProgrammazioneCorso).filter(
            ProgrammazioneCorso.id == id_prog).first()
        if prog_corso.modalita == 'online' or prog_corso.modalita == 'duale':
            if link_virtual_class is None:
                return jsonify({'error': True, 'errormessage': 'Virtual room link missing'}), 400

        if presence_code is None:
            return jsonify({'error': True, 'errormessage': 'Missing presence check code'}), 400

        # Controlla che la lezione non vada a sovrapporsi ad un'altra
        if sessionDocenti.query(ProgrammazioneLezioni).\
                join(ProgrammazioneCorso, ProgrammazioneLezioni.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(
                    ProgrammazioneLezioni.data == date,
                    ProgrammazioneLezioni.orario_fine >= start_time,
                    ProgrammazioneCorso.id == id_prog
        ).count() > 1:
            return jsonify({'error': True, 'errormessage': 'Lesson superimposed on another'}), 409

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
            return jsonify({'error': True, 'errormessage': 'Error updating the lesson: ' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200


# ritorna una lezione specifica di una programmazione del corso specifica di un corso specifico in base all'id
@lezioni.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/lezioni/<id_lezione>', methods=['GET'])
def get_lezione_prog_corso(id_corso, id_prog, id_lezione):
    with PreLoginSession() as preLoginSession, preLoginSession.begin():

        # prova a recuperare la programmazione della lezione
        try:
            prog_lezione = preLoginSession.query(ProgrammazioneLezioni).filter(
                ProgrammazioneLezioni.id_programmazione_corso == id_prog, ProgrammazioneLezioni.id == id_lezione).first()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Error in retrieving the lesson: ' + str(e)}), 500

        if prog_lezione is None:
            # Se non trova alcuna programmazione, ritorna uno status code 404
            return jsonify({'error': True, 'errormessage': 'Lesson not found'}), 404
        else:
            return jsonify(programmazione_lezione_schema.dump(prog_lezione)), 200
