# app/models/usuario.py
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import relationship
from ..extensions import db, bcrypt  # Importando das extensões centralizadas
from sqlalchemy.ext.hybrid import hybrid_property

class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    nome_user = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    endereco = db.Column(db.String(255))
    cep = db.Column(db.String(9), nullable=False)
    telefone = db.Column(db.String(20))
    foto_user = db.Column(db.LargeBinary)
    email = db.Column(db.String(120), unique=True, nullable=False)
    _senha = db.Column('senha', db.String(128), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    pets = relationship("Pet", back_populates="usuario", lazy="joined", 
                         cascade="all, delete-orphan")
    agendamentos = relationship("Agendamento", back_populates="usuario", lazy="dynamic",
                                cascade="all, delete-orphan")
    
    @hybrid_property
    def senha(self) -> str:
        return self._senha
    
    @senha.setter
    def senha(self, senha_texto: str) -> None:
        self._senha = bcrypt.generate_password_hash(senha_texto).decode('utf-8')
    
    def verificar_senha(self, senha: str) -> bool:
        """Verifica se a senha informada corresponde ao hash armazenado."""
        return bcrypt.check_password_hash(self._senha, senha)
    
    def to_dict(self, include_pets: bool = True) -> Dict[str, Any]:
        """
        Converte o modelo em um dicionário para serialização.
        
        Args:
            include_pets: Se True, inclui os pets do usuário no dicionário
            
        Returns:
            Dicionário com os dados do usuário
        """
        result = {
            'id_usuario': self.id_usuario,
            'username': self.username,
            'nome_user': self.nome_user,
            'cpf': self.cpf,
            'endereco': self.endereco,
            'cep': self.cep,
            'telefone': self.telefone,
            'email': self.email,
            'data_cadastro': self.data_cadastro.strftime('%d/%m/%Y %H:%M:%S') if self.data_cadastro else None,
            'ativo': self.ativo,
            'is_admin': self.is_admin
        }
        
        if include_pets and self.pets:
            # Versão mais detalhada dos pets
            result['pets'] = [
                {
                    'id_pet': pet.id_pet, 
                    'nome_pet': pet.nome_pet,
                    'raca': pet.raca,
                    'idade': pet.idade,
                    'sexo': pet.sexo,
                    'peso': pet.peso,
                    'castrado': pet.castrado
                } 
                for pet in self.pets if pet.ativo
            ]
            
        return result
    
    def __repr__(self) -> str:
        return f'<Usuario {self.username}>'