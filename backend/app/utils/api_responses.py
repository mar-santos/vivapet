# app/utils/api_responses.py
from typing import Dict, Any, List, Optional, Union
from flask import jsonify

def success_response(
    data: Optional[Union[Dict[str, Any], List[Any], str]] = None, 
    message: str = "Operação realizada com sucesso", 
    status_code: int = 200
) -> tuple:
    """
    Cria uma resposta de sucesso padronizada.
    
    Args:
        data: Os dados a serem retornados na resposta.
        message: Mensagem descritiva do sucesso.
        status_code: Código HTTP de status da resposta.
    
    Returns:
        Uma tupla contendo a resposta JSON e o código de status.
    """
    response = {
        'status': 'success',
        'message': message
    }
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code

def error_response(
    message: str = "Ocorreu um erro", 
    errors: Optional[Union[List[str], Dict[str, List[str]]]] = None, 
    status_code: int = 400
) -> tuple:
    """
    Cria uma resposta de erro padronizada.
    
    Args:
        message: Mensagem descritiva do erro.
        errors: Lista de erros ou dicionário de campos e seus erros.
        status_code: Código HTTP de status da resposta.
    
    Returns:
        Uma tupla contendo a resposta JSON e o código de status.
    """
    response = {
        'status': 'error',
        'message': message
    }
    
    if errors:
        response['errors'] = errors
    
    return jsonify(response), status_code