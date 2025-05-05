from typing import Dict, Any, Tuple
from flask import jsonify
from ..models.usuario import Usuario
from ..extensions import db, bcrypt
from ..utils.api_responses import success_response, error_response

class UserService:
    """Serviço para gerenciar operações relacionadas a usuários."""
    
    def get_all_usuarios(self, current_user_id: int) -> Tuple:
        """
        Retorna todos os usuários ativos do sistema.
        
        Args:
            current_user_id: ID do usuário autenticado
            
        Returns:
            Resposta da API com lista de usuários
        """
        try:
            # Verificar se o usuário atual é administrador
            current_user = Usuario.query.get(current_user_id)
            
            if not current_user or not current_user.is_admin:
                # Usuários normais só podem ver seu próprio perfil
                usuario = Usuario.query.get(current_user_id)
                if not usuario or not usuario.ativo:
                    return error_response('Usuário não encontrado', status_code=404)
                return success_response(usuario.to_dict(), 'Perfil recuperado com sucesso')
            
            # Administradores podem ver todos os usuários
            usuarios = Usuario.query.filter_by(ativo=True).all()
            usuarios_dict = [usuario.to_dict(include_pets=False) for usuario in usuarios]
            
            return success_response(usuarios_dict, 'Usuários listados com sucesso')
        
        except Exception as e:
            return error_response(f'Erro ao listar usuários: {str(e)}', status_code=500)
    
    def get_usuario_by_id(self, user_id: int, current_user_id: int) -> Tuple:
        """
        Retorna dados de um usuário específico.
        
        Args:
            user_id: ID do usuário a ser recuperado
            current_user_id: ID do usuário autenticado
            
        Returns:
            Resposta da API com dados do usuário
        """
        try:
            # Verificar se o usuário atual é administrador ou o próprio usuário
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
            return error_response(f'Erro ao recuperar usuário: {str(e)}', status_code=500)
    
    def create_usuario(self, data: Dict[str, Any]) -> Tuple:
        """
        Cria um novo usuário no sistema, incluindo seus pets se fornecidos.
        
        Args:
            data: Dados do usuário a ser criado, incluindo pets
            
        Returns:
            Resposta da API com resultado da operação
        """
        try:
            # Verificar se username, email ou CPF já existem
            if Usuario.query.filter_by(username=data['username']).first():
                return error_response('Nome de usuário já está em uso', status_code=400)
            
            if Usuario.query.filter_by(email=data['email']).first():
                return error_response('Email já está em uso', status_code=400)
            
            if Usuario.query.filter_by(cpf=data['cpf']).first():
                return error_response('CPF já está em uso', status_code=400)
            
            # Criar o novo usuário
            usuario = Usuario(
                username=data['username'],
                nome_user=data['nome_user'],
                cpf=data['cpf'],
                endereco=data.get('endereco'),
                cep=data['cep'],
                telefone=data.get('telefone'),
                email=data['email'],
                ativo=True,
                is_admin=data.get('is_admin', False)
            )
            
            # Definir a senha
            usuario.senha = data['senha']
            
            # Processar pets, se fornecidos
            if 'pets' in data and isinstance(data['pets'], list):
                from ..models.pet import Pet
                
                for pet_data in data['pets']:
                    # Validar dados mínimos do pet
                    if 'nome_pet' not in pet_data:
                        return error_response('Nome do pet é obrigatório', status_code=400)
                    
                    novo_pet = Pet(
                        nome_pet=pet_data['nome_pet'],
                        raca=pet_data.get('raca'),
                        idade=pet_data.get('idade'),
                        sexo=pet_data.get('sexo'),
                        peso=pet_data.get('peso'),
                        castrado=pet_data.get('castrado', False),
                        alimentacao=pet_data.get('alimentacao'),
                        saude=pet_data.get('saude'),
                        ativo=True
                    )
                    
                    # Adicionar o pet ao usuário
                    usuario.pets.append(novo_pet)
            
            db.session.add(usuario)
            db.session.commit()
            
            # Incluir pets na resposta
            return success_response(usuario.to_dict(include_pets=True), 'Usuário criado com sucesso', 201)
        
        except Exception as e:
            db.session.rollback()
            return error_response(f'Erro ao criar usuário: {str(e)}', status_code=500)
    
    def update_usuario(self, user_id: int, data: Dict[str, Any], current_user_id: int) -> Tuple:
        """
        Atualiza os dados de um usuário existente.
        
        Args:
            user_id: ID do usuário a ser atualizado
            data: Novos dados do usuário
            current_user_id: ID do usuário autenticado
            
        Returns:
            Resposta da API com resultado da operação
        """
        try:
            # Verificar se o usuário atual é administrador ou o próprio usuário
            current_user = Usuario.query.get(current_user_id)
            
            if not current_user:
                return error_response('Usuário autenticado não encontrado', status_code=404)
            
            if not current_user.is_admin and current_user_id != user_id:
                return error_response('Acesso negado. Você só pode editar seu próprio perfil', status_code=403)
            
            usuario = Usuario.query.get(user_id)
            if not usuario or not usuario.ativo:
                return error_response('Usuário não encontrado', status_code=404)
            
            # Atualizar campos permitidos
            allowed_fields = ['nome_user', 'endereco', 'cep', 'telefone', 'email', 'ativo']
            
            # Administradores podem atualizar campos adicionais
            if current_user.is_admin:
                allowed_fields.extend(['is_admin'])
            
            # Atualizar cada campo permitido
            for field in allowed_fields:
                if field in data:
                    setattr(usuario, field, data[field])
            
            # Atualizar senha, se fornecida
            if 'senha' in data and data['senha']:
                usuario.senha = data['senha']
            
            db.session.commit()
            
            return success_response(usuario.to_dict(), 'Usuário atualizado com sucesso')
        
        except Exception as e:
            db.session.rollback()
            return error_response(f'Erro ao atualizar usuário: {str(e)}', status_code=500)
    
    def delete_usuario(self, user_id: int, current_user_id: int) -> Tuple:
        """
        Marca um usuário como inativo (exclusão lógica).
        
        Args:
            user_id: ID do usuário a ser excluído
            current_user_id: ID do usuário autenticado
            
        Returns:
            Resposta da API com resultado da operação
        """
        try:
            # Verificar se o usuário atual é administrador ou o próprio usuário
            current_user = Usuario.query.get(current_user_id)
            
            if not current_user:
                return error_response('Usuário autenticado não encontrado', status_code=404)
            
            if not current_user.is_admin and current_user_id != user_id:
                return error_response('Acesso negado. Você só pode excluir seu próprio perfil', status_code=403)
            
            usuario = Usuario.query.get(user_id)
            if not usuario or not usuario.ativo:
                return error_response('Usuário não encontrado', status_code=404)
            
            usuario.ativo = False
            db.session.commit()
            
            return success_response(message='Usuário excluído com sucesso')
        
        except Exception as e:
            db.session.rollback()
            return error_response(f'Erro ao excluir usuário: {str(e)}', status_code=500)