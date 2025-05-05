# app/models/servico.py
from ..extensions import db
from typing import Dict, Any

class Servico(db.Model):
    __tablename__ = 'servico'
    
    id_servico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_servico = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    valor_hora = db.Column(db.Float)
    valor_dia = db.Column(db.Float)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    # Não criar relacionamento direto com Agendamento, apenas através de AgendamentoServico
    agendamentos_servicos = db.relationship("AgendamentoServico", back_populates="servico")
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto Servico para um dicionário."""
        return {
            'id_servico': self.id_servico,
            'nome_servico': self.nome_servico,
            'descricao': self.descricao,
            'valor_hora': self.valor_hora,
            'valor_dia': self.valor_dia,
            'ativo': self.ativo
        }
    
    def __repr__(self) -> str:
        return f'<Servico {self.id_servico}: {self.nome_servico}>'