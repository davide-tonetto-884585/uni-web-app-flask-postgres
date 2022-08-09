import json
from flask import Blueprint, jsonify, request

from . import PreLoginSession, SessionDocenti, SessionAmministratori, SessionStudenti
from .marshmallow_models import ProgrammazioneCorsoSchema, ProgrammazioneLezioniSchema, CorsoSchema
from .auth import token_required
from .models import Docente, DocenteCorso, Utente, ProgrammazioneCorso, ProgrammazioneLezioni, PresenzeLezione, Studente, IscrizioniCorso, Aula, Corso

presenze = Blueprint('presenze', __name__)

programmazione_corsi_schema = ProgrammazioneCorsoSchema(many=True)
programmazione_corso_schema = ProgrammazioneCorsoSchema()
programmazione_lezioni_schema = ProgrammazioneLezioniSchema(many=True)
programmazione_lezione_schema = ProgrammazioneLezioniSchema()
corsi_schema = CorsoSchema(many=True)


# ritorna le presenze di una specifica lezione
@presenze.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/lezioni/<id_lezione>/presenze', methods=['GET'])
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


@presenze.route('/corsi/<id_corso>/programmazione_corso/<id_prog>/lezioni/<id_lezione>/presenze', methods=['POST'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def add_presenza(user, id_corso, id_prog, id_lezione):
    with SessionStudenti() as sessionStudenti:
        sessionStudenti.begin()

        if request.form.get('id_studente') is None or request.form.get('codice_verifica_presenza') is None:
            return jsonify({'error': True, 'errormessage': 'Dati mancanti'}), 400

        # Controlla che lo studente esista
        studente = sessionStudenti.query(Studente).filter(
            Studente.id == request.form.get('id_studente')).first()
        if studente is None:
            return jsonify({'error': True, 'errormessage': 'Studente inesistente'}), 404

        if ('studente' in user['roles'] and user['id'] != int(request.form.get('id_studente'))):
            return jsonify({'error': True, 'errormessage': 'Permesso negato'}), 400

        # Controlla che lo studente sia iscritto al corso
        if sessionStudenti.query(IscrizioniCorso).\
                join(ProgrammazioneCorso, ProgrammazioneCorso.id == IscrizioniCorso.id_programmazione_corso).\
                filter(IscrizioniCorso.id_studente == studente.id, ProgrammazioneCorso.id == id_prog).count() == 0:
            return jsonify({'error': True, 'errormessage': 'Studente non iscritto al corso'}), 404
        
        if sessionStudenti.query(PresenzeLezione).\
            filter(PresenzeLezione.id_studente == studente.id, PresenzeLezione.id_programmazione_lezioni == id_lezione).count() > 0:
            return jsonify({'error': True, 'errormessage': 'Presenza già segnata'}), 404

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
