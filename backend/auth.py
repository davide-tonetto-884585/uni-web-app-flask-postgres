import random
import string
import hmac
import hashlib
from flask import Blueprint, jsonify, request

from .models import Utente, Studente
from .mail import send_mail
from . import db

auth = Blueprint('auth', __name__)


@auth.route('/students', methods=['POST'])
def signup():
    if request.form.get('email') is None or\
            request.form.get('password') is None or\
            request.form.get('nome') is None or\
            request.form.get('cognome') is None or\
            request.form.get('data_nascita') is None:
        return jsonify({'error': 'true', 'errormessage': 'Sono necessarie ulteriori informazioni per creare lo studente'})

    if Utente.query.filter_by(email=request.form.get('email')).first():
        return jsonify({'error': 'true', 'errormessage': 'utente gia\' esistente'})

    salt = ''.join(random.choice(string.printable) for i in range(16))
    digest = hmac.new(salt.encode(), request.form.get(
        'password').encode(), hashlib.sha512).hexdigest()

    token_salt = ''.join(random.choice(string.printable) for i in range(16))
    token = hmac.new(salt.encode(), token_salt.encode(),
                     hashlib.sha512).hexdigest()
    new_user = Utente(email=request.form.get('email'),
                      salt=salt.encode(),
                      digest=digest,
                      nome=request.form.get('nome'),
                      cognome=request.form.get('cognome'),
                      data_nascita=request.form.get('data_nascita'),
                      token_verifica=token)

    try:
        db.session.add(new_user)
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({'error': 'true', 'errormessage': 'Errore inserimento utente'})

    # send_mail([request.form.get('email')],
    #          'Verifica indirizzo mail',
    #          'Accedi al seguente <a href="">link</a> per verificare la mail e completare il tuo account')

    return jsonify({'status': 200, 'error': 'false', 'errormessage': ''})


@auth.route('/students/<id>', methods=['POST'])
def complete_signup(id):
    if request.form.get('token_verifica') is None or\
            request.form.get('nome_istituto') is None or\
            request.form.get('indirizzo_istituto') is None or\
            request.form.get('indirizzo_di_studio') is None or\
            request.form.get('citta') is None:
        return jsonify({'error': 'true', 'errormessage': 'Sono necessarie ulteriori informazioni per completare la creazione dello studente'})

    user = Utente.query.filter_by(id=id).one()
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

            db.session.add(new_student)
            db.session.commit()

            return jsonify({'status': 200, 'error': 'false', 'errormessage': ''})

    return jsonify({'error': 'true', 'errormessage': 'impossibile completare creazione studente'})


@auth.route('/login')
def login():
    return 'Login'


@auth.route('/logout')
def logout():
    return 'Logout'
