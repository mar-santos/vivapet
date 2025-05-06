# app/api/routes/agendamento_routes.py (parte inicial)
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt_identity

from ...extensions import db
from ...models.agendamento import Agendamento
from ...models.agendamento_servico import AgendamentoServico
from ...models.pet import Pet
from ...models.servico import Servico
from ...models.usuario import Usuario
from ...utils.api_responses import success_response, error_response
from ...utils.validators import (
    validate_required_fields, validate_datetime_format, 
    validate_service_datetime, validate_positive_number,
    validate_payment_type, validate_date_range
)

agendamento_bp = Blueprint('agendamentos', __name__)
logger = logging.getLogger(__name__)

def calcular_valor_servico(servico_id, data_inicio_str, data_fim_str):
    """
    Calcula o valor total de um serviço com base no período e tipo.
    
    Args:
        servico_id: ID do serviço
        data_inicio_str: String com data/hora início (DD/MM/YYYY HH:MM)
        data_fim_str: String com data/hora fim (DD/MM/YYYY HH:MM)
    
    Returns:
        tuple: (valor calculado, erro)
    """
    try:
        servico = Servico.query.get(servico_id)
        if not servico:
            return None, "Serviço não encontrado"
        
        if hasattr(servico, 'ativo') and not servico.ativo:
            return None, "Este serviço não está mais disponível"
        
        # Converter strings para objetos datetime
        data_inicio = datetime.strptime(data_inicio_str, '%d/%m/%Y %H:%M')
        data_fim = datetime.strptime(data_fim_str, '%d/%m/%Y %H:%M')
        
        # Validar intervalo de datas
        valido, erro = validate_date_range(data_inicio, data_fim)
        if not valido:
            return None, erro
        
        # Calcular diferença em horas e dias
        diff_seconds = (data_fim - data_inicio).total_seconds()
        horas = diff_seconds / 3600
        dias = diff_seconds / (24 * 3600)
        
        # Cálculo baseado no tipo de serviço
        nome_servico = servico.nome_servico.lower() if hasattr(servico, 'nome_servico') else ""
        
        if "cãominhada" in nome_servico or "caminhada" in nome_servico:
            # Passeio de 30 minutos
            quantidade = horas / 0.5  # Quantidade de passeios de 30min
            return servico.valor_hora * quantidade, None
            
        elif "creche" in nome_servico:
            # Serviço de creche (por dia/diária)
            if horas <= 8:
                # Até 8 horas = 1 diária
                return servico.valor_dia, None
            else:
                # Mais de 8 horas - cobrar proporcional
                return servico.valor_dia * (horas / 8), None
                
        elif "hospedagem" in nome_servico:
            # Serviço de hospedagem (por dia/diária completa)
            if dias < 1:
                # Menos de 24h = 1 diária
                return servico.valor_dia, None
            else:
                # Arredondar para cima
                import math
                return servico.valor_dia * math.ceil(dias), None
        else:
            # Para outros serviços
            if hasattr(servico, 'valor_hora') and servico.valor_hora and not (hasattr(servico, 'valor_dia') and servico.valor_dia):
                return servico.valor_hora * horas, None
            elif hasattr(servico, 'valor_dia') and servico.valor_dia and not (hasattr(servico, 'valor_hora') and servico.valor_hora):
                return servico.valor_dia * dias, None
            else:
                return None, "Configuração de preço inválida para este serviço"
                
    except ValueError as e:
        return None, f"Erro de formato de data: {str(e)}"
    except Exception as e:
        logger.error(f"Erro ao calcular valor do serviço: {str(e)}")
        return None, f"Erro ao calcular valor do serviço: {str(e)}"

@agendamento_bp.route('/agendamentos', methods=['GET'])
@jwt_required()
def listar_agendamentos():
    """Lista todos os agendamentos do usuário ou todos se for admin."""
    try:
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return error_response("Usuário não encontrado", 404)
        
        # Parâmetros de consulta
        status = request.args.get('status')
        pet_id = request.args.get('pet_id')
        
        # Construir consulta base
        query = Agendamento.query
        
        # Filtrar por status, se fornecido e o campo existir
        if status and hasattr(Agendamento, 'status'):
            query = query.filter_by(status=status)
        
        # Filtrar por pet, se fornecido
        if pet_id:
            query = query.filter_by(id_pet=pet_id)
        
        # Filtrar por ativo, se o campo existir
        if hasattr(Agendamento, 'ativo'):
            query = query.filter_by(ativo=True)
        
        # Admin vê todos, usuário normal vê apenas os seus
        if not usuario.is_admin:
            query = query.filter_by(id_usuario=current_user_id)
        
        # Ordenar por data de criação, se o campo existir
        if hasattr(Agendamento, 'data_criacao'):
            query = query.order_by(Agendamento.data_criacao.desc())
        
        agendamentos = query.all()
        
        return success_response(
            data=[agendamento.to_dict() for agendamento in agendamentos],
            message=f"Encontrado(s) {len(agendamentos)} agendamento(s)"
        )
    except Exception as e:
        logger.error(f"Erro ao listar agendamentos: {str(e)}")
        return error_response(f"Erro ao listar agendamentos: {str(e)}", 500)

@agendamento_bp.route('/agendamentos/<int:id>', methods=['GET'])
@jwt_required()
def obter_agendamento(id):
    """Obtém um agendamento específico pelo ID."""
    try:
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return error_response("Usuário não encontrado", 404)
        
        agendamento = Agendamento.query.get(id)
        
        if not agendamento:
            return error_response("Agendamento não encontrado", 404)
        
        # Verificar se agendamento está ativo, se o campo existir
        if hasattr(agendamento, 'ativo') and not agendamento.ativo:
            return error_response("Agendamento não encontrado", 404)
        
        # Verificar permissão - apenas admin ou dono do agendamento pode ver
        if not usuario.is_admin and agendamento.id_usuario != current_user_id:
            return error_response("Acesso negado a este agendamento", 403)
        
        return success_response(
            data=agendamento.to_dict(),
            message="Agendamento encontrado com sucesso"
        )
    except Exception as e:
        logger.error(f"Erro ao obter agendamento: {str(e)}")
        return error_response(f"Erro ao obter agendamento: {str(e)}", 500)

@agendamento_bp.route('/agendar_servico', methods=['POST'])
@jwt_required()
def agendar_servico():
    """Agenda um serviço para um pet."""
    try:
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return error_response("Usuário não encontrado", 404)
        
        data = request.get_json()
        
        # Converte campos se necessário
        if 'data_entrada' in data and 'data_saida' in data:
            data['data_inicio'] = data.pop('data_entrada')
            data['data_fim'] = data.pop('data_saida')
        
        # Validação
        required_fields = ['id_pet', 'id_servico', 'data_inicio', 'data_fim']
        missing_fields = validate_required_fields(data, required_fields)
        if missing_fields:
            return error_response(f"Campos obrigatórios faltando: {', '.join(missing_fields)}", 400)
        
        # Verificar pet
        pet = Pet.query.get(data['id_pet'])
        if not pet:
            return error_response("Pet não encontrado", 404)
        
        if not usuario.is_admin and pet.id_usuario != current_user_id:
            return error_response("Este pet não pertence ao usuário atual", 403)
        
        # Verificar serviço
        servico = Servico.query.get(data['id_servico'])
        if not servico:
            return error_response("Serviço não encontrado", 404)
        
        # Validar formatos de data/hora
        format_inicio = validate_datetime_format(data['data_inicio'])
        if not format_inicio:
            return error_response("Formato de data de início inválido. Use DD/MM/YYYY HH:MM", 400)
            
        format_fim = validate_datetime_format(data['data_fim'])
        if not format_fim:
            return error_response("Formato de data de fim inválido. Use DD/MM/YYYY HH:MM", 400)
        
        # Calcular valor
        valor, erro = calcular_valor_servico(data['id_servico'], data['data_inicio'], data['data_fim'])
        if erro:
            return error_response(erro, 400)
        
        # Criar objeto agendamento
        data_inicio = datetime.strptime(data['data_inicio'], '%d/%m/%Y %H:%M')
        data_fim = datetime.strptime(data['data_fim'], '%d/%m/%Y %H:%M')
        
        # Criar novo agendamento - incluindo id_servico
        agendamento = Agendamento(
            id_usuario=current_user_id,
            id_pet=data['id_pet'],
            id_servico=data['id_servico'],  # Adicionando id_servico aqui
            data_inicio=data_inicio,
            data_fim=data_fim,
            observacoes=data.get('observacoes', ''),
            status='agendado',
            valor_total=valor
        )
        
        db.session.add(agendamento)
        db.session.flush()  # Para obter o ID gerado
        
        # Criar item de serviço
        item_servico = AgendamentoServico(
            id_agendamento=agendamento.id_agendamento,
            id_servico=data['id_servico'],
            quantidade=1,
            valor_unitario=valor,
            observacoes=data.get('observacoes', '')
        )
        
        db.session.add(item_servico)
        db.session.commit()
        
        return success_response(
            data=agendamento.to_dict(),
            message="Agendamento criado com sucesso"
        )
        
    except ValueError as e:
        db.session.rollback()
        logger.error(f"Erro de validação: {str(e)}")
        return error_response(f"Erro de validação: {str(e)}", 400)
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erro de banco de dados: {str(e)}")
        return error_response("Erro ao salvar no banco de dados", 500)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao agendar serviço: {str(e)}")
        return error_response("Erro ao processar a solicitação", 500)
    
@agendamento_bp.route('/agendamentos/<int:id>', methods=['PUT'])
@jwt_required()
def atualizar_agendamento(id):
    """Atualiza um agendamento específico pelo ID."""
    try:
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return error_response("Usuário não encontrado", 404)
        
        agendamento = Agendamento.query.get(id)
        
        if not agendamento:
            return error_response("Agendamento não encontrado", 404)
        
        # Verificar se agendamento está ativo, se o campo existir
        if hasattr(agendamento, 'ativo') and not agendamento.ativo:
            return error_response("Agendamento não encontrado ou inativo", 404)
        
        # Verificar permissão - apenas admin ou dono do agendamento pode editar
        if not usuario.is_admin and agendamento.id_usuario != current_user_id:
            return error_response("Acesso negado a este agendamento", 403)
        
        data = request.get_json()
        
        # Converte campos se necessário
        if 'data_entrada' in data and 'data_saida' in data:
            data['data_inicio'] = data.pop('data_entrada')
            data['data_fim'] = data.pop('data_saida')
        
        # Validar formatos de data/hora se estiverem presentes nos dados
        if 'data_inicio' in data:
            format_inicio = validate_datetime_format(data['data_inicio'])
            if not format_inicio:
                return error_response("Formato de data de início inválido. Use DD/MM/YYYY HH:MM", 400)
        
        if 'data_fim' in data:
            format_fim = validate_datetime_format(data['data_fim'])
            if not format_fim:
                return error_response("Formato de data de fim inválido. Use DD/MM/YYYY HH:MM", 400)
        
        # Se ambas as datas foram fornecidas, recalcular o valor
        if 'data_inicio' in data and 'data_fim' in data:
            id_servico = data.get('id_servico', agendamento.id_servico)
            valor, erro = calcular_valor_servico(id_servico, data['data_inicio'], data['data_fim'])
            if erro:
                return error_response(erro, 400)
            data['valor_total'] = valor
        
        # Verificar pet, se id_pet for fornecido
        if 'id_pet' in data:
            pet = Pet.query.get(data['id_pet'])
            if not pet:
                return error_response("Pet não encontrado", 404)
            
            if not usuario.is_admin and pet.id_usuario != current_user_id:
                return error_response("Este pet não pertence ao usuário atual", 403)
        
        # Verificar serviço, se id_servico for fornecido
        if 'id_servico' in data:
            servico = Servico.query.get(data['id_servico'])
            if not servico:
                return error_response("Serviço não encontrado", 404)
            
            # Se mudar o serviço mas não as datas, recalcular o valor
            if 'data_inicio' not in data and 'data_fim' not in data:
                data_inicio_str = agendamento.data_inicio.strftime('%d/%m/%Y %H:%M')
                data_fim_str = agendamento.data_fim.strftime('%d/%m/%Y %H:%M')
                valor, erro = calcular_valor_servico(data['id_servico'], data_inicio_str, data_fim_str)
                if erro:
                    return error_response(erro, 400)
                data['valor_total'] = valor
        
        # Atualizar campos do agendamento
        campos_atualizaveis = [
            'id_pet', 'id_servico', 'data_inicio', 'data_fim', 
            'observacoes', 'status', 'valor_total'
        ]
        
        for campo in campos_atualizaveis:
            if campo in data:
                # Converter datas de string para datetime
                if campo in ['data_inicio', 'data_fim']:
                    valor = datetime.strptime(data[campo], '%d/%m/%Y %H:%M')
                else:
                    valor = data[campo]
                setattr(agendamento, campo, valor)
        
        # Se houver mudança no serviço, atualizamos o AgendamentoServico também
        if 'id_servico' in data:
            # Buscar o item de serviço atual
            item_servico = AgendamentoServico.query.filter_by(
                id_agendamento=agendamento.id_agendamento
            ).first()
            
            if item_servico:
                item_servico.id_servico = data['id_servico']
                # Atualizar valor unitário se foi recalculado
                if 'valor_total' in data:
                    item_servico.valor_unitario = data['valor_total']
                # Atualizar observações se fornecidas
                if 'observacoes' in data:
                    item_servico.observacoes = data['observacoes']
        
        db.session.commit()
        
        return success_response(
            data=agendamento.to_dict(),
            message="Agendamento atualizado com sucesso"
        )
        
    except ValueError as e:
        db.session.rollback()
        logger.error(f"Erro de validação: {str(e)}")
        return error_response(f"Erro de validação: {str(e)}", 400)
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erro de banco de dados: {str(e)}")
        return error_response("Erro ao atualizar no banco de dados", 500)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar agendamento: {str(e)}")
        return error_response("Erro ao processar a solicitação", 500)
    
@agendamento_bp.route('/agendamentos/<int:id>', methods=['DELETE'])
@jwt_required()
def deletar_agendamento(id):
    """Remove logicamente um agendamento específico pelo ID e seus serviços relacionados."""
    try:
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get(current_user_id)
        
        if not usuario:
            return error_response("Usuário não encontrado", 404)
        
        agendamento = Agendamento.query.get(id)
        
        if not agendamento:
            return error_response("Agendamento não encontrado", 404)
        
        # Verificar se agendamento já está inativo, se o campo existir
        if hasattr(agendamento, 'ativo') and not agendamento.ativo:
            return error_response("Agendamento já foi removido", 400)
        
        # Verificar permissão - apenas admin ou dono do agendamento pode remover
        if not usuario.is_admin and agendamento.id_usuario != current_user_id:
            return error_response("Acesso negado a este agendamento", 403)
        
        # Verificar se o agendamento pode ser removido com base no status
        if hasattr(agendamento, 'status'):
            # Não permitir remover agendamentos já concluídos/pagos/em andamento
            status_nao_removiveis = ['concluido', 'pago', 'em_andamento']
            if agendamento.status.lower() in status_nao_removiveis:
                return error_response(f"Não é possível remover um agendamento com status '{agendamento.status}'", 400)
        
        # Exclusão lógica (preferível) se o campo existir
        if hasattr(agendamento, 'ativo'):
            # Desativar o agendamento
            agendamento.ativo = False
            
            # Opcionalmente, atualizar o status também
            if hasattr(agendamento, 'status'):
                agendamento.status = 'cancelado'
            
            # Desativar também todos os serviços associados ao agendamento
            itens_servico = AgendamentoServico.query.filter_by(id_agendamento=agendamento.id_agendamento).all()
            for item in itens_servico:
                if hasattr(item, 'ativo'):
                    item.ativo = False
                
            db.session.commit()
            return success_response(
                data=None,
                message="Agendamento e serviços associados removidos com sucesso"
            )
        else:
            # Exclusão física se não houver campo 'ativo'
            # Primeiro remover os serviços associados
            AgendamentoServico.query.filter_by(id_agendamento=agendamento.id_agendamento).delete()
            
            # Depois remover o agendamento
            db.session.delete(agendamento)
            db.session.commit()
            
            return success_response(
                data=None,
                message="Agendamento excluído com sucesso"
            )
        
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Erro de banco de dados: {str(e)}")
        return error_response("Erro ao remover agendamento do banco de dados", 500)
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao deletar agendamento: {str(e)}")
        return error_response("Erro ao processar a solicitação", 500)