from flask import Blueprint, jsonify, current_app, request
import configparser

from .auth import token_required

global_settings = Blueprint('global_settings', __name__)


@global_settings.route('/impostazioni', methods=['GET'])
@token_required(restrict_to_roles=['amministratore'])
def get_current_settings(user):
    config = configparser.ConfigParser()
    config.read('global_settings.ini')
    settings = {}
    for key in config['SETTINGS']:
        settings[key] = config['SETTINGS'][key]

    return jsonify({'error': False, 'errormessage': '', 'settings': settings}), 200


@global_settings.route('/impostazioni', methods=['PUT'])
@token_required(restrict_to_roles=['amministratore'])
def update_settings(user):
    config = configparser.ConfigParser()
    config.read('global_settings.ini')
    
    if request.form.get('percentuale_presenze_minima') is not None:
        config['SETTINGS']['percentuale_presenze_minima'] = request.form.get(
            'percentuale_presenze_minima')

    if request.form.get('limite_iscrizioni_attive_studente') is not None:
        config['SETTINGS']['limite_iscrizioni_attive_studente'] = request.form.get('limite_iscrizioni_attive_studente')
        
    if request.form.get('limite_corsi_docente') is not None:
        config['SETTINGS']['limite_corsi_docente'] = request.form.get('limite_corsi_docente')
        
    with open('global_settings.ini', 'w') as configfile:
       config.write(configfile)

    return jsonify({'error': False, 'errormessage': ''}), 200
