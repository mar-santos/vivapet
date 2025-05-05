# app/services/auth_service.py
from typing import Dict, Any
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
from ..models.usuario import Usuario
from ..extensions import db, jwt
from ..utils.jwt_utils import token_blocklist

class AuthService:
    """Serviço para gerenciar autenticação de usuários."""
    
    def authenticate(self, username: str, senha: str) -> Dict[str, Any]:
        """
        Autentica um usuário e gera tokens JWT.
        
        Args:
            username: Nome de usuário para autenticação
            senha: Senha para autenticação
            
        Returns:
            Dicionário contendo status de sucesso, mensagem e dados do login.
        """
        # Buscar usuário pelo username
        usuario = Usuario.query.filter_by(username=username).first()
        
        # Verificar se o usuário existe e está ativo
        if not usuario:
            return {
                'success': False,
                'message': 'Usuário não encontrado'
            }
        
        if not usuario.ativo:
            return {
                'success': False,
                'message': 'Esta conta está desativada'
            }
        
        # Verificar senha
        if not usuario.verificar_senha(senha):
            return {
                'success': False,
                'message': 'Senha incorreta'
            }
        
        # Gerar tokens
        access_token = create_access_token(identity=str(usuario.id_usuario))  # Converte para string
        refresh_token = create_refresh_token(identity=str(usuario.id_usuario))  # Converte para string
        
        return {
            'success': True,
            'message': 'Login realizado com sucesso',
            'data': {
                'user': usuario.to_dict(include_pets=False),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }
    
    def blacklist_token(self, jti: str) -> None:
        """
        Adiciona um token à lista negra (para logout).
        
        Args:
            jti: Identificador único do token JWT
        """
        token_blocklist.add(jti)