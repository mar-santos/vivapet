# app/models/pet.py
from ..extensions import db
from datetime import datetime
from typing import Dict, Any

class Pet(db.Model):
    __tablename__ = 'pet'
    
    id_pet = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    nome_pet = db.Column(db.String(100), nullable=False)
    raca = db.Column(db.String(100))
    idade = db.Column(db.Integer)
    sexo = db.Column(db.String(1))  # M ou F
    peso = db.Column(db.Float)
    castrado = db.Column(db.Boolean, default=False)
    alimentacao = db.Column(db.Text)
    saude = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    foto_pet = db.Column(db.LargeBinary)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    usuario = db.relationship("Usuario", back_populates="pets")
    agendamentos = db.relationship("Agendamento", back_populates="pet")
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto Pet para um dicionário."""
        return {
            'id_pet': self.id_pet,
            'id_usuario': self.id_usuario,
            'nome_pet': self.nome_pet,
            'raca': self.raca,
            'idade': self.idade,
            'sexo': self.sexo,
            'peso': self.peso,
            'castrado': self.castrado,
            'alimentacao': self.alimentacao,
            'saude': self.saude,
            'ativo': self.ativo,
            'data_cadastro': self.data_cadastro.strftime('%d/%m/%Y %H:%M:%S') if self.data_cadastro else None
        }
    
    def __repr__(self) -> str:
        return f'<Pet {self.nome_pet}>'