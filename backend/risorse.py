import json
from backend.utils import load_file
from flask import Blueprint, jsonify, request

from . import PreLoginSession, SessionDocenti, SessionAmministratori, SessionStudenti
from .marshmallow_models import RisorseCorsoSchema
from .auth import token_required
from .models import DocenteCorso, ProgrammazioneCorso, IscrizioniCorso, RisorseCorso

risorse = Blueprint('risorse', __name__)

preLoginSession = PreLoginSession()
sessionDocenti = SessionDocenti()
sessionAmministratori = SessionAmministratori()
sessionStudenti = SessionStudenti()

risorsa_corso_schema = RisorseCorsoSchema()
risorse_corso_schema = RisorseCorsoSchema(many=True)


# Funzione per controllare che un docente possieda il corso (per evitare ridondanze nel codice)
def checkDocenteHasCourse(user, id_corso):
    return (sessionDocenti.query(DocenteCorso.id_docente).\
        filter(DocenteCorso.id_corso == id, DocenteCorso.id_docente == user['id']).count() != 0)


#ritorna le risorse di un corso
@risorse.route('/corso/<id>/risorse', methods=['GET'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])    #ruoli che possono eseguire questa funzione
def get_risorse(user, id):
    # Parametri del form
    skip = request.args('skip')
    limit = request.args('limit')
    name = request.args('nome')
    visible = request.args('visibile')

    if (user['role'] == 'studente'):

        # Controlliamo che lo studente sia iscritto al corso, altrimenti non mostriamo le risorse
        if(sessionDocenti.query(IscrizioniCorso.id_studente).\
            join(ProgrammazioneCorso, ProgrammazioneCorso.id == IscrizioniCorso.id_programmazione_corso).\
            filter(ProgrammazioneCorso.id_corso == id, IscrizioniCorso.id_studente == user['id']).count() == 0):

            return jsonify({'error': True, 'errormessage': 'Non puoi vedere la/e risorsa/e di questo corso'}), 401

        # Forziamo la visualizzazione delle risorse solo a quelle visibili, per gli studenti iscritti
        else:
            visible = True

    # Controlliamo che il docente sia proprietario del corso, altrimento non mostriamo le risorse
    elif(user['role'] == 'docente' and not checkDocenteHasCourse(user, id)):
        return jsonify({'error': True, 'errormessage': 'Non puoi vedere la/e risorsa/e di questo corso'}), 401

    risorse = sessionStudenti.query(RisorseCorso).\
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

    if len(risorse) == 0:
        # Se non trova alcuna risorsa, ritorna uno status code 404
        return jsonify({'error': True, 'errormessage': 'Nessuna risorsa del corso disponibile'}), 404
    else:
        return jsonify(risorse_corso_schema.dump(risorse)), 200


#aggiunge risorse a un corso
@risorse.route('/corso/<id>/risorse', methods=['POST'])
@token_required(restrict_to_roles=['amministratore', 'docente'])    #ruoli che possono eseguire questa funzione
def add_risorsa(user, id):
    
    # Controlliamo che il docente sia proprietario del corso, altrimento non permettiamo l'aggiunta di risorse
    if(user['role'] == 'docente' and not checkDocenteHasCourse(user, id)):
        return jsonify({'error': True, 'errormessage': 'Non puoi aggiuntere la/e risorsa/e a questo corso'}), 401

    #controllo che i dati obbligatori siano stati inseriti nel form
    if request.form.get('nome') is None or request.form.get('visibile') is None:
        return jsonify({'error': True, 'errormessage': 'Dati mancanti'}), 404

    # Recupera il path della risorsa e la salva (se non già presente) nel server
    path_risorsa = load_file('risorsa_corso')

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
    
    # Controlliamo che il docente sia proprietario del corso, altrimento non permettiamo la rimozione delle risorse
    if(user['role'] == 'docente' and not checkDocenteHasCourse(user, id)):
        return jsonify({'error': True, 'errormessage': 'Non puoi rimuovere la/e risorsa/e per questo corso'}), 401

    try:
        # Elimina la risorsa dal corso
        sessionDocenti.delete(RisorseCorso(id_corso = id_corso, id_risorsa = id_risorsa))
        sessionDocenti.commit()
    except Exception as e:
        sessionDocenti.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore nell\'eliminazione della risorsa'}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200


@risorse.route('/corso/<id_corso>/risorse/<id_risorsa>', methods=['PUT'])
@token_required(restrict_to_roles=['amministratore', 'docente'])
def modify_risorsa(user, id_corso, id_risorsa):

    # Controlliamo che il docente sia proprietario del corso, altrimento non permettiamo la modifica delle risorse
    if(user['role'] == 'docente' and not checkDocenteHasCourse(user, id)):
        return jsonify({'error': True, 'errormessage': 'Non puoi modificare la/e risorsa/e di questo corso'}), 401

    # Recupera la risorsa da modificare
    risorsa = sessionDocenti.query(RisorseCorso).filter(RisorseCorso.id_corso == id_corso, RisorseCorso.id_risorsa == id_risorsa).first()

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