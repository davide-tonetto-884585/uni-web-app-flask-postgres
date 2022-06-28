import json
from telnetlib import DO
from flask import Blueprint, jsonify, request

from . import PreLoginSession, SessionDocenti, SessionAmministratori
from .marshmallow_models import CorsoSchema, DocenteSchema
from .auth import token_required
from .models import Corso, Docente, DocenteCorso, Studente, Utente, ProgrammazioneCorso, IscrizioniCorso
from .utils import load_file

corsi = Blueprint('corsi', __name__)

preLoginSession = PreLoginSession()
sessionDocenti = SessionDocenti()
sessionAmministratori = SessionAmministratori()

# converte un array di oggetti corsi in un array di json
corsi_schemas = CorsoSchema(many=True)
corsi_schema = CorsoSchema()  # converte un singolo oggetto corso in json
docenti_schemas = DocenteSchema(many=True)


@corsi.route('/corsi', methods=['GET'])
def get_corsi():
    # Parametri del form
    name = request.args.get('name')
    skip = request.args.get('skip')
    limit = request.args.get('limit')
    lingua = request.args.get('lingua')

    # Query per reperire tutti i corsi
    corsi = preLoginSession.query(Corso).order_by(Corso.titolo).all()

    # Filtri per la specializzazione della ricerca o visualizzazione dei corsi
    if name is not None:
        corsi = corsi.filter(Corso.titolo.like('%' + name + '%'))
    if skip is not None:
        corsi = corsi.offset(skip)
    if limit is not None:
        corsi = corsi.limit(limit)
    if lingua is not None:
        corsi = corsi.filter(Corso.lingua.like('%' + lingua + '%'))

    if len(corsi) == 0 :
        # Se non trova alcuna risorsa, ritorna uno status code 404
        return jsonify({'error': True, 'errormessage': 'Nessun corso presente'}), 404
    else:
        return jsonify(corsi_schemas.dump(corsi.all())), 200


@corsi.route('/corsi/<id>', methods=['GET'])
def get_corso(id):
    # Query per reperire il corso
    corso = preLoginSession.query(Corso).filter(Corso.id == id)

    try:
        corso = corso.first()      # Prende il primo risultato
    except Exception as e:
        # Eccezione lanciata in caso di errore interno del server
        return jsonify({'error': True, 'errormessage': 'Errore nel reperire il corso: ' + str(e)}), 500

    if corso is None:
        # Errore lanciato nel caso non ci sia alcun risultato
        return jsonify({'error': True, 'errormessage': 'Corso inesistente'}), 404
    else:
        return jsonify(corsi_schema.dump(corso)), 200


@corsi.route('/corsi', methods=['POST'])
@token_required(restrict_to_roles=['amministratore', 'docente'])
def add_corso(user):  # su tutte token_required bisogna mettere user (per reperire i dati di chi è loggato)

    # Controlla se ci sono i campi necessari
    if request.form.get('titolo') is None:
        return jsonify({'error': True, 'errormessage': 'Titolo mancante'}), 400

    # Controlla che il corso non abbia un titolo già esistente
    if sessionDocenti.query(Corso).filter(Corso.titolo == request.form.get('titolo')).first():
        return jsonify({'error': True, 'errormessage': 'Corso gia\' esistente con lo stesso titolo'}), 409

    # Carica l'immagine di copertina e il file certificato, e ne recupera i path (se già presenti non carica niente e recupera solo i path)
    path_to_immagine_copertina = load_file('immagine_copertina')
    path_to_file_certificato = load_file('file_certificato')

    abilitato = request.form.get('abilitato') if not None else True

    # Crea l'oggetto Corso da aggiungere
    new_corso = Corso(titolo=request.form.get('titolo'),
                      descrizione=request.form.get('descrizione'),
                      lingua=request.form.get('lingua'),
                      immagine_copertina=path_to_immagine_copertina,
                      file_certificato=path_to_file_certificato,
                      abilitato=abilitato)

    try:
        # Aggiunge l'oggetto nel DB
        sessionDocenti.add(new_corso)
        sessionDocenti.commit()
    except Exception as e:
        sessionDocenti.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore inserimento corso' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200


@corsi.route('/corsi/<id>', methods=['PUT'])
@token_required(restrict_to_roles=['amministratore', 'docente'])
def modify_corso(user, id):

    # Controlla che l'utente sia il docente che deteiene il corso
    if(sessionDocenti.query(DocenteCorso).\
        filter(DocenteCorso.id_docente == user['id'], DocenteCorso.id_corso == id).count() == 0):
        return jsonify({'error': True, 'errormessage': 'Non puoi modificare un corso che non ti appartiene'}), 401

    # Recupera il corso tramite l'id
    corso = sessionDocenti.query(Corso).filter(Corso.id == id).first()

    # Campi del form
    titolo = request.form.get('titolo')
    descrizione = request.form.get('descrizione')
    lingua = request.form.get('lingua')
    abilitato = request.form.get('abilitato')

    corso.immagine_copertina = load_file('immagine_copertina')
    corso.file_certificato = load_file('file_certificato')

    # Controlla che le variabili necessarie siano settate, altrimenti le lascia ai vecchi valori
    if titolo is not None:
        corso.titolo = titolo

    if abilitato is not None:
        corso.abilitato = abilitato

    # Questi campi invece possono essere messi a None e sono a discrezione dell'utente
    corso.descrizione = descrizione
    corso.lingua = lingua

    try:
        # Apporta le modifiche (le modifiche vengono effettuate modificando i campi dell'oggetto reperito dalla query)
        sessionDocenti.commit()
    except Exception as e:
        sessionDocenti.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore aggiornamento informazioni del corso: ' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200


@corsi.route('/corsi/<id>/docenti', methods=['GET'])
def get_docenti_corsi(id):
    try:
        # Recupera i docenti dello specifico corso
        docenti = preLoginSession.\
            query(Utente.id, Utente.nome, Utente.cognome, Docente.immagine_profilo, Docente.link_pagina_docente, Docente.descrizione_docente).\
            join(Utente, Utente.id == Docente.id).\
            join(DocenteCorso, DocenteCorso.id_docente == Docente.id).\
            filter(DocenteCorso.id_corso == id).all()
    except Exception as e:
        return jsonify({'error': True, 'errormessage': 'Errore nel reperire i docenti del corso: ' + str(e)}), 500

    if len(docenti) == 0:
        return jsonify({'error': True, 'errormessage': 'Corso senza docenti assegnati'}), 404
    else:
        return jsonify(json.loads(json.dumps([dict(docente._mapping) for docente in docenti]))), 200


@corsi.route('/corsi/<id>/docenti', methods=['POST'])
@token_required(restrict_to_roles=['amministratore'])
def add_docente_corso(user, id):
    # TODO: CAPIRE SE è GIà UN ARRAY?   (Assumiamo che lo sia)
    # Crea un set per eliminare i duplicati
    id_docenti_to_add = set(request.form.get('id_docenti'))

    try:
        # Aggiunge ogni docente nel set
        for id_docente in id_docenti_to_add:
            sessionAmministratori.add(DocenteCorso(id_docente=id_docente, id_corso=id))
        
        # Solo dopo averli aggiunti tutti esegue la commit
        sessionAmministratori.commit()
    except Exception as e:
        sessionAmministratori.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore nell\'inserimento di uno (o più) docenti al corso: ' + str(e)}), 500
    
    return jsonify({'error': False, 'errormessage': ''}), 200


@corsi.route('/utenti/docenti/<id>/corsi', methods=['GET'])
def get_corsi_docente(id):
    try:
        # Recupera i corsi di un determinato docente
        corsi = preLoginSession.query(Corso).\
            join(DocenteCorso, DocenteCorso.id_corso == Corso.id).\
            filter(DocenteCorso.id_docente == id).all()
    except Exception as e:
        return jsonify({'error': True, 'errormessage': 'Errore nel reperire i corsi del docente: ' + str(e)}), 500

    return jsonify(corsi_schemas.dump(corsi)), 200


@corsi.route('/corsi/<id>/docenti', methods=['DELETE'])
@token_required(restrict_to_roles=['amministratore'])
def remove_docente(user, id):
    # Crea un set per rimuovere i duplicati
    id_docenti_to_remove = set(request.form.get('id_docenti'))

    try:
        # Rimuove i docenti presenti nel set
        for id_docente in id_docenti_to_remove:
            docente = sessionAmministratori.query(DocenteCorso).\
                filter(DocenteCorso.id_docente == id_docente, DocenteCorso.id_corso == id).first()
            sessionAmministratori.delete(docente)

        # Solo dopo averli rimossi tutti esegue la commit
        sessionAmministratori.commit()
    except Exception as e:
        sessionAmministratori.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore nell\'eliminazione di uno (o più) docenti dal corso: ' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200


@corsi.route('/corsi/<id>', methods=['DELETE'])
@token_required(restrict_to_roles=['amministratore'])
def remove_course(user, id):
    try:
        # Rimuove uno specifico corso
        corso = sessionAmministratori.query(Corso).filter(Corso.id == id).first()
        sessionAmministratori.delete(corso)
        sessionAmministratori.commit()
    except Exception as e:
        sessionAmministratori.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore nell\'eliminazione del corso: ' + str(e)}), 500

    return jsonify({'error': False, 'errormessage': ''}), 200


@corsi.route('/corsi/<id>/studenti', methods=['GET'])
def get_studenti_corso(id):
    try:
        # Reperisce tutti gli studenti del corso
        studenti = preLoginSession.\
            query(Utente.id, Utente.nome, Utente.cognome, Studente.indirizzo_di_studio, Studente.id_scuola).\
            join(Utente, Utente.id == Studente.id).\
            join(IscrizioniCorso, Studente.id == IscrizioniCorso.id_studente).\
            join(ProgrammazioneCorso, IscrizioniCorso.id_programmazione_corso == ProgrammazioneCorso.id).\
            filter(ProgrammazioneCorso.id_corso == id).all()

    except Exception as e:
        return jsonify({'error': True, 'errormessage': 'Errore nel reperire gli studenti del corso: ' + str(e)}), 500

    if len(studenti) == 0:
        return jsonify({'error': True, 'errormessage': 'Corso senza studenti registrati'}), 404
    else:
        return jsonify(json.loads(json.dumps([dict(studente._mapping) for studente in studenti]))), 200
