# app/api/routes/usuario_routes.py
from flask import Blueprint, request, jsonify, render_template
from ...extensions import db
from ...models.usuario import Usuario
from ...services.user_service import UserService
from ...utils.api_responses import success_response, error_response
from ...utils.validators import validate_usuario
from flask_jwt_extended import jwt_required, get_jwt_identity

usuario_bp = Blueprint('usuarios', __name__)
user_service = UserService()

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
    """Cria um novo usuário."""
    data = request.get_json()
    
    # Validação dos dados de entrada
    is_valid, errors = validate_usuario(data)
    if not is_valid:
        return error_response('Dados de usuário inválidos', errors=errors, status_code=400)
    
    return user_service.create_usuario(data)

@usuario_bp.route('/usuarios/<int:id>', methods=['PUT'])
@jwt_required()
def update_usuario(id):
    """Atualiza um usuário existente."""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    return user_service.update_usuario(id, data, current_user_id)

@usuario_bp.route('/usuarios/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_usuario(id):
    """Marca um usuário como inativo."""
    current_user_id = get_jwt_identity()
    return user_service.delete_usuario(id, current_user_id)

# Adicionar em app/api/routes/usuario_routes.py
@usuario_bp.route('/usuarios/diagnostico', methods=['GET'])
def diagnostico_db():
    """Rota temporária para diagnóstico do banco de dados."""
    import logging, time
    from flask import current_app
    
    logger = logging.getLogger(__name__)
    
    try:
        # 1. Verificar configuração do banco de dados
        db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Não configurado')
        
        # 2. Contar registros na tabela usuário
        count = Usuario.query.count()
        
        # 3. Tentar criar um usuário de teste diretamente
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
        
        # 4. Verificar se foi criado
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