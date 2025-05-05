# app/models/servico.py
from ..extensions import db
from datetime import datetime
from typing import Dict, Any

class Servico(db.Model):
    __tablename__ = 'servico'
    
    id_servico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_servico = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    valor_hora = db.Column(db.Float)
    valor_dia = db.Column(db.Float)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    agendamentos = db.relationship("Agendamento", back_populates="servico")
    
    # Modificando este relacionamento para resolver o conflito
    agendamentos_servicos = db.relationship("AgendamentoServico", 
                                            back_populates="servico")
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto Servico para um dicionário."""
        return {
            'id_servico': self.id_servico,
            'nome_servico': self.nome_servico,
            'descricao': self.descricao,
            'valor_hora': self.valor_hora,
            'valor_dia': self.valor_dia,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.strftime('%d/%m/%Y %H:%M:%S') if self.data_criacao else None
        }
    
    def __repr__(self) -> str:
        return f'<Servico {self.nome_servico}>'