# app/api/routes/pet_routes.py
from flask import Blueprint, request, jsonify
from ...extensions import db
from ...models.pet import Pet
from ...services.pet_service import PetService
from ...utils.api_responses import success_response, error_response
from ...utils.validators import validate_pet
from flask_jwt_extended import jwt_required, get_jwt_identity

pet_bp = Blueprint('pets', __name__)
pet_service = PetService()

@pet_bp.route('/pets', methods=['GET'])
@jwt_required()
def get_pets():
    """Lista todos os pets cadastrados no sistema."""
    try:
        current_user_id = get_jwt_identity()
        
        from ...models.usuario import Usuario
        
        usuario = Usuario.query.get(current_user_id)
        
        # Se for um admin, pode ver todos os pets
        if usuario and usuario.is_admin:
            pets = Pet.query.filter(Pet.ativo==True).all()
        else:
            # Para usuários normais, só vê seus próprios pets
            pets = Pet.query.filter(
                Pet.id_usuario == current_user_id,
                Pet.ativo==True
            ).all()
        
        pets_dict = [pet.to_dict() for pet in pets]
        
        # Opcionalmente, adicione informações sobre a quantidade de agendamentos para cada pet
        for pet_dict in pets_dict:
            from ...models.agendamento import Agendamento
            
            # Total de agendamentos
            agendamentos_count = Agendamento.query.filter(
                Agendamento.id_pet == pet_dict['id_pet']
            ).count()
            
            pet_dict['total_agendamentos'] = agendamentos_count
            
            # Último agendamento (se houver)
            ultimo_agendamento = Agendamento.query.filter(
                Agendamento.id_pet == pet_dict['id_pet']
            ).order_by(Agendamento.data_inicio.desc()).first()
            
            if ultimo_agendamento:
                pet_dict['ultimo_agendamento'] = {
                    'id_agendamento': ultimo_agendamento.id_agendamento,
                    'data_inicio': ultimo_agendamento.data_inicio.strftime('%d/%m/%Y %H:%M:%S') if ultimo_agendamento.data_inicio else None,
                    'status': ultimo_agendamento.status
                }
            else:
                pet_dict['ultimo_agendamento'] = None
        
        return success_response(pets_dict, 'Pets listados com sucesso')
    
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # Imprime o stack trace completo nos logs
        return error_response(f'Erro ao listar pets: {str(e)}', status_code=500)

@pet_bp.route('/pets/<int:id>', methods=['GET'])
@jwt_required()
def get_pet(id):
    """Retorna um pet específico pelo ID."""
    current_user_id = get_jwt_identity()
    return pet_service.get_pet_by_id(id, current_user_id)

@pet_bp.route('/pets', methods=['POST'])
@jwt_required()
def create_pet():
    """Adiciona um novo pet para um usuário existente."""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validação dos dados de entrada
    is_valid, errors = validate_pet(data)
    if not is_valid:
        return error_response('Dados do pet inválidos', errors=errors, status_code=400)
    
    return pet_service.create_pet(data, current_user_id)

@pet_bp.route('/pets/<int:id>', methods=['PUT'])
@jwt_required()
def update_pet(id):
    """Atualiza as informações de um pet."""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    return pet_service.update_pet(id, data, current_user_id)

@pet_bp.route('/pets/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_pet(id):
    """Marca um pet como inativo."""
    current_user_id = get_jwt_identity()
    return pet_service.delete_pet(id, current_user_id)