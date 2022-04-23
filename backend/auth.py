import random
import string
import hmac
import hashlib
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, jsonify, request, current_app

from .models import Utente, Studente, Docente, Amministratore
from .mail import send_mail
from . import db

auth = Blueprint('auth', __name__)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'error': True, 'errormessage': 'Token mancante'}), 401

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            current_user = Utente.query\
                .filter(Utente.id == data['id'])\
                .first()
        except:
            return jsonify({
                'error': True,
                'errormessage': 'Token invalido'
            }), 401
        # returns the current logged in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated


@auth.route('/students', methods=['POST'])
def signup():
    if request.form.get('email') is None or\
            request.form.get('password') is None or\
            request.form.get('nome') is None or\
            request.form.get('cognome') is None or\
            request.form.get('data_nascita') is None:
        return jsonify({'error': True, 'errormessage': 'Sono necessarie ulteriori informazioni per creare lo studente'}), 404

    if Utente.query.filter(Utente.email == request.form.get('email')).first():
        return jsonify({'error': True, 'errormessage': 'utente gia\' esistente'}), 404

    salt = ''.join(random.choice(string.printable) for i in range(16))
    digest = hmac.new(salt.encode(), request.form.get(
        'password').encode(), hashlib.sha512).hexdigest()

    token_salt = ''.join(random.choice(string.printable) for i in range(16))
    token = hmac.new(salt.encode(), token_salt.encode(),
                     hashlib.sha512).hexdigest()
    new_user = Utente(email=request.form.get('email'),
                      salt=salt,
                      digest=digest,
                      nome=request.form.get('nome'),
                      cognome=request.form.get('cognome'),
                      data_nascita=request.form.get('data_nascita'),
                      token_verifica=token)

    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': False, 'errormessage': 'Errore inserimento utente: ' + str(e)}), 404

    # send_mail([request.form.get('email')],
    #          'Verifica indirizzo mail',
    #          'Accedi al seguente <a href="">link</a> per verificare la mail e completare il tuo account')

    return jsonify({'error': False, 'errormessage': ''}), 200


@auth.route('/students/<id>', methods=['POST'])
def complete_signup(id):
    if request.form.get('token_verifica') is None or\
            request.form.get('nome_istituto') is None or\
            request.form.get('indirizzo_istituto') is None or\
            request.form.get('indirizzo_di_studio') is None or\
            request.form.get('citta') is None:
        return jsonify({'error': True, 'errormessage': 'Sono necessarie ulteriori informazioni per completare la creazione dello studente'}), 404

    if Studente.query.filter(Studente.id == id).first():
        return jsonify({'error': True, 'errormessage': 'studente gia\' esistente'}), 404

    user = Utente.query.filter(Utente.id == id).first()
    if user:
        if user.token_verifica == request.form.get('token_verifica'):
            new_student = Studente(id=id,
                                   nome_istituto=request.form.get(
                                       'nome_istituto'),
                                   indirizzo_istituto=request.form.get(
                                       'indirizzo_istituto'),
                                   indirizzo_di_studio=request.form.get(
                                       'indirizzo_di_studio'),
                                   citta=request.form.get('citta'))
            
            user.verificato = True

            try:
                db.session.add(new_student)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({'error': True, 'errormessage': 'Errore inserimento studente: ' + str(e)}), 500

            return jsonify({'error': False, 'errormessage': ''}), 200

    return jsonify({'error': True, 'errormessage': 'impossibile completare creazione studente'}), 404


@auth.route('/login', methods=['POST'])
def login():
    email = request.authorization["username"]
    password = request.authorization["password"]

    user = Utente.query.filter(Utente.email == email).first()
    if not user or user.abilitato == False or user.verificato == False:
        return jsonify({'error': True, 'errormessage': 'Autenticaione fallita 1'}), 401

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
        
    amministratore = Amministratore.query.filter(Amministratore.id == user.id).first()
    if amministratore:
        roles.append('amministratore')
        
    token_data['roles'] = roles
    
    if hmac.new(user.salt.encode(), password.encode(), hashlib.sha512).hexdigest() == user.digest:
        token = jwt.encode(token_data, current_app.config['SECRET_KEY'])

        return jsonify({'error': False, 'errormessage': '', 'token': token}), 200

    return jsonify({'error': True, 'errormessage': 'Autenticaione fallita'}), 401
