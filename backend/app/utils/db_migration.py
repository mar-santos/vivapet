import sqlite3
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_columns_to_tables():
    """
    Adiciona as colunas necessárias às tabelas do banco de dados:
    - agendamento_servico: adiciona data_criacao e ativo
    - agendamento: adiciona ativo (se não existir)
    - pagamento: adiciona ativo (se não existir)
    """
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    INSTANCE_DIR = BASE_DIR / 'instance'
    db_path = INSTANCE_DIR / "dbVivapet.db"
    
    logger.info(f"Caminho do banco de dados: {db_path}")
    
    # Verificar se o arquivo de banco de dados existe
    if not os.path.exists(db_path):
        logger.error(f"Arquivo de banco de dados não encontrado em: {db_path}")
        return
    
    # Conectar ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Lista de tabelas para verificar e atualizar
        tabelas = ['agendamento_servico', 'agendamento', 'pagamento']
        
        for tabela in tabelas:
            # Verificar se a tabela existe
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabela}'")
            if not cursor.fetchone():
                logger.warning(f"Tabela {tabela} não existe no banco de dados.")
                continue
            
            # Verificar colunas existentes
            cursor.execute(f"PRAGMA table_info({tabela})")
            colunas = [coluna[1] for coluna in cursor.fetchall()]
            logger.info(f"Colunas existentes na tabela {tabela}: {colunas}")
            
            # Para a tabela agendamento_servico, verificar e adicionar data_criacao
            if tabela == 'agendamento_servico' and 'data_criacao' not in colunas:
                logger.info(f"Adicionando coluna data_criacao à tabela {tabela}...")
                cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP")
                conn.commit()
                logger.info(f"Coluna data_criacao adicionada com sucesso à tabela {tabela}!")
            
            # Para todas as tabelas, verificar e adicionar ativo
            if 'ativo' not in colunas:
                logger.info(f"Adicionando coluna ativo à tabela {tabela}...")
                cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN ativo BOOLEAN DEFAULT 1")
                conn.commit()
                logger.info(f"Coluna ativo adicionada com sucesso à tabela {tabela}!")
            
            # Verificar se as colunas foram adicionadas
            cursor.execute(f"PRAGMA table_info({tabela})")
            colunas_atualizadas = [coluna[1] for coluna in cursor.fetchall()]
            logger.info(f"Colunas atualizadas para {tabela}: {colunas_atualizadas}")
        
    except Exception as e:
        logger.error(f"Erro ao adicionar colunas: {str(e)}")
    finally:
        # Fechar a conexão
        conn.close()

if __name__ == "__main__":
    add_columns_to_tables()
