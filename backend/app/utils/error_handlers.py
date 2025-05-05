# app/utils/error_handlers.py
from flask import jsonify

def register_error_handlers(app):
    """Registra tratadores de erro para a aplicação."""
    
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            'status': 'error',
            'message': 'Requisição inválida',
            'error': str(e)
        }), 400
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            'status': 'error',
            'message': 'Recurso não encontrado',
            'error': str(e)
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({
            'status': 'error',
            'message': 'Método não permitido',
            'error': str(e)
        }), 405
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({
            'status': 'error',
            'message': 'Erro interno do servidor',
            'error': str(e)
        }), 500