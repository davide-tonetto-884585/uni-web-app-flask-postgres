import json
import configparser
from flask import Blueprint, jsonify, request
from datetime import date

from .. import PreLoginSession, SessionDocenti, SessionAmministratori, SessionStudenti
from ..model.marshmallow_models import ProgrammazioneCorsoSchema, ProgrammazioneLezioniSchema, CorsoSchema
from .auth import token_required
from ..model.models import Docente, DocenteCorso, Utente, ProgrammazioneCorso, ProgrammazioneLezioni, PresenzeLezione, Studente, IscrizioniCorso, Aula, Corso

iscrizioni = Blueprint('iscrizioni', __name__)

programmazione_corsi_schema = ProgrammazioneCorsoSchema(many=True)
programmazione_corso_schema = ProgrammazioneCorsoSchema()
programmazione_lezioni_schema = ProgrammazioneLezioniSchema(many=True)
programmazione_lezione_schema = ProgrammazioneLezioniSchema()
corsi_schema = CorsoSchema(many=True)


@iscrizioni.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/iscrizioni', methods=['POST'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def add_iscrizione(user, id_corso, id_prog):
    with SessionStudenti() as sessionStudenti:
        sessionStudenti.begin()
        config = configparser.ConfigParser()
        config.read('global_settings.ini')

        if request.form.get('id_studente') is None:
            return jsonify({'error': True, 'errormessage': 'Missing information'}), 400

        # Controlla che lo studente esista
        studente = sessionStudenti.query(Studente).filter(
            Studente.id == request.form.get('id_studente')).first()
        if studente is None:
            return jsonify({'error': True, 'errormessage': 'Student not found'}), 404

        if ('studente' in user['roles'] and user['id'] != int(request.form.get('id_studente'))):
            return jsonify({'error': True, 'errormessage': 'You cannot enroll other students to the course'}), 400

        # controllo che il numero di iscrizioni attive dello studente non superi il limite consentito
        active_prog_course = sessionStudenti.query(ProgrammazioneCorso.id).\
            join(ProgrammazioneLezioni, ProgrammazioneCorso.id == ProgrammazioneLezioni.id_programmazione_corso).\
            filter(ProgrammazioneLezioni.data >= date.today()).\
            group_by(ProgrammazioneCorso.id).subquery()
        if sessionStudenti.query(IscrizioniCorso).\
                join(ProgrammazioneCorso, ProgrammazioneCorso.id == IscrizioniCorso.id_programmazione_corso).\
                filter(ProgrammazioneCorso.id.in_(active_prog_course)).\
                filter(IscrizioniCorso.id_studente == studente.id).count() >= int(config['SETTINGS']['limite_iscrizioni_attive_studente']):
            return jsonify({'error': True, 'errormessage': 'Registrations limit reached'}), 400

        # Controlla che lo studente non sia già iscritto al corso
        if sessionStudenti.query(IscrizioniCorso).\
                filter(IscrizioniCorso.id_studente == studente.id).\
                filter(IscrizioniCorso.id_programmazione_corso == id_prog).count() != 0:

            return jsonify({'error': True, 'errormessage': 'Student already enrolled to the course'}), 409

        prog_corso = sessionStudenti.query(ProgrammazioneCorso).filter(
            ProgrammazioneCorso.id == id_prog).first()
        in_presenza = None

        # Se lo studente ha scelto "duale" e non sceglie se in presenza od online, allora lo setta a True di default
        if prog_corso.modalita == 'duale':
            if request.form.get('in_presenza') is not None:
                in_presenza = True if request.form.get(
                    'in_presenza') == 'true' else False
            else:
                in_presenza = True
        elif prog_corso.modalita == 'presenza':
            in_presenza = True

        # Recupera il numero di iscritti
        num_iscritti = sessionStudenti.query(IscrizioniCorso).filter(
            IscrizioniCorso.id_programmazione_corso == id_prog).count()

        num_iscritti_presenza = sessionStudenti.query(IscrizioniCorso).filter(
            IscrizioniCorso.id_programmazione_corso == id_prog).filter(IscrizioniCorso.in_presenza == True).count()

        # Recupera la capienza dell'aula più piccola
        if prog_corso.modalita == 'duale' or prog_corso.modalita == 'presenza':
            capienza_aula_piu_piccola = sessionStudenti.query(Aula.capienza).\
                join(ProgrammazioneLezioni, ProgrammazioneLezioni.id_aula == Aula.id).\
                filter(ProgrammazioneLezioni.id_programmazione_corso == prog_corso.id).\
                order_by(Aula.capienza).limit(1).first()[0]

        if prog_corso.modalita == 'duale':
            if (prog_corso.limite_iscrizioni is not None and num_iscritti >= prog_corso.limite_iscrizioni) \
                    or (in_presenza == True and num_iscritti_presenza >= capienza_aula_piu_piccola):
                return jsonify({'error': True, 'errormessage': 'Inscription limit reached.'}), 401

        # Si puo' indicare un limite di iscrizioni, se non e' indicato viene scelto come limite la capienza dell'aula piu' piccola
        # Nota: ogni lezione ha una sola aula
        if prog_corso.modalita == 'presenza':
            if (prog_corso.limite_iscrizioni is not None and num_iscritti >= prog_corso.limite_iscrizioni) \
                    or (num_iscritti >= capienza_aula_piu_piccola):
                return jsonify({'error': True, 'errormessage': 'Inscription limit reached.'}), 401

        new_iscrizione = IscrizioniCorso(id_studente=studente.id,
                                         id_programmazione_corso=prog_corso.id,
                                         in_presenza=in_presenza)

        try:
            sessionStudenti.add(new_iscrizione)
            sessionStudenti.commit()
        except Exception as e:
            sessionStudenti.rollback()
            return jsonify({'error': True, 'errormessage': 'Registration entry error' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200


@iscrizioni.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/iscrizioni', methods=['GET'])
# @token_required(restrict_to_roles=['amministratore', 'docente'])
def get_iscrizioni(id_corso, id_prog):
    with PreLoginSession() as preLoginSession, preLoginSession.begin():

        # Campi del form
        skip = request.args.get('skip')
        limit = request.args.get('limit')
        in_presenza = request.args.get('in_presenza')
        name = request.args.get('nome')
        lastname = request.args.get('cognome')

        try:
            # Query per recurepare le iscrizioni dal programma del corso
            iscrizioni = preLoginSession.query(Utente.id, Utente.nome, Utente.cognome, IscrizioniCorso.in_presenza).\
                join(Studente, Utente.id == Studente.id).\
                join(IscrizioniCorso, Studente.id == IscrizioniCorso.id_studente).\
                filter(IscrizioniCorso.id_programmazione_corso == id_prog).\
                order_by(Utente.cognome, Utente.nome)

            # Filtri per migliorare la ricerca e/o visualizzazione
            if in_presenza is not None:
                iscrizioni = iscrizioni.filter(
                    IscrizioniCorso.in_presenza == in_presenza)
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
            return jsonify({'error': True, 'errormessage': 'Error while retrieving course enrollments: ' + str(e)}), 500

        return jsonify(json.loads(json.dumps([dict(studente._mapping) for studente in iscrizioni]))), 200


@iscrizioni.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/iscrizioni/<id_studente>', methods=['DELETE'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def remove_subscription(user, id_corso, id_prog, id_studente):
    with SessionStudenti() as sessionStudenti:
        sessionStudenti.begin()

        # Controlla che lo studente non stia cercando di eliminare altri studenti al di fuori di sé stesso
        if ('studente' in user['roles'] and user['id'] != int(id_studente)):
            return jsonify({'error': True, 'errormessage': 'You are not authorized to remove a student from the course outside of yourself'}), 400

        # Controlla che il docente non stia cercando di eliminare uno studente da un corso che non gli appartiene
        if ('docente' in user['roles'] and 'amministratore' not in user['roles']):
            if (sessionStudenti.query(DocenteCorso.id_docente).
                    filter(DocenteCorso.id_corso == id_corso, DocenteCorso.id_docente == user['id']).count() == 0):

                return jsonify({'error': True, 'errormessage': 'You are not authorized to remove a student from a course that does not belong to you'}), 401

        # controllo che il corso debba ancora iniziare
        if sessionStudenti.query(ProgrammazioneCorso).\
                join(ProgrammazioneLezioni, ProgrammazioneLezioni.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.id == id_prog).\
                filter(ProgrammazioneLezioni.data <= date.today()).count() > 0:
            return jsonify({'error': True, 'errormessage': 'You cannot unsubscribe from a course that has already started'}), 401

        try:
            iscrizione = sessionStudenti.query(IscrizioniCorso).\
                filter(IscrizioniCorso.id_studente == id_studente,
                       IscrizioniCorso.id_programmazione_corso == id_prog).first()

            sessionStudenti.delete(iscrizione)
            sessionStudenti.commit()
        except Exception as e:
            sessionStudenti.rollback()
            return jsonify({'error': True, 'errormessage': 'Unable to unsubscribe student: ' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200


@iscrizioni.route('/utenti/studenti/<id>/iscrizioni', methods=['GET'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def get_student_inscriptions(user, id):
    with SessionStudenti() as sessionStudenti, sessionStudenti.begin():

        if 'studente' in user['roles'] and user['id'] != int(id):
            return jsonify({'error': True, 'errormessage': 'You cannot see other students\' enrollments'}), 401

        try:
            inscriptions = sessionStudenti.query(Corso.id, Corso.titolo, Corso.descrizione, Corso.lingua, Corso.immagine_copertina, Corso.file_certificato, Corso.abilitato,
                                                 ProgrammazioneCorso.id.label('id_programmazione_corso'), IscrizioniCorso.in_presenza)\
                .join(ProgrammazioneCorso, Corso.id == ProgrammazioneCorso.id_corso)\
                .join(IscrizioniCorso, IscrizioniCorso.id_programmazione_corso == ProgrammazioneCorso.id)\
                .filter(IscrizioniCorso.id_studente == id).all()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Error in retrieving student enrollments: ' + str(e)}), 500

        return jsonify(json.loads(json.dumps([dict(inscription._mapping) for inscription in inscriptions]))), 200
