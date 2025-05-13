#run.py
from app import create_app, db
import logging
import os
from pathlib import Path
from flask import Flask
from flask_cors import CORS

# Configurar o logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Garantir que o diretório instance exista com o caminho absoluto correto
BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / 'instance'
INSTANCE_DIR.mkdir(exist_ok=True)
logger.info(f"Diretório instance: {INSTANCE_DIR}")

# Verificar permissões
if not os.access(INSTANCE_DIR, os.W_OK):
    logger.error(f"Sem permissão de escrita no diretório: {INSTANCE_DIR}")
    # Tentar corrigir as permissões
    try:
        os.chmod(INSTANCE_DIR, 0o755)
        logger.info(f"Permissões atualizadas para o diretório: {INSTANCE_DIR}")
    except Exception as e:
        logger.error(f"Não foi possível atualizar as permissões: {str(e)}")

# Função para remover o banco de dados existente
def reset_db():
    """Remove o banco de dados existente para recriá-lo do zero"""
    try:
        db_path = os.path.join(INSTANCE_DIR, 'dbVivapet.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            logger.info(f"Banco de dados removido: {db_path}")
            return True
    except Exception as e:
        logger.error(f"Erro ao remover banco de dados: {str(e)}")
    return False

# Criar a aplicação
app = create_app()

# Configurar o CORS
CORS(app, resources={r"/*": {"origins": "*"}})  # Permite CORS para todas as rotas

# Função para inicializar o banco de dados
def init_db():
    """Cria o banco de dados e tabelas e insere dados iniciais"""
    logger.info(f"Diretório de trabalho atual: {os.getcwd()}")
    
    # Verificar o URI do banco de dados configurado
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    logger.info(f"URI do banco de dados: {db_uri}")
    
    with app.app_context():
        try:
            # Cria todas as tabelas definidas nos modelos
            db.create_all()
            logger.info("Banco de dados e tabelas criados com sucesso")
            
            # Opcional: Inserir dados iniciais
            from app.models.servico import Servico
            if Servico.query.count() == 0:
                # Inserir serviços iniciais
                servicos_iniciais = [
                    Servico(
                        nome_servico='Cãominhada (30 min)', 
                        descricao='Passeio de 30 minutos próximo a residência do tutor(a)', 
                        valor_hora=30.00, 
                        valor_dia=None,
                        ativo=True
                    ),
                    Servico(
                        nome_servico='Creche', 
                        descricao='Período de 8 horas', 
                        valor_hora=None, 
                        valor_dia=70.00,
                        ativo=True
                    ),
                    Servico(
                        nome_servico='Hospedagem', 
                        descricao='Diária com alimentação inclusa', 
                        valor_hora=None, 
                        valor_dia=90.00,
                        ativo=True
                    )
                ]
                
                for servico in servicos_iniciais:
                    db.session.add(servico)
                
                db.session.commit()
                logger.info("Serviços iniciais cadastrados com sucesso")
            
            # Verificar se as tabelas foram criadas corretamente
            engine = db.engine
            inspector = db.inspect(engine)
            tables = inspector.get_table_names()
            logger.info(f"Tabelas criadas: {', '.join(tables)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar banco de dados: {str(e)}")
            # Se houver problemas no mapeamento dos modelos, fornecer orientações
            if "mapper" in str(e).lower() or "relationship" in str(e).lower():
                logger.error("Detectado erro de mapeamento entre os modelos.")
                logger.error("Verifique se todos os relacionamentos estão definidos corretamente.")
                logger.error("Tentando reiniciar o banco de dados...")
                
                # Se o banco de dados já existe, tenta remover e criar novamente
                db_path = os.path.join(INSTANCE_DIR, 'dbVivapet.db')
                if db_path and os.path.exists(db_path):
                    try:
                        os.remove(db_path)
                        logger.info(f"Banco de dados removido: {db_path}")
                        # Tentar criar novamente
                        db.create_all()
                        logger.info("Banco de dados recriado com sucesso após remoção")
                        return True
                    except Exception as ex:
                        logger.error(f"Falha ao recriar banco de dados: {str(ex)}")
            
            return False

if __name__ == '__main__':
    logger.info("Inicializando o banco de dados...")
    
    # Evita recriar o banco de dados em reinicializações do modo debug
    import sys
    db_path = os.path.join(INSTANCE_DIR, 'dbVivapet.db')
    if not os.path.exists(db_path) or '--force-init-db' in sys.argv:
        reset_db()
        success = init_db()
    else:
        logger.info("Usando banco de dados existente")
        success = True
    
    if success:
        logger.info("Iniciando o servidor Flask VivaPet...")
        logger.info("O servidor estará disponível em http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        logger.error("Não foi possível inicializar o banco de dados. Verifique os erros acima.")