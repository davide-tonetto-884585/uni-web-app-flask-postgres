from .models import DocenteCorso, IscrizioniCorso, PresenzeLezione, ProgrammazioneCorso, ProgrammazioneLezioni, Scuola, Studente, Utente
from flask import Blueprint, jsonify, current_app, request
from datetime import date
import json

from sqlalchemy import func, desc
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.sql import extract

from . import SessionDocenti
from .auth import token_required

statistics = Blueprint('statistics', __name__)


@statistics.route('/corsi/<id>/statistiche', methods=['GET'])
@token_required(restrict_to_roles=['amministratore', 'docente'])
def get_statistiche_corso(user, id):
    with SessionDocenti() as sessionDocenti, sessionDocenti.begin():
        # controllo che il corso sia del docente che sta richiedendo i dati
        if 'amministratore' not in user['roles']:
            if sessionDocenti.query(DocenteCorso).filter(DocenteCorso.id_corso == id, DocenteCorso.id_docente == user['id']).count() == 0:
                return jsonify({'error': True, 'errormessage': 'You are not authorized to view the statistics of a course that does not belong to you.'}), 401

        try:
            totale_iscrizioni_maschi = sessionDocenti.query(IscrizioniCorso).\
                join(Utente, IscrizioniCorso.id_studente == Utente.id).\
                join(ProgrammazioneCorso, IscrizioniCorso.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(Utente.sesso == 'M').\
                filter(ProgrammazioneCorso.id_corso == id).count()

            totale_iscrizioni_femmine = sessionDocenti.query(IscrizioniCorso).\
                join(Utente, IscrizioniCorso.id_studente == Utente.id).\
                join(ProgrammazioneCorso, IscrizioniCorso.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(Utente.sesso == 'F').\
                filter(ProgrammazioneCorso.id_corso == id).count()

            totale_iscrizioni_altri_sessi = sessionDocenti.query(IscrizioniCorso).\
                join(Utente, IscrizioniCorso.id_studente == Utente.id).\
                join(ProgrammazioneCorso, IscrizioniCorso.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(Utente.sesso == None).\
                filter(ProgrammazioneCorso.id_corso == id).count()

            eta_media_iscritti = sessionDocenti.query(func.avg(date.today().year - extract('year', Utente.data_nascita))).\
                join(IscrizioniCorso, IscrizioniCorso.id_studente == Utente.id).\
                join(ProgrammazioneCorso, IscrizioniCorso.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.id_corso == id).first()

            totale_iscrizioni = sessionDocenti.query(IscrizioniCorso).\
                join(ProgrammazioneCorso, IscrizioniCorso.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.id_corso == id).count()

            totale_lezioni = sessionDocenti.query(ProgrammazioneLezioni).\
                join(ProgrammazioneCorso, ProgrammazioneLezioni.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.id_corso == id).count()

            totale_presenze = sessionDocenti.query(PresenzeLezione).\
                join(ProgrammazioneLezioni, PresenzeLezione.id_programmazione_lezioni == ProgrammazioneLezioni.id).\
                join(ProgrammazioneCorso, ProgrammazioneLezioni.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.id_corso == id).count()

            distribuzione_studenti = sessionDocenti.query(Scuola.provincia.label('name'), func.count().label('value')).\
                join(Studente, Studente.id_scuola == Scuola.id).\
                join(IscrizioniCorso, IscrizioniCorso.id_studente == Studente.id).\
                join(ProgrammazioneCorso, IscrizioniCorso.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.id_corso == id).\
                group_by(Scuola.provincia).all()

            provenienza_studenti = sessionDocenti.query(Studente.indirizzo_di_studio.label('name'), func.count().label('value')).\
                join(IscrizioniCorso, IscrizioniCorso.id_studente == Studente.id).\
                join(ProgrammazioneCorso, IscrizioniCorso.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.id_corso == id).\
                group_by(Studente.indirizzo_di_studio).all()

            totale_iscrizioni_presenza = sessionDocenti.query(IscrizioniCorso).\
                join(ProgrammazioneCorso, IscrizioniCorso.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.modalita == 'presenza').\
                filter(ProgrammazioneCorso.id_corso == id).count()

            totale_iscrizioni_online = sessionDocenti.query(IscrizioniCorso).\
                join(ProgrammazioneCorso, IscrizioniCorso.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.modalita == 'online').\
                filter(ProgrammazioneCorso.id_corso == id).count()

            totale_iscrizioni_duale = sessionDocenti.query(IscrizioniCorso).\
                join(ProgrammazioneCorso, IscrizioniCorso.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.modalita == 'duale').\
                filter(ProgrammazioneCorso.id_corso == id).count()

            totale_lezioni_online = sessionDocenti.query(ProgrammazioneLezioni).\
                join(ProgrammazioneCorso, ProgrammazioneLezioni.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.modalita == 'online').\
                filter(ProgrammazioneCorso.id_corso == id).count()

            totale_lezioni_presenza = sessionDocenti.query(ProgrammazioneLezioni).\
                join(ProgrammazioneCorso, ProgrammazioneLezioni.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.modalita == 'presenza').\
                filter(ProgrammazioneCorso.id_corso == id).count()

            totale_lezioni_duale = sessionDocenti.query(ProgrammazioneLezioni).\
                join(ProgrammazioneCorso, ProgrammazioneLezioni.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.modalita == 'duale').\
                filter(ProgrammazioneCorso.id_corso == id).count()

            totale_presenze_online = sessionDocenti.query(PresenzeLezione).\
                join(ProgrammazioneLezioni, PresenzeLezione.id_programmazione_lezioni == ProgrammazioneLezioni.id).\
                join(ProgrammazioneCorso, ProgrammazioneLezioni.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.modalita == 'online').\
                filter(ProgrammazioneCorso.id_corso == id).count()

            totale_presenze_presenza = sessionDocenti.query(PresenzeLezione).\
                join(ProgrammazioneLezioni, PresenzeLezione.id_programmazione_lezioni == ProgrammazioneLezioni.id).\
                join(ProgrammazioneCorso, ProgrammazioneLezioni.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.modalita == 'presenza').\
                filter(ProgrammazioneCorso.id_corso == id).count()

            totale_presenze_duale = sessionDocenti.query(PresenzeLezione).\
                join(ProgrammazioneLezioni, PresenzeLezione.id_programmazione_lezioni == ProgrammazioneLezioni.id).\
                join(ProgrammazioneCorso, ProgrammazioneLezioni.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.modalita == 'duale').\
                filter(ProgrammazioneCorso.id_corso == id).count()

            count_iscrizioni = sessionDocenti.query(ProgrammazioneCorso.id, func.count().label('num_iscrizioni')).\
                join(IscrizioniCorso, IscrizioniCorso.id_programmazione_corso == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.id_corso == id).\
                group_by(ProgrammazioneCorso.id).subquery()
            count_presenze = sessionDocenti.query(ProgrammazioneCorso.id, func.count().label('num_presenze')).\
                join(ProgrammazioneLezioni, ProgrammazioneLezioni.id_programmazione_corso == ProgrammazioneCorso.id).\
                join(PresenzeLezione, PresenzeLezione.id_programmazione_lezioni == ProgrammazioneLezioni.id).\
                filter(ProgrammazioneCorso.id_corso == id).\
                group_by(ProgrammazioneCorso.id).subquery()
            confronto_programmazioni_corso = sessionDocenti.query(ProgrammazioneCorso.id, ProgrammazioneCorso.modalita,
                                                                  coalesce(count_iscrizioni.c.num_iscrizioni, 0).label(
                                                                      'num_iscrizioni'),
                                                                  coalesce(count_presenze.c.num_presenze, 0).label('num_presenze')).\
                outerjoin(count_iscrizioni, count_iscrizioni.c.id == ProgrammazioneCorso.id).\
                outerjoin(count_presenze, count_presenze.c.id == ProgrammazioneCorso.id).\
                filter(ProgrammazioneCorso.id_corso == id).order_by(ProgrammazioneCorso.id).all()

        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Error while retrieving statistics: ' + str(e)}), 500

        return jsonify(
            {
                'error': False, 'errormessage': '',
                'totale_iscrizioni_maschi': totale_iscrizioni_maschi,
                'totale_iscrizioni_femmine': totale_iscrizioni_femmine,
                'totale_iscrizioni_altri_sessi': totale_iscrizioni_altri_sessi,
                'eta_media_iscritti': eta_media_iscritti[0],
                'totale_lezioni': totale_lezioni,
                'totale_presenze': totale_presenze,
                'totale_iscrizioni': totale_iscrizioni,
                'totale_lezioni_online': totale_lezioni_online,
                'totale_lezioni_presenza': totale_lezioni_presenza,
                'totale_lezioni_duale': totale_lezioni_duale,
                'totale_iscrizioni_presenza': totale_iscrizioni_presenza,
                'totale_iscrizioni_online': totale_iscrizioni_online,
                'totale_iscrizioni_duale': totale_iscrizioni_duale,
                'totale_presenze_online': totale_presenze_online,
                'totale_presenze_presenza': totale_presenze_presenza,
                'totale_presenze_duale': totale_presenze_duale,
                'distribuzione_studenti': json.loads(json.dumps([dict(dist._mapping) for dist in distribuzione_studenti])),
                'provenienza_studenti': json.loads(json.dumps([dict(dist._mapping) for dist in provenienza_studenti])),
                'confronto_programmazioni_corso': json.loads(json.dumps([dict(dist._mapping) for dist in confronto_programmazioni_corso])),
            }
        ), 200
