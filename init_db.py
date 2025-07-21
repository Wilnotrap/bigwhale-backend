import os
import sys
import time
import logging
from app import create_app
from database import db
from models.user import User
from models.active_signal import ActiveSignal

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wait_for_db(app, max_retries=5, retry_interval=5):
    retries = 0
    
    while retries < max_retries:
        try:
            with app.app_context():
                db.engine.connect()
                logger.info("Conexão com o banco de dados estabelecida com sucesso")
                return True
        except Exception as e:
            retries += 1
            logger.warning(f"Tentativa {retries}/{max_retries} falhou: {e}")
            
            if retries < max_retries:
                logger.info(f"Tentando novamente em {retry_interval} segundos...")
                time.sleep(retry_interval)
            else:
                logger.error(f"Não foi possível conectar ao banco de dados após {max_retries} tentativas")
                return False

def init_database():
    app = create_app()
    
    if not wait_for_db(app):
        logger.error("Falha ao conectar ao banco de dados")
        return False
    
    with app.app_context():
        try:
            logger.info("Criando tabelas do banco de dados...")
            db.create_all()
            logger.info("Tabelas criadas com sucesso!")
            
            demo_user = User.query.filter_by(email='financeiro@lexxusadm.com.br').first()
            
            if demo_user:
                logger.info(f"Usuário demo já existe: {demo_user.full_name}")
                if demo_user.operational_balance_usd != 600.0:
                    demo_user.operational_balance_usd = 600.0
                    db.session.commit()
                    logger.info("Saldo atualizado para: $600.00")
            else:
                demo_user = User(
                    email='financeiro@lexxusadm.com.br',
                    full_name='Conta Demo Financeiro',
                    is_admin=False,
                    is_active=True,
                    operational_balance_usd=600.0
                )
                
                demo_user.set_password('FinanceiroDemo2025@')
                
                db.session.add(demo_user)
                db.session.commit()
                
                logger.info("Usuário demo criado com sucesso:")
                logger.info("Email: financeiro@lexxusadm.com.br")
                logger.info("Saldo: $600.00")
            
            signals_count = ActiveSignal.query.count()
            logger.info(f"Total de sinais ativos: {signals_count}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = init_database()
    
    if success:
        logger.info("✅ Banco de dados inicializado com sucesso!")
    else:
        logger.error("❌ Erro ao inicializar banco de dados!")
        sys.exit(1)