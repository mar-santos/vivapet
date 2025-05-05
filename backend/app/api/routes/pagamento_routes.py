#app/api/routes/pagamento_routes.py
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt_identity

from ...extensions import db
from ...models.pagamento import Pagamento
from ...models.agendamento import Agendamento
from ...models.usuario import Usuario
from ...utils.api_responses import success_response, error_response
from ...utils.validators import (
    validate_required_fields, validate_positive_number,
    validate_payment_type, validate_datetime_format
)

pagamento_bp = Blueprint('pagamentos', __name__)
logger = logging.getLogger(__name__)

@pagamento_bp.route('/pagamentos', methods=['GET'])
@jwt_required()
def listar_pagamentos():
    """Lista pagamentos com filtros opcionais."""
    try:
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return error_response("Usuário não encontrado", 404)
        
        # Parâmetros de filtro
        status = request.args.get('status')
        agendamento_id = request.args.get('agendamento_id')
        
        # Construir consulta base
        query = Pagamento.query
        
        # Filtrar por status
        if status:
            if status not in ['pendente', 'processando', 'concluido', 'cancelado']:
                return error_response(f"Status inválido: {status}", 400)
            query = query.filter_by(status=status)
        
        # Filtrar por agendamento
        if agendamento_id:
            try:
                agendamento_id = int(agendamento_id)
                query = query.filter_by(id_agendamento=agendamento_id)
            except ValueError:
                return error_response("ID de agendamento inválido", 400)
        
        # Usuário normal só vê seus próprios pagamentos
        if not usuario.is_admin:
            query = query.join(Agendamento).filter(Agendamento.id_usuario == current_user_id)
        
        # Ordenar por data de criação (mais recentes primeiro)
        query = query.order_by(Pagamento.data_criacao.desc())
        
        pagamentos = query.all()
        
        return success_response(
            data=[pagamento.to_dict() for pagamento in pagamentos],
            message=f"Encontrado(s) {len(pagamentos)} pagamento(s)"
        )
    except Exception as e:
        logger.error(f"Erro ao listar pagamentos: {str(e)}")
        return error_response(f"Erro ao listar pagamentos: {str(e)}", 500)

@pagamento_bp.route('/pagamentos/<int:id>', methods=['GET'])
@jwt_required()
def obter_pagamento(id):
    """Obtém detalhes de um pagamento específico."""
    try:
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return error_response("Usuário não encontrado", 404)
        
        pagamento = Pagamento.query.get(id)
        
        if not pagamento:
            return error_response("Pagamento não encontrado", 404)
        
        # Verificar permissão - apenas admin ou dono do agendamento
        if not usuario.is_admin:
            agendamento = Agendamento.query.get(pagamento.id_agendamento)
            if not agendamento or agendamento.id_usuario != current_user_id:
                return error_response("Acesso negado a este pagamento", 403)
        
        return success_response(
            data=pagamento.to_dict(),
            message="Pagamento encontrado com sucesso"
        )
    except Exception as e:
        logger.error(f"Erro ao obter pagamento: {str(e)}")
        return error_response(f"Erro ao obter pagamento: {str(e)}", 500)

@pagamento_bp.route('/realizar_pagamento', methods=['POST'])
@jwt_required()
def realizar_pagamento():
    """Registra um novo pagamento para um agendamento."""
    try:
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return error_response("Usuário não encontrado", 404)
        
        data = request.get_json()
        
        # Validar campos obrigatórios
        required_fields = ['id_agendamento', 'valor', 'tipo_pagamento']
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            return error_response(f"Campos obrigatórios faltando: {', '.join(missing_fields)}", 400)
        
        # Validar valor positivo
        if not validate_positive_number(data['valor']):
            return error_response("O valor do pagamento deve ser positivo", 400)
        
        # Validar tipo de pagamento
        tipos_pagamento = ['pix', 'cartao', 'boleto', 'dinheiro']
        if not validate_payment_type(data['tipo_pagamento'], tipos_pagamento):
            return error_response(f"Tipo de pagamento inválido. Use um dos: {', '.join(tipos_pagamento)}", 400)
        
        # Verificar se o agendamento existe
        agendamento = Agendamento.query.get(data['id_agendamento'])
        if not agendamento:
            return error_response("Agendamento não encontrado", 404)
        
        if not agendamento.ativo:
            return error_response("Este agendamento está inativo", 400)
        
        if agendamento.status == 'cancelado':
            return error_response("Não é possível realizar pagamento para um agendamento cancelado", 400)
        
        # Verificar permissão - apenas admin ou dono do agendamento
        if not usuario.is_admin and agendamento.id_usuario != current_user_id:
            return error_response("Acesso negado a este agendamento", 403)
        
        # Determinar status do pagamento
        status_pagamento = data.get('status', 'pendente')
        if status_pagamento not in ['pendente', 'processando', 'concluido']:
            return error_response("Status de pagamento inválido", 400)
        
        # Criar o novo pagamento
        pagamento = Pagamento(
            id_agendamento=data['id_agendamento'],
            valor=data['valor'],
            tipo_pagamento=data['tipo_pagamento'],
            status=status_pagamento,
            data_pagamento=datetime.now() if status_pagamento == 'concluido' else None
        )
        
        db.session.add(pagamento)
        
        # Se o pagamento for concluído, atualizar o status do agendamento
        if status_pagamento == 'concluido':
            agendamento.status = 'confirmado'
        
        db.session.commit()
        
        return success_response(
            data=pagamento.to_dict(),
            message="Pagamento registrado com sucesso"
        )
    except ValueError as e:
        db.session.rollback()
        return error_response(f"Erro de validação: {str(e)}", 400)
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erro de banco de dados: {str(e)}")
        return error_response("Erro ao salvar no banco de dados", 500)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao realizar pagamento: {str(e)}")
        return error_response(f"Erro ao realizar pagamento: {str(e)}", 500)

@pagamento_bp.route('/pagamentos/<int:id>', methods=['PUT'])
@jwt_required()
def atualizar_pagamento(id):
    """Atualiza um pagamento existente."""
    try:
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return error_response("Usuário não encontrado", 404)
        
        # Apenas administradores podem alterar pagamentos
        if not usuario.is_admin:
            return error_response("Apenas administradores podem alterar pagamentos", 403)
        
        pagamento = Pagamento.query.get(id)
        if not pagamento:
            return error_response("Pagamento não encontrado", 404)
        
        data = request.get_json()
        
        # Validar e atualizar status
        if 'status' in data:
            status_validos = ['pendente', 'processando', 'concluido', 'cancelado']
            if data['status'] not in status_validos:
                return error_response(f"Status inválido. Use um dos: {', '.join(status_validos)}", 400)
            
            # Se mudar para concluído, atualizar data de pagamento
            if data['status'] == 'concluido' and pagamento.status != 'concluido':
                pagamento.data_pagamento = datetime.now()
                
                # Atualizar status do agendamento
                agendamento = Agendamento.query.get(pagamento.id_agendamento)
                if agendamento and agendamento.status in ['agendado', 'pendente']:
                    agendamento.status = 'confirmado'
            
            pagamento.status = data['status']
        
        # Validar e atualizar valor
        if 'valor' in data:
            if not validate_positive_number(data['valor']):
                return error_response("O valor do pagamento deve ser positivo", 400)
            pagamento.valor = data['valor']
        
        # Validar e atualizar tipo de pagamento
        if 'tipo_pagamento' in data:
            tipos_pagamento = ['pix', 'cartao', 'boleto', 'dinheiro']
            if not validate_payment_type(data['tipo_pagamento'], tipos_pagamento):
                return error_response(f"Tipo de pagamento inválido. Use um dos: {', '.join(tipos_pagamento)}", 400)
            pagamento.tipo_pagamento = data['tipo_pagamento']
        
        db.session.commit()
        
        return success_response(
            data=pagamento.to_dict(),
            message="Pagamento atualizado com sucesso"
        )
    except ValueError as e:
        db.session.rollback()
        return error_response(f"Erro de validação: {str(e)}", 400)