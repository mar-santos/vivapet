# app/config.py
import os
from datetime import timedelta
from pathlib import Path

# Obter o diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / 'instance'

class Config:
    # Chave secreta para sessões Flask e CSRF
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-padrao-dev'
    
    # Configuração do SQLAlchemy
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{INSTANCE_DIR / "dbVivapet.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações para otimizar SQLite
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'connect_args': {'check_same_thread': False}
    }
    
    # Configuração JWT
    # IMPORTANTE: Usar uma chave fixa para desenvolvimento para evitar que tokens sejam invalidados em recargas
    JWT_SECRET_KEY = 'DEBUG-KEY-123'  # Temporário para diagnóstico
    
    #JWT_SECRET_KEY = 'jwt-chave-secreta-para-desenvolvimento-nao-use-em-producao'
    
    # Configuração de tokens
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Configurações de blacklist (apenas se implementar logout)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # Configurações de token - IMPORTANTE para corrigir o problema
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Limites de upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limite para uploads
    
    # Configurações CORS
    CORS_RESOURCES = {r"/api/*": {"origins": "*"}}

class DevelopmentConfig(Config):
    DEBUG = True
    # IMPORTANTE: Configuração para garantir que o reload não afete o JWT
    PROPAGATE_EXCEPTIONS = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    PROPAGATE_EXCEPTIONS = True

class ProductionConfig(Config):
    # Em produção, usar variáveis de ambiente para chaves secretas
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gerar-uma-chave-aleatoria-segura'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'gerar-uma-chave-jwt-aleatoria-segura'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{INSTANCE_DIR / "dbVivapet.db"}'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    
    # Em produção, configure origens CORS específicas
    CORS_RESOURCES = {r"/api/*": {"origins": [
        "https://seudominioprincipal.com.br", 
        "https://www.seudominioprincipal.com.br"
    ]}}

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}