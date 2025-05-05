from ..extensions import db
from typing import Dict, Any

class AgendamentoServico(db.Model):
    __tablename__ = 'agendamento_servico'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_agendamento = db.Column(db.Integer, db.ForeignKey('agendamento.id_agendamento'), nullable=False)
    id_servico = db.Column(db.Integer, db.ForeignKey('servico.id_servico'), nullable=False)
    quantidade = db.Column(db.Integer, default=1)
    valor_unitario = db.Column(db.Float, nullable=False)
    observacoes = db.Column(db.String(255))
    data_criacao = db.Column(db.DateTime, default=db.func.current_timestamp())
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    agendamento = db.relationship('Agendamento', back_populates='itens_servico')
    servico = db.relationship('Servico', back_populates='agendamentos_servicos')
    
    def calcular_valor_total(self) -> float:
        """Calcula o valor total deste item de serviço (quantidade * valor_unitario)."""
        return self.quantidade * self.valor_unitario
    
    def __repr__(self) -> str:
        return f'<AgendamentoServico {self.id}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto para um dicionário."""
        return {
            'id': self.id,
            'id_agendamento': self.id_agendamento,
            'id_servico': self.id_servico,
            'quantidade': self.quantidade,
            'valor_unitario': self.valor_unitario,
            'valor_total': self.calcular_valor_total(),
            'observacoes': self.observacoes,
            'ativo': self.ativo,
            'servico': {
                'id_servico': self.servico.id_servico,
                'nome_servico': self.servico.nome_servico,
                'valor_hora': self.servico.valor_hora,
                'valor_dia': self.servico.valor_dia
            } if self.servico else None
        }
