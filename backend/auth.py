from pydoc import Doc
import random
import string
import hmac
import hashlib
import jwt  # PyJWT
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename

from .models import Utente, Studente, Docente, Amministratore
from .utils import allowed_file, send_mail
from . import db

auth = Blueprint('auth', __name__)

# decoratore utilizzato per controllare che la richiesta contenga un token di autenticazione valido se richiesto
# e inoltre per controllare se l'utente soddisfa i requisiti per accedere alla risorsa
def token_required(restrict_to_roles=[]):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            # jwt is passed in the request header
            auth_header = request.headers.get('Authorization')
            if auth_header:
                token = auth_header.split(" ")[1]

            # return 401 if token is not passed
            if not token:
                return jsonify({'error': True, 'errormessage': 'Token mancante'}), 401

            try:
                # decoding the payload to fetch the stored details
                user_data = jwt.decode(
                    token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                #current_user = Utente.query.filter(Utente.id == user_data['id']).first()

                # se sono stati passati ruoli allora controllo che l'utente soddisfi i requisiti
                for allowed_role in restrict_to_roles:
                    if not allowed_role in user_data['roles']:
                        return jsonify({'error': True, 'errormessage': 'accesso non consentito'}), 401
            except Exception as e:
                return jsonify({
                    'error': True,
                    'errormessage': 'Token invalido: ' + str(e)
                }), 401
            # returns the current logged in users contex to the routes
            return f(user_data, *args, **kwargs)

        return decorated

    return decorator

# route usata per aggiungere un nuovo studente 
@auth.route('/studenti', methods=['POST'])
def signup_student():
    # controllo che la richiesta contenga tutte le informazioni obbligatorie
    if request.form.get('email') is None or\
            request.form.get('password') is None or\
            request.form.get('nome') is None or\
            request.form.get('cognome') is None or\
            request.form.get('data_nascita') is None:
        return jsonify({'error': True, 'errormessage': 'Sono necessarie ulteriori informazioni per creare lo studente'}), 404

    # controlle che non esista già un utente con la stessa email
    if Utente.query.filter(Utente.email == request.form.get('email')).first():
        return jsonify({'error': True, 'errormessage': 'utente gia\' esistente'}), 404

    # genero un salt randomico per rendere la password illeggibile da database
    salt = ''.join(random.choice(string.printable) for i in range(16))
    # creo il digest della password da salvare nel database
    digest = hmac.new(salt.encode(), request.form.get(
        'password').encode(), hashlib.sha512).hexdigest()

    # genero il token usato per verificare che la mial dell'utente sia valida
    token_salt = ''.join(random.choice(string.printable) for i in range(16))
    token = hmac.new(salt.encode(), token_salt.encode(),
                     hashlib.sha512).hexdigest()
    
    # creo il nuovo utente con le informazioni ottenute
    new_user = Utente(email=request.form.get('email'),
                      salt=salt,
                      digest=digest,
                      nome=request.form.get('nome'),
                      cognome=request.form.get('cognome'),
                      data_nascita=request.form.get('data_nascita'),
                      token_verifica=token)

    # inserisco i dati nel database
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore inserimento utente: ' + str(e)}), 404
    
    # invio mail per verifica validità indirizzo se richiesta, il frontend passerà un link che sarà mostrato nella mail completato
    # con tipologia utente, token e id utente
    if request.form.get('frontend_activation_link') is not None:
        send_mail(
            [new_user.email],
            'Confirm your email',
            'To verify your email please press this button: <a href="%s/%s/%s/%d">Confirm your email</a>' %
            (request.form.get('frontend_activation_link'), 'studente',
             new_user.token_verifica, new_user.id)
        )

    # printf("%s/studenti/%d", request.host, new_user.id)
    activation_link = '%s/studenti/%d' % (request.host, new_user.id)

    # TODO: capire se ha senso restiuire il token..
    return jsonify({'error': False, 'errormessage': '', 'activation_link': activation_link, 'token_verifica': new_user.token_verifica}), 200


# route usata per completare la registrazione di uno studente
@auth.route('/studenti/<id>', methods=['POST'])
def complete_signup_student(id):
    # controllo che la richiesta contenga tutte le informazioni obbligatorie
    if request.form.get('token_verifica') is None or\
            request.form.get('nome_istituto') is None or\
            request.form.get('indirizzo_istituto') is None or\
            request.form.get('indirizzo_di_studio') is None or\
            request.form.get('citta') is None:
        return jsonify({'error': True, 'errormessage': 'Sono necessarie ulteriori informazioni per completare la creazione dello studente'}), 404

    # controllo che non esista già uno studente con lo stesso id
    if Studente.query.filter(Studente.id == id).first():
        return jsonify({'error': True, 'errormessage': 'studente gia\' esistente'}), 404

    # controllo se esiste un utente con l'id passato
    user = Utente.query.filter(Utente.id == id).first()
    if user:
        # controllo che il token di verifica della mail sia corretto
        if user.token_verifica == request.form.get('token_verifica'):
            # creo nuovo studente
            new_student = Studente(id=id,
                                   nome_istituto=request.form.get(
                                       'nome_istituto'),
                                   indirizzo_istituto=request.form.get(
                                       'indirizzo_istituto'),
                                   indirizzo_di_studio=request.form.get(
                                       'indirizzo_di_studio'),
                                   citta=request.form.get('citta'))

            # setto come verificato l'account utente
            user.verificato = True

            # rendo effettive le modifiche sul db
            try:
                db.session.add(new_student)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': True, 'errormessage': 'Errore inserimento studente: ' + str(e)}), 500

            return jsonify({'error': False, 'errormessage': ''}), 200

    return jsonify({'error': True, 'errormessage': 'impossibile completare creazione studente'}), 404


# route usata per inserire un nuovo docente 
@auth.route('/docenti', methods=['POST'])
# blocco la route agli utenti loggati con ruolo amministratore
@token_required(restrict_to_roles=['amministratore'])
def signup_teacher(user):
    # controllo che la richiesta contenga tutte le informazioni obbligatorie
    if request.form.get('email') is None or\
            request.form.get('nome') is None or\
            request.form.get('cognome') is None or\
            request.form.get('data_nascita') is None:
        return jsonify({'error': True, 'errormessage': 'Sono necessarie ulteriori informazioni per creare il docente'}), 404

    # controllo che non esista già un utente con la stessa mail
    if Utente.query.filter(Utente.email == request.form.get('email')).first():
        return jsonify({'error': True, 'errormessage': 'utente gia\' esistente'}), 404

    # genero il token per la verifica della mail
    salt = ''.join(random.choice(string.printable) for i in range(16))
    token_salt = ''.join(random.choice(string.printable) for i in range(16))
    token = hmac.new(salt.encode(), token_salt.encode(),
                     hashlib.sha512).hexdigest()

    # creo il nuovo utente
    new_user = Utente(email=request.form.get('email'),
                      salt=salt,
                      nome=request.form.get('nome'),
                      cognome=request.form.get('cognome'),
                      data_nascita=request.form.get('data_nascita'),
                      token_verifica=token)

    # creo nuovo docente per evitare che uno studente possa attivarsi come docente cambiando la url di attivazione
    new_teacher = Docente(id=new_user.id)

    try:
        db.session.add_all([new_user, new_teacher])
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': True, 'errormessage': 'Errore inserimento utente: ' + str(e)}), 404
    
    # invio mail per verifica validità indirizzo se richiesta
    if request.form.get('frontend_activation_link') is not None:
        send_mail(
            [new_user.email],
            'Confirm your email',
            'To verify your email please press this button: <a href="%s/%s/%s/%d">Confirm your email</a>' %
            (request.form.get('frontend_activation_link'), 'docente',
             new_user.token_verifica, new_user.id)
        )

    activation_link = '%s/docenti/%d' % (request.host, new_user.id)

    return jsonify({'error': False, 'errormessage': '', 'activation_link': activation_link, 'token_verifica': new_user.token_verifica}), 200


# route usata per completare la registrazione di un nuovo docente
@auth.route('/docenti/<id>', methods=['POST'])
def complete_signup_teacher(id):
    # controllo che la richiesta contenga tutte le informazioni obbligatorie
    if request.form.get('token_verifica') is None or\
            request.form.get('password') is None:
        return jsonify({'error': True, 'errormessage': 'Sono necessarie ulteriori informazioni per completare la creazione del docente'}), 404

    # controllo che esista l'utente
    user = Utente.query.filter(Utente.id == id).first()
    # controllo che esista il docente
    teacher = Docente.query.filter(Docente.id == id).first()
    
    if user and teacher:
        if user.token_verifica == request.form.get('token_verifica'):
            # creo digest password
            digest = hmac.new(user.salt.encode(), request.form.get(
                'password').encode(), hashlib.sha512).hexdigest()
            user.digest = digest

            # salvo file immagine_profilo se caricato
            path_to_immagine_profilo = None
            if 'immagine_profilo' in request.files:
                file = request.files['immagine_profilo']
                # controllo se il file è valido
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    path_to_immagine_profilo = os.path.join(
                        current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(path_to_immagine_profilo)
            
            # aggiorno i dati del docente
            teacher.descrizione_docente = request.form.get(
                'descrizione_docente')
            teacher.immagine_profilo = path_to_immagine_profilo
            teacher.link_pagina_docente = request.form.get(
                'link_pagina_docente')

            user.verificato = True

            try:
                db.session.add(teacher)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': True, 'errormessage': 'Errore inserimento docente: ' + str(e)}), 500

            return jsonify({'error': False, 'errormessage': ''}), 200

    return jsonify({'error': True, 'errormessage': 'impossibile completare creazione docente'}), 404


# route usata per inserire un nuovo amministratore
@auth.route('/amministratori/<id>', methods=['POST'])
# blocco la route agli utenti loggati con ruolo amministratore
@token_required(restrict_to_roles=['amministratore'])
def add_administrator(user, id):
    # controllo che esista un docente con l'id passato
    if Docente.query.filter(Docente.id == id).first():
        # creo il nuovo amministratore
        new_administrator = Amministratore(id=id)

        try:
            db.session.add(new_administrator)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': True, 'errormessage': 'Errore inserimento amministratore: ' + str(e)}), 404

        return jsonify({'error': False, 'errormessage': ''}), 200

    return jsonify({'error': True, 'errormessage': 'Docente inesistente'})


# route usata per loggare un utente
@auth.route('/login', methods=['GET'])
def login():
    # verifico che siano stati passati username e password (tramite basic auth)
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({'error': True, 'errormessage': 'Autenticazione richiesta'}), 401

    email = auth.username
    password = auth.password

    # reperisco l'utente
    user = Utente.query.filter(Utente.email == email).first()
    if not user or user.abilitato == False or user.verificato == False:
        return jsonify({'error': True, 'errormessage': 'Autenticaione fallita'}), 401

    # definisco il token jwt (json web token)
    token_data = {
        'id': user.id,
        'email': user.email,
        'nome': user.nome,
        'cognome': user.cognome,
        'data_nascita': user.data_nascita.strftime('%m/%d/%Y'),
        'exp': datetime.utcnow() + timedelta(minutes=60)
    }

    studente = Studente.query.filter(Studente.id == user.id).first()
    docente = Docente.query.filter(Docente.id == user.id).first()
    roles = []
    if studente:
        token_data['nome_istituto'] = studente.nome_istituto
        token_data['indirizzo_istituto'] = studente.indirizzo_istituto
        token_data['indirizzo_di_studio'] = studente.indirizzo_di_studio
        token_data['citta'] = studente.citta
        roles.append('studente')
    else:
        token_data['descrizione_docente'] = docente.descrizione_docente
        token_data['immagine_profilo'] = docente.immagine_profilo
        token_data['link_pagina_docente'] = docente.link_pagina_docente
        roles.append('docente')

    amministratore = Amministratore.query.filter(
        Amministratore.id == user.id).first()
    if amministratore:
        roles.append('amministratore')

    token_data['roles'] = roles

    # verifico che la password corrisponda
    if hmac.new(user.salt.encode(), password.encode(), hashlib.sha512).hexdigest() == user.digest:
        # codifico il token
        token = jwt.encode(token_data, current_app.config['SECRET_KEY'])

        return jsonify({'error': False, 'errormessage': '', 'token': token}), 200

    return jsonify({'error': True, 'errormessage': 'Autenticaione fallita'}), 401
