# app/utils/validators.py
import re
from typing import Dict, Any, List, Tuple, Optional
from flask import Request
from datetime import datetime

def validate_cpf(cpf: str) -> bool:
    """Valida um CPF brasileiro."""
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se o CPF tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    if resto < 2:
        dv1 = 0
    else:
        dv1 = 11 - resto
    
    # Verifica o primeiro dígito verificador
    if dv1 != int(cpf[9]):
        return False
    
    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    if resto < 2:
        dv2 = 0
    else:
        dv2 = 11 - resto
    
    # Verifica o segundo dígito verificador
    return dv2 == int(cpf[10])

def validate_email(email: str) -> bool:
    """Valida um endereço de e-mail."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_senha(senha: str) -> Tuple[bool, str]:
    """
    Valida uma senha seguindo critérios de segurança.
    Retorna uma tupla com (sucesso, mensagem)
    """
    if len(senha) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres"
    
    if not re.search(r'[A-Z]', senha):
        return False, "A senha deve conter pelo menos uma letra maiúscula"
    
    if not re.search(r'[a-z]', senha):
        return False, "A senha deve conter pelo menos uma letra minúscula"
    
    if not re.search(r'[0-9]', senha):
        return False, "A senha deve conter pelo menos um número"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
        return False, "A senha deve conter pelo menos um caractere especial"
    
    return True, "Senha válida"

def validate_usuario(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida os dados de um usuário.
    Retorna uma tupla com (sucesso, lista de erros)
    """
    errors = []
    
    required_fields = ['username', 'nome_user', 'cpf', 'cep', 'email', 'senha']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Campo '{field}' é obrigatório")
    
    if errors:
        return False, errors
    
    # Valida username
    if not re.match(r'^[a-zA-Z0-9_]{4,20}$', data['username']):
        errors.append("Username deve conter apenas letras, números e _ com 4 a 20 caracteres")
    
    # Valida CPF
    if not validate_cpf(data['cpf']):
        errors.append("CPF inválido")
    
    # Valida CEP
    if not re.match(r'^\d{5}-?\d{3}$', data['cep']):
        errors.append("CEP inválido. Formato esperado: 12345-678 ou 12345678")
    
    # Valida email
    if not validate_email(data['email']):
        errors.append("Email inválido")
    
    # Valida senha
    valido, msg = validate_senha(data['senha'])
    if not valido:
        errors.append(msg)
    
    return len(errors) == 0, errors

def validate_pet(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida os dados de um pet.
    Retorna uma tupla com (sucesso, lista de erros)
    """
    errors = []
    
    # Verifica campos obrigatórios
    if 'nome_pet' not in data or not data['nome_pet']:
        errors.append("Nome do pet é obrigatório")
    
    if 'id_usuario' not in data or not data['id_usuario']:
        errors.append("ID do usuário é obrigatório")
    
    # Validações opcionais
    if 'idade' in data and data['idade'] is not None:
        try:
            idade = int(data['idade'])
            if idade < 0 or idade > 30:
                errors.append("Idade do pet deve estar entre 0 e 30 anos")
        except ValueError:
            errors.append("Idade do pet deve ser um número inteiro")
    
    if 'peso' in data and data['peso'] is not None:
        try:
            peso = float(data['peso'])
            if peso <= 0 or peso > 100:
                errors.append("Peso do pet deve estar entre 0 e 100 kg")
        except ValueError:
            errors.append("Peso do pet deve ser um número")
    
    if 'sexo' in data and data['sexo'] and data['sexo'] not in ['M', 'F']:
        errors.append("Sexo do pet deve ser 'M' ou 'F'")
    
    if 'castrado' in data and data['castrado'] is not None:
        if not isinstance(data['castrado'], bool):
            errors.append("Campo 'castrado' deve ser verdadeiro ou falso")
    
    return len(errors) == 0, errors

def validate_agendamento(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida os dados de um agendamento.
    Retorna uma tupla com (sucesso, lista de erros)
    """
    errors = []
    
    # Campos obrigatórios
    required_fields = ['id_usuario', 'id_pet', 'data_entrada', 'data_saida']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Campo '{field}' é obrigatório")
    
    if errors:
        return False, errors
    
    # Validação de datas
    try:
        data_entrada = datetime.strptime(data['data_entrada'], "%d/%m/%Y %H:%M")
        data_saida = datetime.strptime(data['data_saida'], "%d/%m/%Y %H:%M")
        
        now = datetime.now()
        
        if data_entrada < now:
            errors.append("Data de entrada não pode ser no passado")
        
        if data_saida <= data_entrada:
            errors.append("Data de saída deve ser posterior à data de entrada")
        
        # Verificação de horários (hora certa ou meia em meia hora)
        if data_entrada.minute not in [0, 30] or data_saida.minute not in [0, 30]:
            errors.append("Horários devem ser na hora certa (HH:00) ou meia hora (HH:30)")
            
    except ValueError:
        errors.append("Data inválida. Use o formato DD/MM/AAAA HH:MM")
    
    return len(errors) == 0, errors

def validate_pagamento(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Valida os dados de um pagamento.
    Retorna uma tupla com (sucesso, lista de erros)
    """
    errors = []
    
    # Campos obrigatórios
    required_fields = ['id_agendamento', 'valor']
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"Campo '{field}' é obrigatório")
    
    if errors:
        return False, errors
    
    # Validação do valor
    try:
        valor = float(data['valor'])
        if valor <= 0:
            errors.append("Valor do pagamento deve ser maior que zero")
    except ValueError:
        errors.append("Valor do pagamento deve ser um número")
    
    # Validação do status
    if 'status' in data and data['status'] not in ['pendente', 'concluido']:
        errors.append("Status deve ser 'pendente' ou 'concluido'")
    
    # Validação da data de pagamento
    if 'data_pagamento' in data and data['data_pagamento']:
        try:
            datetime.strptime(data['data_pagamento'], "%d/%m/%Y %H:%M")
        except ValueError:
            errors.append("Data de pagamento inválida. Use o formato DD/MM/AAAA HH:MM")
    
    return len(errors) == 0, errors

# Funções adicionais para validação de agendamento e pagamento

def validate_required_fields(data: Dict[str, Any], fields: List[str]) -> List[str]:
    """Verifica se todos os campos obrigatórios estão presentes e não vazios."""
    missing = []
    for field in fields:
        if field not in data or data[field] is None or data[field] == "":
            missing.append(field)
    return missing

def validate_datetime_format(date_str: str) -> bool:
    """Valida se a string de data está no formato DD/MM/YYYY HH:MM."""
    try:
        datetime.strptime(date_str, "%d/%m/%Y %H:%M")
        return True
    except ValueError:
        return False

def validate_payment_type(payment_type: str, valid_types: List[str]) -> bool:
    """Valida se o tipo de pagamento é válido."""
    return payment_type.lower() in [t.lower() for t in valid_types]

def sanitize_input(input_str: str) -> str:
    """Sanitiza entrada de texto para prevenir injeção."""
    if not input_str:
        return ""
    # Remove caracteres potencialmente perigosos
    sanitized = re.sub(r'[<>&\'"()]', '', input_str)
    return sanitized

def validate_date_range(start_date: datetime, end_date: datetime) -> Tuple[bool, Optional[str]]:
    """Valida se a data de início é anterior à data de fim."""
    if start_date >= end_date:
        return False, "A data de início deve ser anterior à data de fim"
    return True, None

def validate_positive_number(value: float) -> bool:
    """Valida se o número é positivo."""
    try:
        return float(value) > 0
    except (ValueError, TypeError):
        return False

def validate_service_id(service_id: int, valid_services: List[int]) -> bool:
    """Valida se o ID do serviço está na lista de serviços válidos."""
    return service_id in valid_services

def validate_service_hours(hora: int, minuto: int) -> bool:
    """Valida se o horário está dentro das regras (hora em ponto ou meia hora)."""
    return 0 <= hora < 24 and minuto in [0, 30]

def validate_service_datetime(date_str: str) -> Tuple[bool, Optional[str]]:
    """
    Valida se a string de data/hora segue o formato correto e as regras de horário.
    Retorna (sucesso, mensagem de erro opcional)
    """
    try:
        dt = datetime.strptime(date_str, "%d/%m/%Y %H:%M")
        
        # Verifica se o minuto é 0 ou 30
        if dt.minute not in [0, 30]:
            return False, "Os horários devem ser na hora exata ou na meia hora (ex: 09:00 ou 09:30)"
        
        # Verifica se a data não é no passado
        if dt < datetime.now():
            return False, "A data não pode estar no passado"
        
        return True, None
    except ValueError:
        return False, "Formato de data inválido. Use o formato DD/MM/YYYY HH:MM (ex: 01/06/2025 14:30)"