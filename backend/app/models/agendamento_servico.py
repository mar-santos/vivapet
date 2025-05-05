# app/models/agendamento_servico.py
from ..extensions import db
from datetime import datetime

class AgendamentoServico(db.Model):
    __tablename__ = 'agendamento_servico'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_agendamento = db.Column(db.Integer, db.ForeignKey('agendamento.id_agendamento'), nullable=False)
    id_servico = db.Column(db.Integer, db.ForeignKey('servico.id_servico'), nullable=False)
    quantidade = db.Column(db.Integer, default=1)
    valor_unitario = db.Column(db.Float, nullable=False)
    observacoes = db.Column(db.String(255))
    
    # Relacionamentos - corrigidos para resolver o conflito
    agendamento = db.relationship('Agendamento', back_populates='itens_servico')
    servico = db.relationship('Servico', back_populates='agendamentos_servicos')
    
    def __repr__(self):
        return f'<AgendamentoServico {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_agendamento': self.id_agendamento,
            'id_servico': self.id_servico,
            'quantidade': self.quantidade,
            'valor_unitario': self.valor_unitario,
            'observacoes': self.observacoes,
            'servico': self.servico.to_dict() if self.servico else None
        }