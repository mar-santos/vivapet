# app/models/agendamento.py
from ..extensions import db
from datetime import datetime
from typing import Dict, Any

class Agendamento(db.Model):
    __tablename__ = 'agendamento'
    
    id_agendamento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    id_pet = db.Column(db.Integer, db.ForeignKey('pet.id_pet'), nullable=False)
    id_servico = db.Column(db.Integer, db.ForeignKey('servico.id_servico'), nullable=False)
    data_inicio = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='agendado')  # agendado, confirmado, concluido, cancelado
    observacoes = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    usuario = db.relationship("Usuario", back_populates="agendamentos")
    pet = db.relationship("Pet", back_populates="agendamentos")
    servico = db.relationship("Servico", back_populates="agendamentos")
    pagamentos = db.relationship("Pagamento", back_populates="agendamento", cascade="all, delete-orphan")
    itens_servico = db.relationship("AgendamentoServico", back_populates="agendamento", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto Agendamento para um dicionário."""
        return {
            'id_agendamento': self.id_agendamento,
            'id_usuario': self.id_usuario,
            'id_pet': self.id_pet,
            'id_servico': self.id_servico,
            'data_inicio': self.data_inicio.strftime('%d/%m/%Y %H:%M:%S') if self.data_inicio else None,
            'data_fim': self.data_fim.strftime('%d/%m/%Y %H:%M:%S') if self.data_fim else None,
            'status': self.status,
            'observacoes': self.observacoes,
            'data_criacao': self.data_criacao.strftime('%d/%m/%Y %H:%M:%S') if self.data_criacao else None,
            'usuario': self.usuario.nome_user if self.usuario else None,
            'pet': self.pet.nome_pet if self.pet else None,
            'servico': self.servico.nome_servico if self.servico else None,
            'valor_total': sum(item.quantidade * item.valor_unitario for item in self.itens_servico) if self.itens_servico else 0
        }
    
    def __repr__(self) -> str:
        return f'<Agendamento {self.id_agendamento}>'