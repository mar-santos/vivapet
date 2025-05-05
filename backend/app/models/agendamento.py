# app/models/agendamento.py
from ..extensions import db
from datetime import datetime
from typing import Dict, Any, List, Optional

class Agendamento(db.Model):
    __tablename__ = 'agendamento'
    __table_args__ = {'extend_existing': True}  # Adicionado para evitar conflitos
    
    id_agendamento = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    id_pet = db.Column(db.Integer, db.ForeignKey('pet.id_pet'), nullable=False)
    id_servico = db.Column(db.Integer, db.ForeignKey('servico.id_servico'), nullable=False)
    data_inicio = db.Column(db.DateTime, nullable=False)
    data_fim = db.Column(db.DateTime, nullable=False)
    observacoes = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    valor_total = db.Column(db.Float)
    status = db.Column(db.String(20), default='agendado')
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos - usando foreign_keys para evitar conflitos de backref
    usuario = db.relationship('Usuario', foreign_keys=[id_usuario])
    pet = db.relationship('Pet', foreign_keys=[id_pet])
    servico = db.relationship('Servico', foreign_keys=[id_servico])
    itens_servico = db.relationship('AgendamentoServico', back_populates='agendamento', cascade='all, delete-orphan')
    
    # Modificar para corresponder ao nome usado em Pagamento
    pagamentos = db.relationship('Pagamento', back_populates='agendamento', cascade='all, delete-orphan')
    
    def __repr__(self) -> str:
        return f'<Agendamento {self.id_agendamento}>'
    
    def calcular_valor_total(self) -> float:
        """Calcula o valor total do agendamento com base nos itens de serviço."""
        if self.itens_servico:
            return sum(item.quantidade * item.valor_unitario for item in self.itens_servico)
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto Agendamento para um dicionário."""
        return {
            'id_agendamento': self.id_agendamento,
            'id_usuario': self.id_usuario,
            'id_pet': self.id_pet,
            'id_servico': self.id_servico,
            'data_inicio': self.data_inicio.strftime('%d/%m/%Y %H:%M') if self.data_inicio else None,
            'data_fim': self.data_fim.strftime('%d/%m/%Y %H:%M') if self.data_fim else None,
            'observacoes': self.observacoes,
            'status': self.status,
            'ativo': self.ativo,
            'valor_total': self.valor_total or self.calcular_valor_total(),
            'data_criacao': self.data_criacao.strftime('%d/%m/%Y %H:%M') if self.data_criacao else None,
            'usuario': self.usuario.nome_user if self.usuario else None,
            'pet': self.pet.nome_pet if self.pet else None,
            'servico': self.servico.nome_servico if self.servico else None,
            'itens_servico': [item.to_dict() for item in self.itens_servico] if self.itens_servico else [],
            'pagamentos': [pagamento.to_dict() for pagamento in self.pagamentos] if self.pagamentos else []
        }