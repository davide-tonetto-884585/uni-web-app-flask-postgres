# from pydoc import Doc, doc
import random
import string
import hmac
import hashlib
import jwt  # PyJWT
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, jsonify, request, current_app

from ..model.marshmallow_models import StudenteSchema, DocenteSchema, UtenteSchema
from ..model.models import Utente, Studente, Docente, Amministratore
from ..utils import send_mail, load_file
from .. import PreLoginSession, SessionAmministratori, SessionDocenti, SessionStudenti

""" preLoginSession = PreLoginSession()
sessionAmministratori = SessionAmministratori()
SessionDocenti = SessionDocenti() """

auth = Blueprint('auth', __name__)

#studenti_schema = StudenteSchema(many=True)
studente_schema = StudenteSchema()
docente_schema = DocenteSchema()
utenti_schema = UtenteSchema(many=True)
utente_schema = UtenteSchema()

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
                arr = auth_header.split(" ")
                if len(arr) > 1:
                    token = arr[1]

            # return 401 if token is not passed
            if not token:
                return jsonify({'error': True, 'errormessage': 'Missing token'}), 401

            try:
                # decoding the payload to fetch the stored details
                user_data = jwt.decode(
                    token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                #current_user = Utente.query.filter(Utente.id == user_data['id']).first()

                # se sono stati passati ruoli allora controllo che l'utente soddisfi i requisiti
                satisfied = False
                for allowed_role in restrict_to_roles:
                    if allowed_role in user_data['roles']:
                        satisfied = True
                        break

                if not satisfied:
                    return jsonify({'error': True, 'errormessage': 'Unauthorized'}), 401
            except Exception as e:
                return jsonify({
                    'error': True,
                    'errormessage': 'Invalid token: ' + str(e)
                }), 400

            # returns the current logged in users contex to the routes
            return f(user_data, *args, **kwargs)

        return decorated

    return decorator


# route usata per aggiungere un nuovo studente
@auth.route('/utenti/studenti', methods=['POST'])
def signup_student():
    with PreLoginSession() as preLoginSession:
        preLoginSession.begin()

        # controllo che la richiesta contenga tutte le informazioni obbligatorie
        if request.form.get('email') is None or\
                request.form.get('password') is None or\
                request.form.get('nome') is None or\
                request.form.get('cognome') is None or\
                request.form.get('data_nascita') is None:
            return jsonify({'error': True, 'errormessage': 'You must provide more information in order to create a new student'}), 400

        # controlle che non esista già un utente con la stessa email
        if preLoginSession.query(Utente).filter(Utente.email == request.form.get('email')).first():
            return jsonify({'error': True, 'errormessage': 'Already exixsting user'}), 409

        # genero un salt randomico per rendere la password illeggibile da database
        salt = ''.join(random.choice(string.printable) for i in range(16))
        # creo il digest della password da salvare nel database
        digest = hmac.new(salt.encode(), request.form.get(
            'password').encode(), hashlib.sha512).hexdigest()

        # genero il token usato per verificare che la mial dell'utente sia valida
        token_salt = ''.join(random.choice(string.printable)
                             for i in range(16))
        token = hmac.new(salt.encode(), token_salt.encode(),
                         hashlib.sha512).hexdigest()

        # creo il nuovo utente con le informazioni ottenute
        new_user = Utente(email=request.form.get('email'),
                          salt=salt,
                          digest=digest,
                          nome=request.form.get('nome'),
                          cognome=request.form.get('cognome'),
                          data_nascita=request.form.get('data_nascita'),
                          sesso=request.form.get('sesso'),
                          token_verifica=token)

        # inserisco i dati nel database
        try:
            preLoginSession.add(new_user)
            preLoginSession.commit()
        except Exception as e:
            preLoginSession.rollback()
            return jsonify({'error': True, 'errormessage': 'User insertion error: ' + str(e)}), 500

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
@auth.route('/utenti/studenti/<id>', methods=['POST'])
def complete_signup_student(id):
    with PreLoginSession() as preLoginSession:
        preLoginSession.begin()

        # controllo che la richiesta contenga tutte le informazioni obbligatorie
        if request.form.get('token_verifica') is None or\
                request.form.get('indirizzo_di_studio') is None or\
                request.form.get('id_scuola') is None:
            return jsonify({'error': True, 'errormessage': 'You must provide more information in order to create a new student'}), 404

        # controllo che non esista già uno studente con lo stesso id
        if preLoginSession.query(Studente).filter(Studente.id == id).first():
            return jsonify({'error': True, 'errormessage': 'Already exixsting user'}), 409

        # controllo se esiste un utente con l'id passato
        user = preLoginSession.query(Utente).filter(Utente.id == id).first()
        if user:
            # controllo che il token di verifica della mail sia corretto
            if user.token_verifica == request.form.get('token_verifica'):
                # creo nuovo studente
                new_student = Studente(id=id,
                                       id_scuola=request.form.get('id_scuola'),
                                       indirizzo_di_studio=request.form.get(
                                           'indirizzo_di_studio'))

                # setto come verificato l'account utente
                user.verificato = True

                # rendo effettive le modifiche sul db
                try:
                    preLoginSession.add(new_student)
                    preLoginSession.commit()
                except Exception as e:
                    preLoginSession.rollback()
                    return jsonify({'error': True, 'errormessage': 'user insertion error: ' + str(e)}), 500

                return jsonify({'error': False, 'errormessage': ''}), 200

        return jsonify({'error': True, 'errormessage': 'Cannot complete user creation'}), 400


# route usata per inserire un nuovo docente
@auth.route('/utenti/docenti', methods=['POST'])
# blocco la route agli utenti loggati con ruolo amministratore
@token_required(restrict_to_roles=['amministratore'])
def signup_teacher(user):
    with SessionAmministratori() as sessionAmministratori:
        sessionAmministratori.begin()
        # controllo che la richiesta contenga tutte le informazioni obbligatorie
        if request.form.get('email') is None or\
                request.form.get('nome') is None or\
                request.form.get('cognome') is None or\
                request.form.get('data_nascita') is None:
            return jsonify({'error': True, 'errormessage': 'You must provide more information in order to create a new teacher'}), 400

        # controllo che non esista già un utente con la stessa mail
        if sessionAmministratori.query(Utente).filter(Utente.email == request.form.get('email')).first():
            return jsonify({'error': True, 'errormessage': 'Already existing user'}), 409

        # genero il token per la verifica della mail
        salt = ''.join(random.choice(string.printable) for i in range(16))
        token_salt = ''.join(random.choice(string.printable)
                             for i in range(16))
        token = hmac.new(salt.encode(), token_salt.encode(),
                         hashlib.sha512).hexdigest()

        # creo il nuovo utente
        new_user = Utente(email=request.form.get('email'),
                          salt=salt,
                          nome=request.form.get('nome'),
                          cognome=request.form.get('cognome'),
                          data_nascita=request.form.get('data_nascita'),
                          sesso=request.form.get('sesso'),
                          token_verifica=token)

        try:
            sessionAmministratori.add(new_user)
            sessionAmministratori.flush()

            # creo nuovo docente per evitare che uno studente possa attivarsi come docente cambiando la url di attivazione
            sessionAmministratori.refresh(new_user)
            new_teacher = Docente(id=new_user.id)
            sessionAmministratori.add(new_teacher)

            sessionAmministratori.commit()
        except Exception as e:
            sessionAmministratori.rollback()
            return jsonify({'error': True, 'errormessage': 'User insertion error: ' + str(e)}), 500

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
@auth.route('/utenti/docenti/<id>', methods=['POST'])
def complete_signup_teacher(id):
    with PreLoginSession() as preLoginSession:
        preLoginSession.begin()

        # controllo che la richiesta contenga tutte le informazioni obbligatorie
        if request.form.get('token_verifica') is None or\
                request.form.get('password') is None:
            return jsonify({'error': True, 'errormessage': 'You must provide more information in order to create a new teacher'}), 400

        # controllo che esista l'utente
        user = preLoginSession.query(Utente).filter(Utente.id == id).first()
        # controllo che esista il docente
        teacher = preLoginSession.query(
            Docente).filter(Docente.id == id).first()

        if user and teacher:
            if user.token_verifica == request.form.get('token_verifica'):
                # creo digest password
                digest = hmac.new(user.salt.encode(), request.form.get(
                    'password').encode(), hashlib.sha512).hexdigest()
                user.digest = digest

                # salvo file immagine_profilo se caricato
                path_to_immagine_profilo = load_file('immagine_profilo')

                # aggiorno i dati del docente
                teacher.descrizione_docente = request.form.get(
                    'descrizione_docente')
                teacher.immagine_profilo = path_to_immagine_profilo
                teacher.link_pagina_docente = request.form.get(
                    'link_pagina_docente')

                user.verificato = True

                try:
                    preLoginSession.add(teacher)
                    preLoginSession.commit()
                except Exception as e:
                    preLoginSession.rollback()
                    return jsonify({'error': True, 'errormessage': 'Teacher insertion error: ' + str(e)}), 500

                return jsonify({'error': False, 'errormessage': ''}), 200

        return jsonify({'error': True, 'errormessage': 'Cannot complete teacher creation'}), 400


# route usata per inserire un nuovo amministratore
@auth.route('/utenti/amministratori/<id>', methods=['POST'])
# blocco la route agli utenti loggati con ruolo amministratore
@token_required(restrict_to_roles=['amministratore'])
def add_administrator(user, id):
    with SessionAmministratori() as sessionAmministratori:
        sessionAmministratori.begin()

        # controllo che esista un docente con l'id passato
        if sessionAmministratori.query(Docente).filter(Docente.id == id).first():
            # creo il nuovo amministratore
            new_administrator = Amministratore(id=id)

            try:
                sessionAmministratori.add(new_administrator)
                sessionAmministratori.commit()
            except Exception as e:
                sessionAmministratori.rollback()
                return jsonify({'error': True, 'errormessage': 'Admin insertion error: ' + str(e)}), 500

            return jsonify({'error': False, 'errormessage': ''}), 200

        return jsonify({'error': True, 'errormessage': 'Teacher not find'})


# route usata per loggare un utente
@auth.route('/login', methods=['GET'])
def login():
    with PreLoginSession() as preLoginSession, preLoginSession.begin():

        # verifico che siano stati passati username e password (tramite basic auth)
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return jsonify({'error': True, 'errormessage': 'Missing authentication informaion'}), 401

        email = auth.username
        password = auth.password

        try:
            # reperisco l'utente
            user = preLoginSession.query(Utente).filter(
                Utente.email == email).first()
            if not user or user.abilitato == False or user.verificato == False:
                return jsonify({'error': True, 'errormessage': 'Authentication failed'}), 401

            # definisco il token jwt (json web token)
            token_data = {
                'id': user.id,
                'email': user.email,
                'nome': user.nome,
                'cognome': user.cognome,
                'data_nascita': user.data_nascita.strftime('%m/%d/%Y'),
                'exp': datetime.utcnow() + timedelta(minutes=120)
            }

            studente = preLoginSession.query(Studente).filter(
                Studente.id == user.id).first()
            docente = preLoginSession.query(Docente).filter(
                Docente.id == user.id).first()
            roles = []
            if studente:
                token_data['id_scuola'] = studente.id_scuola
                token_data['indirizzo_di_studio'] = studente.indirizzo_di_studio
                roles.append('studente')
            else:
                token_data['descrizione_docente'] = docente.descrizione_docente
                token_data['immagine_profilo'] = docente.immagine_profilo
                token_data['link_pagina_docente'] = docente.link_pagina_docente
                roles.append('docente')

            amministratore = preLoginSession.query(Amministratore).filter(
                Amministratore.id == user.id).first()
            if amministratore:
                roles.append('amministratore')

            token_data['roles'] = roles

            # verifico che la password corrisponda
            if hmac.new(user.salt.encode(), password.encode(), hashlib.sha512).hexdigest() == user.digest:
                # codifico il token
                token = jwt.encode(
                    token_data, current_app.config['SECRET_KEY'])

                return jsonify({'error': False, 'errormessage': '', 'token': token}), 200

            return jsonify({'error': True, 'errormessage': 'Authentication failed'}), 401

        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Error during authentication: ' + str(e)}), 500


# ritorna tutti gli studenti
@auth.route('/utenti/studenti', methods=['GET'])
# ruoli che possono eseguire questa funzione
@token_required(restrict_to_roles=['amministratore', 'docente'])
def get_students(user):
    with SessionDocenti() as sessionDocenti, sessionDocenti.begin():

        # Parametri del form
        skip = request.args.get('skip')
        limit = request.args.get('limit')
        name = request.args.get('name')
        surname = request.args.get('surname')

        try:
            # Query per recuperare tutte le aule
            studenti = sessionDocenti.\
                query(Utente.id, Utente.nome, Utente.cognome, Studente.indirizzo_di_studio).\
                join(Utente, Utente.id == Studente.id).order_by(
                    Utente.cognome, Utente.nome)

            # Filtri per specializzazre la ricerca e/o la visualizzazione degli studenti
            if name is not None:
                studenti = studenti.filter(Utente.nome.like('%' + name + '%'))
            if surname is not None:
                studenti = studenti.filter(
                    Utente.cognome.like('%' + surname + '%'))
            if skip is not None:
                studenti = studenti.offset(skip)
            if limit is not None:
                studenti = studenti.limit(limit)

            studenti = studenti.all()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Error in finding students: ' + str(e)}), 500

        return jsonify(json.loads(json.dumps([dict(studente._mapping) for studente in studenti]))), 200


# ritorna uno specifico studente in base al suo id
@auth.route('/utenti/studenti/<id>', methods=['GET'])
# ruoli che possono eseguire questa funzione
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def get_student(user, id):
    with SessionDocenti() as sessionDocenti, sessionDocenti.begin():
        if 'studente' in user['roles'] and user['id'] != int(id):
            return jsonify({'error': True, 'errormessage': 'Permission denied'}), 401
        
        # Query per recuperare lo studente
        studente = sessionDocenti.query(Studente).filter(Studente.id == id)

        # prova a reperire lo studente dalla query
        try:
            studente = studente.first()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Error in finding student: ' + str(e)}), 500

        if studente is None:
            # Se non trova lo studente, ritorna uno status code 404
            return jsonify({'error': True, 'errormessage': 'Student not found'}), 404
        else:
            return jsonify(studente_schema.dump(studente)), 200


# ritorna tutti i docenti
@auth.route('/utenti/docenti', methods=['GET'])
def get_docenti():
    with PreLoginSession() as preLoginSession, preLoginSession.begin():

        # Parametri del form
        skip = request.args.get('skip')
        limit = request.args.get('limit')
        name = request.args.get('name')
        surname = request.args.get('surname')

        try:
            # Query per recuperare tutte le aule
            docenti = preLoginSession.\
                query(Utente.id, Utente.nome, Utente.cognome, Docente.descrizione_docente, Docente.immagine_profilo, Docente.link_pagina_docente).\
                join(Utente, Utente.id == Docente.id).order_by(
                    Utente.cognome, Utente.nome)

            # Filtri per specializzazre la ricerca e/o la visualizzazione dei docenti
            if name is not None:
                docenti = docenti.filter(Utente.nome.like('%' + name + '%'))
            if surname is not None:
                docenti = docenti.filter(
                    Utente.cognome.like('%' + surname + '%'))
            if skip is not None:
                docenti = docenti.offset(skip)
            if limit is not None:
                docenti = docenti.limit(limit)

            docenti = docenti.all()
        # Se non trova alcun docente, ritorna uno status code 404
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Error in finding teachers: ' + str(e)}), 500

        return jsonify(json.loads(json.dumps([dict(docente._mapping) for docente in docenti]))), 200


# ritorna uno specifico docente in base al suo id
@auth.route('/utenti/docenti/<id>', methods=['GET'])
def get_docente(id):
    with PreLoginSession() as preLoginSession, preLoginSession.begin():

        # Query per recuperare il docente
        docente = preLoginSession.query(Docente).filter(Docente.id == id)

        # prova a reperire il docente dalla query
        try:
            docente = docente.first()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Error in finding teacher: ' + str(e)}), 500

        # Se non trova il docente, ritorna uno status code 404
        if docente is None:
            return jsonify({'error': True, 'errormessage': 'Teacher not found'}), 404
        else:
            return jsonify(docente_schema.dump(docente)), 200


# ritorna tutti gli utenti
@auth.route('/utenti', methods=['GET'])
# ruoli che possono eseguire questa funzione
@token_required(restrict_to_roles=['amministratore'])
def get_users(user):
    with SessionDocenti() as sessionDocenti, sessionDocenti.begin():

        # Parametri del form
        skip = request.args.get('skip')
        limit = request.args.get('limit')
        name = request.args.get('name')
        surname = request.args.get('surname')
        birthdate = request.args.get('birthdate')

        try:
            # Query per recuperare tutti gli utenti
            utenti = sessionDocenti.query(Utente).order_by(
                Utente.cognome, Utente.nome)

            # Filtri per specializzazre la ricerca e/o la visualizzazione degli utenti
            if name is not None:
                utenti = utenti.filter(Utente.nome.like('%' + name + '%'))
            if surname is not None:
                utenti = utenti.filter(
                    Utente.cognome.like('%' + surname + '%'))
            if birthdate is not None:
                utenti = utenti.filter(Utente.date_time == birthdate)
            if skip is not None:
                utenti = utenti.offset(skip)
            if limit is not None:
                utenti = utenti.limit(limit)

            utenti = utenti.all()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Cannot get users: ' + str(e)}), 500

        return jsonify(utenti_schema.dump(utenti.all())), 200


# ritorna un utente specifico in base al suo id
@auth.route('/utenti/<id>', methods=['GET'])
def get_user(id):
    with SessionDocenti() as sessionDocenti, sessionDocenti.begin():
        # Query per recuperare l'utente
        utente = sessionDocenti.query(Utente).filter(Utente.id == id)

        # prova a reperire l'utente dalla query
        try:
            utente = utente.first()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Error in finding user: ' + str(e)}), 404

        # Se non trova l'utente, ritorna uno status code 404
        if utente is None:
            return jsonify({'error': True, 'errormessage': 'User not found'}), 404
        else:
            return jsonify(utente_schema.dump(utente)), 200


# update studente
@auth.route('/utenti/studenti/<id>', methods=['PUT'])
@token_required(restrict_to_roles=['amministratore', 'studente'])
def update_studente(user, id):
    with SessionStudenti() as sessionStudenti:
        if 'studente' in user['roles'] and user['id'] != int(id):
            return jsonify({'error': True, 'errormessage': 'Permission denied'}), 401
        
        utente = sessionStudenti.query(Utente).filter(Utente.id == id).first()
        studente = sessionStudenti.query(Studente).filter(Studente.id == id).first()
        
        if request.form.get('nome') is not None:
            utente.nome = request.form.get('nome')
            
        if request.form.get('cognome') is not None:
            utente.cognome = request.form.get('cognome')
            
        if request.form.get('indirizzo_di_studio') is not None:
            studente.indirizzo_di_studio = request.form.get('indirizzo_di_studio')
            
        if request.form.get('id_scuola') is not None:
            studente.id_scuola = request.form.get('id_scuola')
            
        try: 
            sessionStudenti.commit()
        except Exception as e:
            sessionStudenti.rollback()
            return jsonify({'error': True, 'errormessage': 'Student information update error: ' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200
            
            
# update docente
@auth.route('/utenti/docenti/<id>', methods=['PUT'])
@token_required(restrict_to_roles=['amministratore', 'docente'])
def update_docente(user, id):
    with SessionDocenti() as sessionDocenti:
        if 'docente' in user['roles'] and user['id'] != int(id):
            return jsonify({'error': True, 'errormessage': 'Permission deny'}), 401
        
        utente = sessionDocenti.query(Utente).filter(Utente.id == id).first()
        docente = sessionDocenti.query(Docente).filter(Docente.id == id).first()
        
        if request.form.get('nome') is not None:
            utente.nome = request.form.get('nome')
            
        if request.form.get('cognome') is not None:
            utente.cognome = request.form.get('cognome')
            
        if request.form.get('descrizione_docente') is not None:
            docente.descrizione_docente = request.form.get('descrizione_docente')
            
        if request.form.get('link_pagina_docente') is not None:
            docente.link_pagina_docente = request.form.get('link_pagina_docente')
            
        immagine_profilo = load_file('immagine_profilo')
        if immagine_profilo is not None:
            docente.immagine_profilo = immagine_profilo
            
        try: 
            sessionDocenti.commit()
        except Exception as e:
            sessionDocenti.rollback()
            return jsonify({'error': True, 'errormessage': 'Teacher information update error: ' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200
