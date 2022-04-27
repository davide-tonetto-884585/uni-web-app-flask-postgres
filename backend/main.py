from flask import Blueprint, jsonify
from . import db
from .auth import token_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return jsonify({ "api_version": "1.0", "endpoints": ["/studenti", "/docenti", "/login"]}), 200

