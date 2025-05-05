# app/models/__init__.py
# Importar todos os modelos para garantir que o SQLAlchemy os reconheça

from .usuario import Usuario
from .pet import Pet
from .servico import Servico
from .agendamento import Agendamento
from .pagamento import Pagamento
from .agendamento_servico import AgendamentoServico