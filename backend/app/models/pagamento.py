# app/models/pagamento.py
from ..extensions import db
from datetime import datetime
from typing import Dict, Any

class Pagamento(db.Model):
    __tablename__ = 'pagamento'
    
    id_pagamento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_agendamento = db.Column(db.Integer, db.ForeignKey('agendamento.id_agendamento'), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente, processando, concluido, cancelado
    tipo_pagamento = db.Column(db.String(50))  # pix, cartao, boleto, dinheiro
    data_pagamento = db.Column(db.DateTime)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    agendamento = db.relationship("Agendamento", back_populates="pagamentos")
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto Pagamento para um dicionário."""
        return {
            'id_pagamento': self.id_pagamento,
            'id_agendamento': self.id_agendamento,
            'valor': self.valor,
            'status': self.status,
            'tipo_pagamento': self.tipo_pagamento,
            'data_pagamento': self.data_pagamento.strftime('%d/%m/%Y %H:%M:%S') if self.data_pagamento else None,
            'data_criacao': self.data_criacao.strftime('%d/%m/%Y %H:%M:%S') if self.data_criacao else None,
            'agendamento': {
                'id_agendamento': self.agendamento.id_agendamento,
                'status': self.agendamento.status
            } if self.agendamento else None
        }
    
    def __repr__(self) -> str:
        return f'<Pagamento {self.id_pagamento}>'