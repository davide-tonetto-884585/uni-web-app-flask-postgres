import json
import configparser
from flask import Blueprint, jsonify, request
from datetime import date

from . import PreLoginSession, SessionDocenti, SessionAmministratori, SessionStudenti
from .marshmallow_models import ProgrammazioneCorsoSchema, ProgrammazioneLezioniSchema, CorsoSchema
from .auth import token_required
from .models import Docente, DocenteCorso, Utente, ProgrammazioneCorso, ProgrammazioneLezioni, PresenzeLezione, Studente, IscrizioniCorso, Aula, Corso

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
            return jsonify({'error': True, 'errormessage': 'Dati mancanti'}), 400

        # Controlla che lo studente esista
        studente = sessionStudenti.query(Studente).filter(
            Studente.id == request.form.get('id_studente')).first()
        if studente is None:
            return jsonify({'error': True, 'errormessage': 'Studente inesistente'}), 404

        if ('studente' in user['roles'] and user['id'] != int(request.form.get('id_studente'))):
            return jsonify({'error': True, 'errormessage': 'Non puoi iscrivere altri studenti al corso'}), 400

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


@iscrizioni.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/iscrizioni', methods=['GET'])
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


@iscrizioni.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/iscrizioni/<id_studente>', methods=['DELETE'])
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


@iscrizioni.route('/utenti/studenti/<id>/iscrizioni', methods=['GET'])
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
