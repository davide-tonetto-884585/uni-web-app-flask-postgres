import json
from backend.utils import load_file
from flask import Blueprint, jsonify, request

from . import PreLoginSession, SessionDocenti, SessionAmministratori, SessionStudenti
from .marshmallow_models import RisorseCorsoSchema
from .auth import token_required
from .models import DocenteCorso, ProgrammazioneCorso, IscrizioniCorso, RisorseCorso

risorse = Blueprint('risorse', __name__)

""" reLoginSession = PreLoginSession()
sessionDocenti = SessionDocenti()
sessionAmministratori = SessionAmministratori()
sessionStudenti = SessionStudenti() """

risorsa_corso_schema = RisorseCorsoSchema()
risorse_corso_schema = RisorseCorsoSchema(many=True)


# Funzione per controllare che un docente possieda il corso (per evitare ridondanze nel codice)
def checkDocenteHasCourse(user, id_corso):
    with SessionDocenti() as sessionDocenti, sessionDocenti.begin():
        return (sessionDocenti.query(DocenteCorso.id_docente).\
            filter(DocenteCorso.id_corso == id_corso, DocenteCorso.id_docente == user['id']).count() != 0)


#ritorna le risorse di un corso
@risorse.route('/corso/<id>/risorse', methods=['GET'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])    #ruoli che possono eseguire questa funzione
def get_risorse(user, id):
    with SessionDocenti() as sessionDocenti, sessionDocenti.begin():
        
        # Parametri del form
        skip = request.args.get('skip')
        limit = request.args.get('limit')
        name = request.args.get('nome')
        visible = request.args.get('visibile')

        try:
            if ('studente' in user['roles']):

                # Controlliamo che lo studente sia iscritto al corso, altrimenti non mostriamo le risorse
                if(sessionDocenti.query(IscrizioniCorso.id_studente).\
                    join(ProgrammazioneCorso, ProgrammazioneCorso.id == IscrizioniCorso.id_programmazione_corso).\
                    filter(ProgrammazioneCorso.id_corso == id, IscrizioniCorso.id_studente == user['id']).count() == 0):

                    return jsonify({'error': True, 'errormessage': 'Non puoi vedere la/e risorsa/e di questo corso'}), 401

                # Forziamo la visualizzazione delle risorse solo a quelle visibili, per gli studenti iscritti
                else:
                    visible = True

            # Controlliamo che il docente sia proprietario del corso, altrimento non mostriamo le risorse
            elif('amministratore' not in user['roles'] and not checkDocenteHasCourse(user, id)):
                return jsonify({'error': True, 'errormessage': 'Non puoi vedere la/e risorsa/e di questo corso'}), 401

            risorse = sessionDocenti.query(RisorseCorso).\
                filter(RisorseCorso.id_corso == id).\
                order_by(RisorseCorso.nome, RisorseCorso.visibile)

            #Filtri per specializzare la ricerca e/o la visualizzazione delle risorse del corso
            if visible is not None:
                risorse = risorse.filter(RisorseCorso.visibile == visible)
            if name is not None:
                risorse = risorse.filter(RisorseCorso.nome.like('%' + name + '%'))
            if skip is not None:
                risorse = risorse.offset(skip)
            if limit is not None:
                risorse = risorse.limit(limit)

            risorse = risorse.all()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Errore durante il reperimento delle risorse del corso: ' + str(e)}), 500

        return jsonify(risorse_corso_schema.dump(risorse)), 200


#aggiunge risorse a un corso
@risorse.route('/corso/<id>/risorse', methods=['POST'])
@token_required(restrict_to_roles=['amministratore', 'docente'])    #ruoli che possono eseguire questa funzione
def add_risorsa(user, id):
    with SessionDocenti() as sessionDocenti:
        sessionDocenti.begin()

        # Controlliamo che il docente sia proprietario del corso, altrimento non permettiamo l'aggiunta di risorse
        if('docente' in user['roles'] and 'amministratore' not in user['roles'] and not checkDocenteHasCourse(user, id)):
            return jsonify({'error': True, 'errormessage': 'Non puoi aggiuntere la/e risorsa/e a questo corso'}), 401

        #controllo che i dati obbligatori siano stati inseriti nel form
        if request.form.get('nome') is None or request.form.get('visibile') is None:
            return jsonify({'error': True, 'errormessage': 'Dati mancanti'}), 400

        # Recupera il path della risorsa e la salva (se non già presente) nel server
        path_risorsa = load_file('path_risorsa')

        # Crea un oggetto di tipo RisorseCorso da aggiungere successivamente al DB
        new_risorsa = RisorseCorso(nome = request.form.get('nome'), visibile = request.form.get('visibile'), path_risorsa = path_risorsa, id_corso = id)
        
        try:
            # Aggiunge la risorsa al corso
            sessionDocenti.add(new_risorsa)
            sessionDocenti.commit()
        except Exception as e:
            sessionDocenti.rollback()
            return jsonify({'error': True, 'errormessage': 'Errore inserimento risorsa' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200


@risorse.route('/corso/<id_corso>/risorse/<id_risorsa>', methods=['DELETE'])
@token_required(restrict_to_roles=['amministratore', 'docente'])
def delete_risorsa(user, id_corso, id_risorsa):
    with SessionDocenti() as sessionDocenti:
        sessionDocenti.begin()
    
        # Controlliamo che il docente sia proprietario del corso, altrimento non permettiamo la rimozione delle risorse
        if('docente' in user['roles'] and 'amministratore' not in user['roles'] and not checkDocenteHasCourse(user, id_corso)):
            return jsonify({'error': True, 'errormessage': 'Non puoi rimuovere la/e risorsa/e per questo corso'}), 401

        try:
            # Elimina la risorsa dal corso
            risorsa = sessionDocenti.query(RisorseCorso).\
                filter(RisorseCorso.id == id_risorsa, RisorseCorso.id_corso == id_corso).first()

            sessionDocenti.delete(risorsa)
            sessionDocenti.commit()
        except Exception as e:
            sessionDocenti.rollback()
            return jsonify({'error': True, 'errormessage': 'Errore nell\'eliminazione della risorsa: ' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200


@risorse.route('/corso/<id_corso>/risorse/<id_risorsa>', methods=['PUT'])
@token_required(restrict_to_roles=['amministratore', 'docente'])
def modify_risorsa(user, id_corso, id_risorsa):
    with SessionDocenti() as sessionDocenti:
        sessionDocenti.begin()

        # Controlliamo che il docente sia proprietario del corso, altrimento non permettiamo la modifica delle risorse
        if('docente' in user['roles'] and 'amministratore' not in user['roles'] and not checkDocenteHasCourse(user, id_corso)):
            return jsonify({'error': True, 'errormessage': 'Non puoi modificare la/e risorsa/e di questo corso'}), 401

        # Recupera la risorsa da modificare
        try:
            risorsa = sessionDocenti.query(RisorseCorso).filter(RisorseCorso.id_corso == id_corso, RisorseCorso.id == id_risorsa).first()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Risorsa inesistente: ' + str(e)}), 404

        # Campi del form
        nome = request.form.get('nome')
        visibile = request.form.get('visibile')

        # Se i campi obbligatori sono None allora lascia i vecchi valori
        if nome is not None:
            risorsa.nome = nome

        if visibile is not None:
            risorsa.visibile = visibile

        try:
            sessionDocenti.commit()
        except Exception as e:
            sessionDocenti.rollback()
            return jsonify({'error': True, 'errormessage': 'Errore aggiornamento risorsa del corso: ' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200