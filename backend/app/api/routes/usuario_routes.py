from flask import Blueprint, request, jsonify, render_template
from ...extensions import db
from ...models.usuario import Usuario
from ...services.user_service import UserService
from ...utils.api_responses import success_response, error_response
from ...utils.validators import validate_usuario
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.pet import Pet
import logging

usuario_bp = Blueprint('usuarios', __name__)
user_service = UserService()
logger = logging.getLogger(__name__)

def str2bool(value):
    """Converte 'true'/'false' (string) para booleano real."""
    return str(value).lower() in ("true", "1", "yes", "on")

@usuario_bp.route('/cadastro')
def cadastro():
    return render_template('usuarios_cadastrar.html')

@usuario_bp.route('/usuarios', methods=['GET'])
@jwt_required()
def get_usuarios():
    """Retorna todos os usuários ativos."""
    current_user_id = get_jwt_identity()
    return user_service.get_all_usuarios(current_user_id)

@usuario_bp.route('/usuarios/<int:id>', methods=['GET'])
@jwt_required()
def get_usuario(id):
    """Retorna um usuário específico pelo ID."""
    current_user_id = get_jwt_identity()
    return user_service.get_usuario_by_id(id, current_user_id)

@usuario_bp.route('/usuarios', methods=['POST'])
def create_usuario():
    """Cria um novo usuário e seus pets."""
    data = request.form.to_dict()
    foto_user = request.files.get('foto_user')

    logger.info(f"Dados recebidos na rota /usuarios (POST): {data}")

    data['ativo'] = str2bool(data.get('ativo', False))
    data['is_admin'] = str2bool(data.get('is_admin', False))

    if foto_user:
        data['foto_user'] = foto_user.read()

    is_valid, errors = validate_usuario(data)
    if not is_valid:
        logger.warning(f"Dados de usuário inválidos: {errors}")
        return error_response('Dados de usuário inválidos', errors=errors, status_code=400)

    try:
        usuario = user_service.create_usuario(data)
        logger.info(f"Usuário criado com sucesso. ID: {usuario.id_usuario}")
        return success_response(usuario.to_dict(include_pets=True), 'Usuário criado com sucesso', 201)

    except ValueError as e:
        db.session.rollback()
        logger.error(f"Erro de validação ao criar usuário: {str(e)}")
        return error_response(str(e), status_code=400)

    except Exception as e:
        db.session.rollback()
        logger.exception(f"Erro inesperado ao criar usuário: {str(e)}")
        return error_response(f'Erro ao criar usuário: {str(e)}', status_code=500)

@usuario_bp.route('/usuarios/<int:id>', methods=['PUT'])
@jwt_required()
def update_usuario(id):
    """Atualiza um usuário existente."""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if 'ativo' in data:
        data['ativo'] = str2bool(data.get('ativo'))
    if 'is_admin' in data:
        data['is_admin'] = str2bool(data.get('is_admin'))

    return user_service.update_usuario(id, data, current_user_id)

@usuario_bp.route('/usuarios/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_usuario(id):
    """Marca um usuário como inativo."""
    current_user_id = get_jwt_identity()
    return user_service.delete_usuario(id, current_user_id)

@usuario_bp.route('/usuarios/diagnostico', methods=['GET'])
def diagnostico_db():
    """Rota temporária para diagnóstico do banco de dados."""
    import logging, time
    from flask import current_app

    logger = logging.getLogger(__name__)

    try:
        db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Não configurado')
        count = Usuario.query.count()

        usuario_teste = Usuario(
            username=f"teste_{int(time.time())}",
            nome_user="Usuário Teste Diagnóstico",
            cpf=f"{int(time.time())%999}.{int(time.time())%999}.{int(time.time())%999}-{int(time.time())%99}",
            email=f"teste_{int(time.time())}@teste.com",
            cep="12345-678",
            ativo=True
        )
        usuario_teste.senha = "teste123"

        logger.info("Adicionando usuário de diagnóstico à sessão")
        db.session.add(usuario_teste)
        logger.info("Executando commit de diagnóstico")
        db.session.commit()

        id_teste = usuario_teste.id_usuario
        verificacao = Usuario.query.get(id_teste)

        return jsonify({
            'status': 'success',
            'database': {
                'db_uri': db_uri.replace('sqlite:///', 'sqlite:// [path omitted for security]'),
                'count_before': count,
                'test_user_id': id_teste,
                'verification_success': verificacao is not None,
                'verification_username': verificacao.username if verificacao else None
            }
        })
    except Exception as e:
        logger.error(f"Erro no diagnóstico: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500