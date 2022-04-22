from flask import Blueprint, jsonify
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return jsonify({ "api_version": "1.0", "endpoints": ["/users", "/login"] })

@main.route('/profile')
def profile():
    return 'Profile'
