import json
from flask import Blueprint, jsonify, request
from sqlalchemy import func, desc
from sqlalchemy.sql.functions import coalesce

from .. import PreLoginSession, SessionDocenti, SessionAmministratori, SessionStudenti
from ..model.marshmallow_models import DomandeCorsoSchema, LikeDomandaSchema
from .auth import token_required
from ..model.models import DomandeCorso, LikeDomanda, DocenteCorso, Utente

domande = Blueprint('domande_corso', __name__)

""" preLoginSession = PreLoginSession()
sessionDocenti = SessionDocenti()
sessionAmministratori = SessionAmministratori()
sessionStudenti = SessionStudenti() """

domande_corso_schema = DomandeCorsoSchema(many=True)
domanda_corso_schema = DomandeCorsoSchema()
likes_domanda_schema = LikeDomandaSchema(many=True)
like_domanda_schema = LikeDomandaSchema()


@domande.route('/corsi/<id>/domande', methods=['GET'])
def get_domande(id):
    with SessionStudenti() as sessionStudenti, sessionStudenti.begin():
        
        # Parametri del form
        testo = request.args.get('testo')
        chiusa = request.args.get('chiusa')
        skip = request.args.get('skip')
        limit = request.args.get('limit')
        order_by = request.args.get('order_by')

        try:
            # Query per reperire le domande con il relativo numero dei like
            sub_count = sessionStudenti.query(LikeDomanda.id_domanda_corso, func.count().label('tl')).\
                group_by(LikeDomanda.id_domanda_corso).subquery()
            domande = sessionStudenti.query(Utente.nome, Utente.cognome, DomandeCorso.id_utente, DomandeCorso.id, DomandeCorso.id_corso, DomandeCorso.timestamp,
                                            DomandeCorso.chiusa, DomandeCorso.testo, coalesce(sub_count.c.tl, 0).label('total_likes')).\
                join(Utente, DomandeCorso.id_utente == Utente.id).\
                outerjoin(sub_count, sub_count.c.id_domanda_corso == DomandeCorso.id).\
                filter(DomandeCorso.id_corso == id).\
                filter(DomandeCorso.id_domanda_corso == None)

            # Filtri per la specializzazione della ricerca o visualizzazione dei corsi
            if testo is not None:
                domande = domande.filter(
                    DomandeCorso.testo.like('%' + testo + '%'))
            if chiusa is not None:
                domande = domande.filter(DomandeCorso.chiusa == (
                    True if chiusa == 'true' else False))
                
            count = domande.count()

            if order_by == 'like':
                domande = domande.order_by(desc('total_likes'))

            domande = domande.order_by(desc(DomandeCorso.timestamp))

            if skip is not None:
                domande = domande.offset(skip)
            if limit is not None:
                domande = domande.limit(limit)

            domande = domande.all()

        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Error in retrieving questions: ' + str(e)}), 500

        return jsonify({ 'domande': json.loads(json.dumps([dict(domanda._mapping) for domanda in domande], default=str)), 'count': count }), 200


@domande.route('/corsi/<id>/domande/<id_domanda>/risposte', methods=['GET'])
def get_risposte_domanda(id, id_domanda):
    with SessionStudenti() as sessionStudenti, sessionStudenti.begin():
        try:
            # Query per reperire le domande con il relativo numero dei like
            domande = sessionStudenti.query(Utente.nome, Utente.cognome, DomandeCorso.id_utente, DomandeCorso.id, DomandeCorso.id_corso, DomandeCorso.timestamp,
                                            DomandeCorso.chiusa, DomandeCorso.testo).\
                join(Utente, DomandeCorso.id_utente == Utente.id).\
                filter(DomandeCorso.id_corso == id).\
                filter(DomandeCorso.id_domanda_corso == id_domanda).\
                order_by(DomandeCorso.timestamp)

            domande = domande.all()

        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Error in retrieving questions: ' + str(e)}), 500

        return jsonify(json.loads(json.dumps([dict(domanda._mapping) for domanda in domande], default=str))), 200


@domande.route('/corsi/<id>/domande', methods=['POST'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def add_domande(user, id):
    with SessionStudenti() as sessionStudenti:
        sessionStudenti.begin()
        # controllo che i campi obbligatori siano stati inseriti nel form (id_domanda_corso non è obbligatorio)
        testo = request.form.get('testo')
        # ID della domanda da rispondere
        id_domanda_corso = request.form.get('id_domanda_corso')
        chiusa = False

        # Controlla che i campi obbligatori siano stati inseriti nel form
        # NOTA: Solo i docenti del corso possono "chiudere le domande"
        if testo is None:
            return jsonify({'error': True, 'errormessage': 'Missing information'}), 400

        if ('docenti' in user['roles']):
            id_docenti_corso = sessionStudenti.query(
                DocenteCorso.id_docente).filter(DocenteCorso.id_corso == id).all()

            if ((int(user['id']), ) in id_docenti_corso or 'amministratore' in user['roles']):
                chiusa = False if request.form.get(
                    'chiusa') is None else request.form.get('chiusa')

        # Controlla che la domanda a cui si vuole rispondere esista
        if id_domanda_corso is not None:
            try:
                id_domande_corso = sessionStudenti.query(DomandeCorso.id).\
                    filter(DomandeCorso.id_corso == id).all()
            except Exception as e:
                return jsonify({'error': True, 'errormessage': 'Error in inserting the answer: ' + str(e)}), 500

            if ((int(id_domanda_corso),) not in id_domande_corso):
                return jsonify({'error': True, 'errormessage': 'Question not found'}), 400

        # creazione del nuovo oggetto da inserire
        new_domanda_corso = DomandeCorso(testo=testo, chiusa=chiusa, id_corso=id,
                                        id_utente=user['id'], id_domanda_corso=id_domanda_corso)

        # prova di inserimento della nuova domanda
        try:
            sessionStudenti.add(new_domanda_corso)
            sessionStudenti.commit()
        except Exception as e:
            sessionStudenti.rollback()
            return jsonify({'error': True, 'errormessage': 'Error in entering the question: ' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200


@domande.route('/corsi/<id>/domande/<id_domanda>', methods=['PUT'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def update_domande(user, id, id_domanda):
    with SessionStudenti() as sessionStudenti:
        sessionStudenti.begin()
        # controllo che i campi obbligatori siano stati inseriti nel form (id_domanda_corso non è obbligatorio)
        testo = request.form.get('testo')
        # ID della domanda da rispondere
        id_domanda_corso = request.form.get('id_domanda_corso')
        chiusa = request.form.get('chiusa')

        if ('docenti' in user['roles']):
            id_docenti_corso = sessionStudenti.query(
                DocenteCorso.id_docente).filter(DocenteCorso.id_corso == id).all()

            if ((int(user['id']), ) in id_docenti_corso or 'amministratore' in user['roles']):
                chiusa = False if request.form.get(
                    'chiusa') is None else request.form.get('chiusa')

        # Controlla che la domanda a cui si vuole rispondere esista
        if id_domanda_corso is not None:
            try:
                id_domande_corso = sessionStudenti.query(DomandeCorso.id).\
                    filter(DomandeCorso.id_corso == id).all()
            except Exception as e:
                return jsonify({'error': True, 'errormessage': 'Error in updating the answer: ' + str(e)}), 500

            if ((int(id_domanda_corso),) not in id_domande_corso):
                return jsonify({'error': True, 'errormessage': 'Question not found'}), 400

        # creazione del nuovo oggetto da inserire
        domanda_corso = sessionStudenti.query(DomandeCorso).filter(DomandeCorso.id == id_domanda).first()
        
        if testo is not None:
            domanda_corso.testo = testo
        if id_domanda_corso is not None:
            domanda_corso.id_domanda_corso = id_domanda_corso
        if chiusa is not None:
            domanda_corso.chiusa = True if chiusa == 'true' else False
            
        # prova di inserimento della nuova domanda
        try:
            sessionStudenti.commit()
        except Exception as e:
            sessionStudenti.rollback()
            return jsonify({'error': True, 'errormessage': 'Error updating question: ' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200


@domande.route('/corsi/<id>/domande/<id_domanda>', methods=['DELETE'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def remove_domanda(user, id, id_domanda):
    with SessionStudenti() as sessionStudenti:
        sessionStudenti.begin()

        try:
            domanda_to_remove = sessionStudenti.query(
                DomandeCorso).filter(DomandeCorso.id == id_domanda).first()
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Error while retrieving question: ' + str(e)}), 500

        # Controlliamo che lo studente che vuole eliminare la domanda sia effettivamente quello che l'ha posta
        if ('studente' in user['roles'] and domanda_to_remove.id_utente != user['id']):
            return jsonify({'error': True, 'errormessage': 'You cannot remove a question that you have not asked yourself'}), 401

        # Controlliamo che il docente sia proprietario del corso, altrimenti non permettiamo la rimozione delle domande
        if('docente' in user['roles'] and 'amministratore' not in user['roles']):
            try:
                if(sessionStudenti.query(DocenteCorso.id_docente).filter(DocenteCorso.id_corso == id).first() != user['id']):
                    return jsonify({'error': True, 'errormessage': 'You can\'t remove a question from a course that doesn\'t belong to you'}), 401
            except Exception as e:
                return jsonify({'error': True, 'errormessage': 'Error checking permissions: ' + str(e)}), 500

        try:
            sessionStudenti.delete(domanda_to_remove)
            sessionStudenti.commit()
        except Exception as e:
            sessionStudenti.rollback()
            return jsonify({'error': True, 'errormessage': 'Error deleting the question from the course: ' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200


@domande.route('/corsi/<id_corso>/domande/<id_domanda>/like', methods=['GET'])
def get_likes_domanda(id_corso, id_domanda):
    with PreLoginSession() as preLoginSession, preLoginSession.begin():

        skip = request.args.get('skip')
        limit = request.args.get('limit')
        name = request.args.get('nome')
        lastname = request.args.get('cognome')

        try:
            likes = preLoginSession.query(Utente.id).\
                join(LikeDomanda, LikeDomanda.id_utente == Utente.id).\
                filter(LikeDomanda.id_domanda_corso == id_domanda)

            if skip is not None:
                likes = likes.offset(skip)
            if limit is not None:
                likes = likes.limit(limit)
            if name is not None:
                likes = likes.filter(Utente.nome.like('%' + name + '%'))
            if lastname is not None:
                likes = likes.filter(Utente.cognome.like('%' + lastname + '%'))

            likes = likes.all()

        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Error in finding likes: ' + str(e)}), 500

        return jsonify(json.loads(json.dumps([dict(like._mapping) for like in likes]))), 200


@domande.route('/corsi/<id_corso>/domande/<id_domanda>/like', methods=['POST'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def add_like_domanda(user, id_corso, id_domanda):
    with SessionStudenti() as sessionStudenti:
        sessionStudenti.begin()
        try:
            if (sessionStudenti.query(DomandeCorso.id).filter(DomandeCorso.id == id_domanda).count() == 0):
                return jsonify({'error': True, 'errormessage': 'Domanda inesistente'}), 404
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Error in finding question: ' + str(e)}), 500

        try:
            if(sessionStudenti.query(LikeDomanda.id_utente).
                    filter(LikeDomanda.id_utente == user['id'], LikeDomanda.id_domanda_corso == id_domanda).count() != 0):

                return jsonify({'error': True, 'errormessage': 'You have already liked this question'}), 409
        except Exception as e:
            return jsonify({'error': True, 'errormessage': 'Error checking duplicate likes: ' + str(e)}), 500

        # creazione del nuovo oggetto da inserire
        new_like_domanda = LikeDomanda(
            id_utente=user['id'], id_domanda_corso=id_domanda)

        # prova di inserimento del nuovo like alla domanda
        try:
            sessionStudenti.add(new_like_domanda)
            sessionStudenti.commit()
        except Exception as e:
            sessionStudenti.rollback()
            return jsonify({'error': True, 'errormessage': 'Error in inserting the like to the question: ' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200


@domande.route('/corsi/<id_corso>/domande/<id_domanda>/like', methods=['DELETE'])
@token_required(restrict_to_roles=['amministratore', 'docente', 'studente'])
def delete_like_domanda(user, id_corso, id_domanda):
    with SessionStudenti() as sessionStudenti:
        sessionStudenti.begin()
        
        # NOTA: Lasciamo la possibilità di eliminare i like indipendentemente da chi li ha messi solo all'amministratore
        # per questioni di sicurezza; i docenti non possono eliminare i like (W LA LIBERTà DI ESPRESSIONE!)
        id_utente = user['id']
        if ('amministratore' in user['roles']):
            id_utente = request.form.get('id_utente') if (
                request.form.get('id_utente') is not None) else user['id']

        try:
            # Recupera il like posto a quella domanda dell'utente corrente
            like_to_remove = sessionStudenti.query(LikeDomanda).\
                filter(LikeDomanda.id_utente == id_utente,
                    LikeDomanda.id_domanda_corso == id_domanda).first()

            if (like_to_remove is None):
                return jsonify({'error': True, 'errormessage': 'Like not found'}), 404

            sessionStudenti.delete(like_to_remove)
            sessionStudenti.commit()
        except Exception as e:
            sessionStudenti.rollback()
            return jsonify({'error': True, 'errormessage': 'Error while deleting the question like: ' + str(e)}), 500

        return jsonify({'error': False, 'errormessage': ''}), 200
