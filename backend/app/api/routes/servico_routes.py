# app/api/routes/servico_routes.py
from flask import Blueprint, request, jsonify
from ...extensions import db
from ...models.servico import Servico
from ...utils.api_responses import success_response, error_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...models.usuario import Usuario

servico_bp = Blueprint('servicos', __name__)

@servico_bp.route('/servicos', methods=['GET'])
@jwt_required()
def get_servicos():
    """Lista todos os serviços disponíveis."""
    try:
        current_user_id = get_jwt_identity()
        
        # Verificar se o usuário é administrador
        usuario = Usuario.query.get(current_user_id)
        if not usuario or not usuario.is_admin:
            return error_response('Acesso negado. Apenas administradores podem visualizar serviços', status_code=403)
        
        servicos = Servico.query.filter_by(ativo=True).all()
        servicos_dict = [servico.to_dict() for servico in servicos]
        
        return success_response(servicos_dict, 'Serviços listados com sucesso')
    
    except Exception as e:
        return error_response(f'Erro ao listar serviços: {str(e)}', status_code=500)

@servico_bp.route('/servicos/<int:id>', methods=['GET'])
@jwt_required()
def get_servico(id):
    """Retorna os detalhes de um serviço específico."""
    try:
        current_user_id = get_jwt_identity()
        
        # Verificar se o usuário é administrador
        usuario = Usuario.query.get(current_user_id)
        if not usuario or not usuario.is_admin:
            return error_response('Acesso negado. Apenas administradores podem visualizar serviços', status_code=403)
        
        servico = Servico.query.get(id)
        if not servico or not servico.ativo:
            return error_response('Serviço não encontrado', status_code=404)
        
        return success_response(servico.to_dict(), 'Serviço recuperado com sucesso')
    
    except Exception as e:
        return error_response(f'Erro ao recuperar serviço: {str(e)}', status_code=500)

@servico_bp.route('/servicos', methods=['POST'])
@jwt_required()
def create_servico():
    """Cria um novo serviço."""
    try:
        current_user_id = get_jwt_identity()
        
        # Verificar se o usuário é administrador
        usuario = Usuario.query.get(current_user_id)
        if not usuario or not usuario.is_admin:
            return error_response('Acesso negado. Apenas administradores podem criar serviços', status_code=403)
        
        data = request.get_json()
        
        # Validação dos dados de entrada
        if not data or not data.get('nome_servico'):
            return error_response('Nome do serviço é obrigatório', status_code=400)
        
        servico = Servico(
            nome_servico=data['nome_servico'],
            descricao=data.get('descricao'),
            valor_hora=data.get('valor_hora'),
            valor_dia=data.get('valor_dia'),
            ativo=True
        )
        
        db.session.add(servico)
        db.session.commit()
        
        return success_response(servico.to_dict(), 'Serviço criado com sucesso', status_code=201)
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Erro ao criar serviço: {str(e)}', status_code=500)
    

@servico_bp.route('/servicos/<int:id>', methods=['PUT'])
@jwt_required()
def update_servico(id):
    """Atualiza os dados de um serviço existente."""
    try:
        current_user_id = get_jwt_identity()
        
        # Verificar se o usuário é administrador
        usuario = Usuario.query.get(current_user_id)
        if not usuario or not usuario.is_admin:
            return error_response('Acesso negado. Apenas administradores podem editar serviços', status_code=403)
        
        servico = Servico.query.get(id)
        if not servico:
            return error_response('Serviço não encontrado', status_code=404)
        
        data = request.get_json()
        
        # Validação dos dados de entrada
        if not data:
            return error_response('Dados para atualização não fornecidos', status_code=400)
        
        # Atualiza os campos do serviço se eles estiverem presentes no payload
        if 'nome_servico' in data:
            servico.nome_servico = data['nome_servico']
        if 'descricao' in data:
            servico.descricao = data['descricao']
        if 'valor_hora' in data:
            servico.valor_hora = data['valor_hora']
        if 'valor_dia' in data:
            servico.valor_dia = data['valor_dia']
        if 'ativo' in data:
            servico.ativo = data['ativo']
            
        db.session.commit()
        
        return success_response(servico.to_dict(), 'Serviço atualizado com sucesso')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Erro ao atualizar serviço: {str(e)}', status_code=500) 


@servico_bp.route('/servicos/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_servico(id):
    """Marca um serviço como inativo."""
    try:
        current_user_id = get_jwt_identity()
        
        # Verificar se o usuário é administrador
        usuario = Usuario.query.get(current_user_id)
        if not usuario or not usuario.is_admin:
            return error_response('Acesso negado. Apenas administradores podem excluir serviços', status_code=403)
        
        servico = Servico.query.get(id)
        if not servico:
            return error_response('Serviço não encontrado', status_code=404)
        
        servico.ativo = False
        db.session.commit()
        
        return success_response(message='Serviço desativado com sucesso')
    
    except Exception as e:
        db.session.rollback()
        return error_response(f'Erro ao desativar serviço: {str(e)}', status_code=500)