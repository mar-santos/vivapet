# app/api/routes/auth_routes.py
from flask import Blueprint, request, jsonify, current_app
from ...extensions import bcrypt, jwt, jwt_blacklist  # Importar jwt_blacklist daqui
from ...models.usuario import Usuario
from ...services.auth_service import AuthService
from ...utils.api_responses import success_response, error_response
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Endpoint para autenticar um usuário."""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('senha'):
        return error_response('Credenciais incompletas', status_code=400)
    
    username = data.get('username')
    senha = data.get('senha')
    
    logger.info(f"Tentativa de login para usuário: {username}")
    
    # DEBUG: Verificar usuário e senha manualmente
    usuario = Usuario.query.filter_by(username=username).first()
    if usuario:
        print(f"DEBUG: Usuário encontrado: {username}")
        senha_correta = usuario.verificar_senha(senha)
        print(f"DEBUG: Senha correta? {senha_correta}")
        
        # Verificar a chave JWT que será usada
        jwt_key = current_app.config.get('JWT_SECRET_KEY')
        print(f"DEBUG: JWT_SECRET_KEY durante login: {jwt_key[:10]}... (tamanho: {len(jwt_key)})")
    else:
        print(f"DEBUG: Usuário não encontrado: {username}")
    
    result = auth_service.authenticate(username, senha)
    
    if not result['success']:
        logger.warning(f"Falha na autenticação para usuário: {username}")
        return error_response(result['message'], status_code=401)
    
    # DEBUG: Mostrar o token gerado
    print(f"DEBUG: Token gerado: {result['data']['access_token'][:20]}...")
    
    logger.info(f"Login bem-sucedido para usuário: {username}")
    return success_response(result['data'], message='Login realizado com sucesso')

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Endpoint para logout (invalidar o token JWT)."""
    current_user = get_jwt_identity()
    jti = get_jwt()["jti"]
    logger.info(f"Logout para usuário ID: {current_user}, JTI: {jti}")
    auth_service.blacklist_token(jti)
    return success_response(message='Logout realizado com sucesso')

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Endpoint para renovar o token de acesso."""
    current_user = get_jwt_identity()
    logger.info(f"Renovação de token para usuário ID: {current_user}")
    new_access_token = create_access_token(identity=current_user)
    return success_response({'access_token': new_access_token}, 'Token renovado com sucesso')

@auth_bp.route('/debug-token', methods=['GET'])
@jwt_required(optional=True)
def debug_token():
    """Rota de diagnóstico para verificar tokens JWT."""
    # DEBUG: Log da chave secreta usada para verificação
    jwt_key = current_app.config.get('JWT_SECRET_KEY')
    print(f"DEBUG: JWT_SECRET_KEY durante verificação: {jwt_key[:10]}... (tamanho: {len(jwt_key)})")
    
    # Tentar obter identidade do usuário
    current_user_id = get_jwt_identity()
    
    # Capturar todos os cabeçalhos para diagnóstico
    all_headers = dict(request.headers)
    auth_header = all_headers.get('Authorization', '')
    
    # Informações sobre a configuração JWT
    jwt_config = {
        'secret_key_prefix': current_app.config.get('JWT_SECRET_KEY')[:3] + '...' if current_app.config.get('JWT_SECRET_KEY') else None,
        'token_location': current_app.config.get('JWT_TOKEN_LOCATION'),
        'header_name': current_app.config.get('JWT_HEADER_NAME'),
        'header_type': current_app.config.get('JWT_HEADER_TYPE')
    }
    
    if current_user_id:
        # Se há um usuário autenticado, pegar detalhes do token
        claims = get_jwt()
        token_info = {
            'jti': claims.get('jti'),
            'tipo': claims.get('type'),
            'emitido_em': claims.get('iat'),
            'expira_em': claims.get('exp'),
            'csrf': claims.get('csrf', None)
        }
        status = 'valid'
        message = 'Token válido'
    else:
        # Sem token ou token inválido
        token_info = None
        status = 'invalid_or_missing'
        message = 'Token inválido ou ausente'
    
    # Criar resposta detalhada para diagnóstico
    response_data = {
        'status': status,
        'message': message,
        'user_id': current_user_id,
        'auth_header': auth_header,
        'token_info': token_info,
        'jwt_config': jwt_config,
        'request_info': {
            'endpoint': request.endpoint,
            'method': request.method,
            'url': request.url,
            'remote_addr': request.remote_addr
        }
    }
    
    # Log para diagnóstico do servidor
    logger.info(f"Diagnóstico de token: {status} para IP {request.remote_addr}")
    
    return jsonify(response_data)

@auth_bp.route('/verify-auth', methods=['GET'])
def verify_auth():
    """Rota simples para verificar o cabeçalho de autorização sem JWT."""
    auth_header = request.headers.get('Authorization', 'Não encontrado')
    
    # Análise manual do cabeçalho de autorização
    parts = auth_header.split()
    token_type = parts[0] if len(parts) > 0 else "Nenhum"
    token_value = parts[1] if len(parts) > 1 else "Nenhum"
    token_prefix = token_value[:10] + "..." if token_value != "Nenhum" else "Nenhum"
    
    return jsonify({
        'status': 'success',
        'message': 'Verificação de cabeçalho de autorização',
        'authorization_header': auth_header,
        'analysis': {
            'token_type': token_type,
            'token_prefix': token_prefix,
            'valid_format': token_type == 'Bearer' and token_value != "Nenhum"
        },
        'all_headers': dict(request.headers)
    })

@auth_bp.route('/token-diagnostico', methods=['GET'])
def token_diagnostico():
    """Função específica para diagnosticar problemas com JWT."""
    import jwt as pyjwt
    
    # Capturar o cabeçalho de autorização
    auth_header = request.headers.get('Authorization', 'Nenhum')
    
    # Capturar a configuração JWT
    jwt_config = {
        'secret_key_inicio': current_app.config.get('JWT_SECRET_KEY')[:10] + '...' if current_app.config.get('JWT_SECRET_KEY') else None,
        'secret_key_tamanho': len(current_app.config.get('JWT_SECRET_KEY', '')),
        'token_location': current_app.config.get('JWT_TOKEN_LOCATION'),
        'header_name': current_app.config.get('JWT_HEADER_NAME'),
        'header_type': current_app.config.get('JWT_HEADER_TYPE'),
        'blacklist_enabled': current_app.config.get('JWT_BLACKLIST_ENABLED')
    }
    
    # Análise do cabeçalho
    token_parts = auth_header.split()
    
    result = {
        'status': 'info',
        'auth_header': auth_header,
        'jwt_config': jwt_config,
        'token_info': None,
        'token_decode': None,
        'token_verification': None
    }
    
    # Verificar se há um token
    if len(token_parts) == 2 and token_parts[0] == 'Bearer':
        token = token_parts[1]
        result['token_info'] = {
            'primeiros_caracteres': token[:15] + '...',
            'tamanho': len(token)
        }
        
        # Tentar decodificar sem verificar
        try:
            decoded = pyjwt.decode(token, options={"verify_signature": False})
            result['token_decode'] = decoded
            
            # Tentar verificar a assinatura
            try:
                secret_key = current_app.config.get('JWT_SECRET_KEY')
                # DEBUG: Mostrar a chave usada para verificação
                print(f"DEBUG: Verificando token com chave: {secret_key[:10]}... (tamanho: {len(secret_key)})")
                
                pyjwt.decode(token, key=secret_key, algorithms=['HS256'])
                result['token_verification'] = {
                    'status': 'success',
                    'message': 'Assinatura verificada com sucesso'
                }
            except Exception as e:
                result['token_verification'] = {
                    'status': 'error',
                    'message': str(e)
                }
        except Exception as e:
            result['token_decode'] = {
                'status': 'error',
                'message': str(e)
            }
    
    # Verificação da blacklist (se configurada)
    if current_app.config.get('JWT_BLACKLIST_ENABLED') and result.get('token_decode') and isinstance(result['token_decode'], dict) and 'jti' in result['token_decode']:
        # Usar a referência global em vez de importar
        result['blacklist_info'] = {
            'blocklist_size': len(jwt_blacklist),
            'token_in_blocklist': result['token_decode']['jti'] in jwt_blacklist
        }
    
    return jsonify(result)