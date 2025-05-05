# app/services/pet_service.py
from typing import Dict, Any, Tuple
from flask import jsonify
from ..models.pet import Pet
from ..models.usuario import Usuario
from ..extensions import db
from ..utils.api_responses import success_response, error_response

class PetService:
    """Serviço para gerenciar operações relacionadas a pets."""
    
    def get_pet_by_id(self, pet_id: int, current_user_id: int) -> Tuple:
        """
        Retorna dados de um pet específico.
        
        Args:
            pet_id: ID do pet a ser recuperado
            current_user_id: ID do usuário autenticado
            
        Returns:
            Resposta da API com dados do pet
        """
        try:
            # Verificar se o usuário atual é administrador ou dono do pet
            current_user = Usuario.query.get(current_user_id)
            
            if not current_user:
                return error_response('Usuário autenticado não encontrado', status_code=404)
            
            pet = Pet.query.get(pet_id)
            if not pet or not pet.ativo:
                return error_response('Pet não encontrado', status_code=404)
            
            # Verificar se o usuário é administrador ou dono do pet
            if not current_user.is_admin and pet.id_usuario != current_user_id:
                return error_response('Acesso negado. Você só pode ver seus próprios pets', status_code=403)
            
            return success_response(pet.to_dict(), 'Pet recuperado com sucesso')
        
        except Exception as e:
            return error_response(f'Erro ao recuperar pet: {str(e)}', status_code=500)
    
    def create_pet(self, data: Dict[str, Any], current_user_id: int) -> Tuple:
        """
        Cria um novo pet no sistema.
        
        Args:
            data: Dados do pet a ser criado
            current_user_id: ID do usuário autenticado
            
        Returns:
            Resposta da API com resultado da operação
        """
        try:
            # Verificar se o usuário existe
            usuario = Usuario.query.get(current_user_id)
            if not usuario or not usuario.ativo:
                return error_response('Usuário não encontrado', status_code=404)
            
            # Se o ID do usuário foi fornecido nos dados e o usuário não é admin,
            # garantir que seja o próprio usuário
            if 'id_usuario' in data and data['id_usuario'] != current_user_id and not usuario.is_admin:
                return error_response('Acesso negado. Você só pode cadastrar pets para si mesmo', status_code=403)
            
            # Usar o ID do usuário autenticado se não for especificado
            if 'id_usuario' not in data:
                data['id_usuario'] = current_user_id
            
            # Criar o novo pet
            pet = Pet(
                id_usuario=data['id_usuario'],
                nome_pet=data['nome_pet'],
                raca=data.get('raca'),
                idade=data.get('idade'),
                sexo=data.get('sexo'),
                peso=data.get('peso'),
                castrado=data.get('castrado'),
                alimentacao=data.get('alimentacao'),
                saude=data.get('saude'),
                ativo=True
            )
            
            db.session.add(pet)
            db.session.commit()
            
            return success_response(pet.to_dict(), 'Pet cadastrado com sucesso', 201)
        
        except Exception as e:
            db.session.rollback()
            return error_response(f'Erro ao cadastrar pet: {str(e)}', status_code=500)
    
    def update_pet(self, pet_id: int, data: Dict[str, Any], current_user_id: int) -> Tuple:
        """
        Atualiza os dados de um pet existente.
        
        Args:
            pet_id: ID do pet a ser atualizado
            data: Novos dados do pet
            current_user_id: ID do usuário autenticado
            
        Returns:
            Resposta da API com resultado da operação
        """
        try:
            # Verificar se o usuário atual é administrador ou dono do pet
            current_user = Usuario.query.get(current_user_id)
            
            if not current_user:
                return error_response('Usuário autenticado não encontrado', status_code=404)
            
            pet = Pet.query.get(pet_id)
            if not pet or not pet.ativo:
                return error_response('Pet não encontrado', status_code=404)
            
            # Verificar se o usuário é administrador ou dono do pet
            if not current_user.is_admin and pet.id_usuario != current_user_id:
                return error_response('Acesso negado. Você só pode editar seus próprios pets', status_code=403)
            
            # Atualizar campos permitidos
            allowed_fields = ['nome_pet', 'raca', 'idade', 'sexo', 'peso', 'castrado', 'alimentacao', 'saude']
            
            # Atualizar cada campo permitido
            for field in allowed_fields:
                if field in data:
                    setattr(pet, field, data[field])
            
            db.session.commit()
            
            return success_response(pet.to_dict(), 'Pet atualizado com sucesso')
        
        except Exception as e:
            db.session.rollback()
            return error_response(f'Erro ao atualizar pet: {str(e)}', status_code=500)
    
    def delete_pet(self, pet_id: int, current_user_id: int) -> Tuple:
        """
        Marca um pet como inativo (exclusão lógica).
        
        Args:
            pet_id: ID do pet a ser excluído
            current_user_id: ID do usuário autenticado
            
        Returns:
            Resposta da API com resultado da operação
        """
        try:
            # Verificar se o usuário atual é administrador ou dono do pet
            current_user = Usuario.query.get(current_user_id)
            
            if not current_user:
                return error_response('Usuário autenticado não encontrado', status_code=404)
            
            pet = Pet.query.get(pet_id)
            if not pet or not pet.ativo:
                return error_response('Pet não encontrado', status_code=404)
            
            # Verificar se o usuário é administrador ou dono do pet
            if not current_user.is_admin and pet.id_usuario != current_user_id:
                return error_response('Acesso negado. Você só pode excluir seus próprios pets', status_code=403)
            
            pet.ativo = False
            db.session.commit()
            
            return success_response(message='Pet excluído com sucesso')
        
        except Exception as e:
            db.session.rollback()
            return error_response(f'Erro ao excluir pet: {str(e)}', status_code=500)