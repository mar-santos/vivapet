"""Add ativo and data_criacao columns to agendamento table

Revision ID: custom_migration
Revises: 
Create Date: 2023-06-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'custom_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Adiciona a coluna ativo à tabela agendamento
    op.add_column('agendamento', sa.Column('ativo', sa.Boolean(), nullable=True, server_default=sa.text('1')))
    
    # Adiciona a coluna data_criacao à tabela agendamento (se não existir)
    try:
        op.add_column('agendamento', sa.Column('data_criacao', sa.DateTime(), nullable=True, 
                     server_default=sa.text('CURRENT_TIMESTAMP')))
    except:
        pass  # Ignora se a coluna já existir
    
    # Adiciona a coluna valor_total se não existir
    try:
        op.add_column('agendamento', sa.Column('valor_total', sa.Float(), nullable=True))
    except:
        pass


def downgrade():
    # Remove as colunas adicionadas
    op.drop_column('agendamento', 'ativo')
    op.drop_column('agendamento', 'data_criacao')
    op.drop_column('agendamento', 'valor_total')
