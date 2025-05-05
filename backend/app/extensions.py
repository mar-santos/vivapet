# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask import jsonify, current_app
import logging

logger = logging.getLogger(__name__)

# Inicialização de extensões sem vincular a uma aplicação específica
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
bcrypt = Bcrypt()
cors = CORS()

# Armazenamento para tokens na blacklist
jwt_blacklist = set()

def init_extensions(app):
    """Inicializa todas as extensões com a instância da aplicação."""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources=app.config.get('CORS_RESOURCES', {r"/api/*": {"origins": "*"}}))
    
    # Log da chave JWT (apenas para desenvolvimento)
    if app.debug:
        logger.debug(f"JWT está usando a chave: {app.config.get('JWT_SECRET_KEY')[:5]}...")
    
    # Configurar callbacks do JWT
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        logger.warning(f"Token expirado: {jwt_payload.get('sub')} - JTI: {jwt_payload.get('jti')}")
        return jsonify({
            'status': 'error',
            'message': 'O token expirou',
            'error': 'token_expired'
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        logger.warning(f"Token inválido: {error}")
        return jsonify({
            'status': 'error',
            'message': 'Assinatura ou token inválido',
            'error': 'invalid_token'
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        logger.warning(f"Token ausente: {error}")
        return jsonify({
            'status': 'error',
            'message': 'Falta o token de acesso',
            'error': 'authorization_required'
        }), 401
    
    # Verificação da blacklist (apenas se implementar logout)
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        is_blocked = jti in jwt_blacklist
        if is_blocked:
            logger.info(f"Token bloqueado: {jwt_payload.get('sub')} - JTI: {jti}")
        return is_blocked
    
    # Registrar handler para tokens revogados
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        logger.info(f"Token revogado: {jwt_payload.get('sub')} - JTI: {jwt_payload.get('jti')}")
        return jsonify({
            'status': 'error',
            'message': 'O token foi revogado',
            'error': 'token_revoked'
        }), 401