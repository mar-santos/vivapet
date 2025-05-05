# app/api/routes/home_routes.py
from flask import Blueprint, jsonify

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    return jsonify({
        'message': 'Bem-vindo à API VivaPet',
        'version': '1.0',
        'status': 'online',
        'documentation': '/api/docs'  # Se você tiver documentação
    })