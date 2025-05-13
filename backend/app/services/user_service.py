from typing import Dict, Any, Tuple
from flask import jsonify
from ..models.usuario import Usuario
from ..models.pet import Pet  # Certifique-se de que esta linha está presente
from ..extensions import db, bcrypt
from ..utils.api_responses import success_response, error_response
import logging

logger = logging.getLogger(__name__)

class UserService:
    """Serviço para gerenciar operações relacionadas a usuários."""
    
    def get_all_usuarios(self, current_user_id: int) -> Tuple:
        try:
            current_user = Usuario.query.get(current_user_id)
            if not current_user or not current_user.is_admin:
                usuario = Usuario.query.get(current_user_id)
                if not usuario or not usuario.ativo:
                    return error_response('Usuário não encontrado', status_code=404)
                return success_response(usuario.to_dict(), 'Perfil recuperado com sucesso')
            
            usuarios = Usuario.query.filter_by(ativo=True).all()
            usuarios_dict = [usuario.to_dict(include_pets=False) for usuario in usuarios]
            
            return success_response(usuarios_dict, 'Usuários listados com sucesso')
        
        except Exception as e:
            logger.error(f"Erro ao listar usuários: {str(e)}")
            return error_response(f'Erro ao listar usuários: {str(e)}', status_code=500)
    
    def get_usuario_by_id(self, user_id: int, current_user_id: int) -> Tuple:
        try:
            current_user = Usuario.query.get(current_user_id)
            if not current_user:
                return error_response('Usuário autenticado não encontrado', status_code=404)
            
            if not current_user.is_admin and current_user_id != user_id:
                return error_response('Acesso negado. Você só pode ver seu próprio perfil', status_code=403)
            
            usuario = Usuario.query.get(user_id)
            if not usuario or not usuario.ativo:
                return error_response('Usuário não encontrado', status_code=404)
            
            return success_response(usuario.to_dict(), 'Usuário recuperado com sucesso')
        
        except Exception as e:
            logger.error(f"Erro ao recuperar usuário: {str(e)}")
            return error_response(f'Erro ao recuperar usuário: {str(e)}', status_code=500)
    
    def create_usuario(self, data: Dict[str, Any]) -> Usuario:
        try:
            if Usuario.query.filter_by(username=data['username']).first():
                raise ValueError('Nome de usuário já está em uso')
            if Usuario.query.filter_by(email=data['email']).first():
                raise ValueError('Email já está em uso')
            if Usuario.query.filter_by(cpf=data['cpf']).first():
                raise ValueError('CPF já está em uso')

            usuario = Usuario(
                username=data['username'],
                nome_user=data['nome_user'],
                cpf=data['cpf'],
                endereco=data.get('endereco'),
                cep=data['cep'],
                telefone=data['telefone'],
                email=data['email'],
                ativo=True,
                is_admin=data.get('is_admin', False)
            )

            usuario.senha = data['senha']

            if 'foto_user' in data:
                usuario.foto_user = data['foto_user']

            if 'pets' in data:
                nomes_pets = [nome.strip() for nome in data['pets'].split(',') if nome.strip()]
                for nome in nomes_pets:
                    novo_pet = Pet(nome_pet=nome, ativo=True)
                    usuario.pets.append(novo_pet)

            db.session.add(usuario)
            db.session.commit()

            return usuario

        except ValueError as e:
            db.session.rollback()
            logger.error(f'Erro ao criar usuário: {str(e)}')
            raise ValueError(f'Erro ao criar usuário: {str(e)}')

        except Exception as e:
            db.session.rollback()
            logger.error(f'Erro ao criar usuário: {str(e)}')
            raise Exception(f'Erro ao criar usuário: {str(e)}')