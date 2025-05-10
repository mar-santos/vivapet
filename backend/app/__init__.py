# app/__init__.py
import os
from flask import Flask
from .config import config
from .api.routes import home_routes
from .api.routes import usuario_routes

# Importamos db das extensões para exportar para outros módulos
from .extensions import db, jwt

def create_app(config_name=None):
    """Cria e configura a aplicação Flask."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')
    
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    
    # Verifica se a pasta instance existe
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Inicialização de extensões
    from .extensions import init_extensions
    init_extensions(app)
    
    # Registro de blueprints
    register_blueprints(app)
    
    # Configuração de handlers
    configure_handlers(app)
    
    return app

def register_blueprints(app):
    """Registra os blueprints na aplicação."""
    with app.app_context():
        # Registramos os blueprints
        from .api.routes import (
            auth_routes,
            usuario_routes,
            pet_routes,
            servico_routes,
            agendamento_routes,
            pagamento_routes
        )
        
        app.register_blueprint(auth_routes.auth_bp, url_prefix='/api')
        app.register_blueprint(usuario_routes.usuario_bp, url_prefix='/api')
        app.register_blueprint(pet_routes.pet_bp, url_prefix='/api')
        app.register_blueprint(servico_routes.servico_bp, url_prefix='/api')
        app.register_blueprint(agendamento_routes.agendamento_bp, url_prefix='/api')
        app.register_blueprint(pagamento_routes.pagamento_bp, url_prefix='/api')
        app.register_blueprint(home_routes.home_bp, url_prefix='/api')

def configure_handlers(app):
    """Configura tratadores de erros e JWT."""
    with app.app_context():
        # Configuração de tratadores de erro
        from .utils.error_handlers import register_error_handlers
        register_error_handlers(app)
        
        # Configuração do JWT
        from .utils.jwt_utils import configure_jwt
        configure_jwt(jwt)