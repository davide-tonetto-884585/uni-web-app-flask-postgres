from datetime import date
import configparser
import json
from flask import Blueprint, jsonify, request, send_file

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
                return jsonify({'error': True, 'errormessage': 'Error in finding course teachers: ' + str(e)}), 500

            # controllo che il docente sia nei docenti che detiene il corso
            if ((user['id'],) not in docenti):
                return jsonify({'error': True, 'errormessage': 'You are not authorized to schedule a course that does not belong to you.'}), 401

        # controllo che i campi obbligatori siano stati inseriti nel form
        if request.form.get('modalita') is None or request.form.get('password_certificato') is None:
            return jsonify({'error': True, 'errormessage': 'Missing information'}), 400

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
            return jsonify({'error': True, 'errormessage': 'Course schedule entry error' + str(e)}), 500

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
                return jsonify({'error': True, 'errormessage': 'Error in finding course teachers: ' + str(e)}), 500

            # controllo che il docente sia nei docenti che detiene il corso
            if ((user['id'],) not in docenti):
                return jsonify({'error': True, 'errormessage': 'You are not authorized to schedule a course that does not belong to you.'}), 401

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
            return jsonify({'error': True, 'errormessage': 'Course schedule update error' + str(e)}), 500

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
        print(current)

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
            if current is not None:
                if current == 'false':
                    progs_corso = progs_corso.outerjoin(ProgrammazioneLezioni, ProgrammazioneCorso.id == ProgrammazioneLezioni.id_programmazione_corso).\
                        filter((ProgrammazioneLezioni.data >= date.today()) | (ProgrammazioneLezioni.data == None)).\
                        group_by(ProgrammazioneCorso.id)
                else:
                    progs_corso = progs_corso.join(ProgrammazioneLezioni, ProgrammazioneCorso.id == ProgrammazioneLezioni.id_programmazione_corso).\
                        filter(ProgrammazioneLezioni.data >= date.today()).\
                        group_by(ProgrammazioneCorso.id)
            if skip is not None:
                progs_corso = progs_corso.offset(skip)
            if limit is not None:
                progs_corso = progs_corso.limit(limit)

            progs_corso = progs_corso.all()

        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Error finding course schedule: ' + str(e)}), 500

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
            return jsonify({'error': True, 'errormessage': 'Error finding the course: ' + str(e)}), 500

        if prog_corso is None:
            # Se non trova alcuna programmazione, ritorna uno status code 404
            return jsonify({'error': True, 'errormessage': 'Course schedule not found'}), 404
        else:
            # Per ogni entry, aggiunge il limite di iscrizione sulla base dell'aula più piccola
            if prog_corso.modalita == 'presenza' or prog_corso.modalita == 'duale' and prog_corso.limite_iscrizioni is None:
                prog_corso.limite_iscrizioni = preLoginSession.query(Aula.capienza).\
                    join(ProgrammazioneLezioni, ProgrammazioneLezioni.id_aula == Aula.id).\
                    filter(ProgrammazioneLezioni.id_programmazione_corso == prog_corso.id).\
                    order_by(Aula.capienza).limit(1).first()

            return jsonify(programmazione_corso_schema.dump(prog_corso)), 200


@prog_corsi.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/certificato', methods=['GET'])
@token_required(restrict_to_roles=['studente'])
def downloadFile(user, id_corso, id_prog):
    with SessionStudenti() as sessionStudenti, sessionStudenti.begin():
        config = configparser.ConfigParser()
        config.read('global_settings.ini')
        
        corso = sessionStudenti.query(Corso).filter(
            Corso.id == id_corso).first()

        num_presenze = sessionStudenti.query(PresenzeLezione).\
            join(ProgrammazioneLezioni, ProgrammazioneLezioni.id == PresenzeLezione.id_programmazione_lezioni).\
            filter(ProgrammazioneLezioni.id_programmazione_corso == id_prog).\
            filter(PresenzeLezione.id_studente == user['id']).count()
            
        num_lezioni = sessionStudenti.query(ProgrammazioneLezioni).\
            filter(ProgrammazioneLezioni.id_programmazione_corso == id_prog).count()
            
        if (num_presenze * 100) / num_lezioni < int(config['SETTINGS']['percentuale_presenze_minima']):
            return jsonify({'error': True, 'errormessage': 'Minimum attendance requirement not met'}), 409
        
        if corso.file_certificato is None:
            return jsonify({'error': True, 'errormessage': 'Certificate not found, please contact course teacher'}), 404

        return send_file('.' + corso.file_certificato, as_attachment=True, mimetype='application/pdf', attachment_filename=corso.titolo + 'certificate')
