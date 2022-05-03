from flask import Blueprint, jsonify, current_app

from . import RootSession, PreLoginSession
from .auth import token_required
from .models import Amministratore, Studente

main = Blueprint('main', __name__)

@main.route('/')
def index():
    print(PreLoginSession().query(Amministratore).all())
    return jsonify({ "api_version": "1.0", "endpoints": ["/studenti", "/docenti", "/login"]}), 200

