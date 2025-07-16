from flask import Blueprint, request, jsonify
from functools import wraps
# Importa o User do arquivo de modelo padrão
from models.user import User
from models.trade import Trade
from database import db
from datetime import datetime
from sqlalchemy import func, desc, case
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin_clean', __name__)

def admin_required(f):
    @wraps(f) 
    def decorated_function(*args, **kwargs):
        from flask import session
        if 'user_id' not in session:
            return jsonify({'message': 'Acesso negado'}), 403
            
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return jsonify({'message': 'Acesso de administrador necessário'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        users_query = User.query.filter_by(is_active=True)
        
        pagination = users_query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users_data = []
        for user in pagination.items:
            user_stats = Trade.get_user_stats(user.id)
            open_trades_count = Trade.query.filter_by(user_id=user.id, status='open').count()
            
            users_data.append({
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'is_active': user.is_active,
                'is_admin': user.is_admin,
                'operational_balance': user.operational_balance or 0,
                'operational_balance_usd': user.operational_balance_usd or 0,
                'nautilus_active': user.nautilus_active,
                'stats': {
                    'total_trades': user_stats.get('total_trades', 0),
                    'winning_trades': user_stats.get('winning_trades', 0),
                    'total_pnl': user_stats.get('total_pnl', 0),
                    'avg_roe': user_stats.get('avg_roe', 0),
                    'live_roe_display': f"{user_stats.get('sum_open_roe_percentage', 0):.2f}%", 
                    'total_operations': f"({user_stats.get('total_trades', 0)} encerradas | {open_trades_count} abertas)"
                }
            })
        
        summary = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'inactive_users': User.query.filter_by(is_active=False).count(),
            'admin_users': User.query.filter_by(is_admin=True).count()
        }
        
        return jsonify({
            'users': users_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            },
            'summary': summary
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter usuários: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@admin_bp.route('/dashboard/stats', methods=['GET'])
@admin_required
def get_admin_dashboard_stats():
    """Obter estatísticas gerais do dashboard admin de forma otimizada."""
    try:
        # 1. Calcular total de ativos sob gestão (soma dos saldos de futuros de todos os usuários)
        total_under_management = db.session.query(
            func.sum(User.operational_balance_usd)
        ).scalar() or 0
        
        # 2. Calcular posições abertas: contagem e ROE total (usando o banco como fonte de verdade)
        open_trades = Trade.query.filter_by(status='open').all()
        
        positive_count = 0
        negative_count = 0
        total_roe_percentage = 0
        
        # Instanciar o cliente da API fora do loop para reutilização
        bitget_client = None 
        try:
            from api.bitget_client import BitgetAPI
            # Não precisamos de chaves para buscar preços públicos
            bitget_client = BitgetAPI(api_key="", secret_key="", passphrase="")
        except Exception as e:
            logger.error(f"Não foi possível instanciar o BitgetAPI client: {e}")

        for trade in open_trades:
            current_roe = 0
            if bitget_client:
                try:
                    # O método 'calculate_current_roe' buscará o preço de mercado e retornará o ROE
                    current_roe = trade.calculate_current_roe(bitget_client)
                except Exception as e:
                    logger.error(f"Erro ao calcular ROE para o trade {trade.id}: {e}")
                    # Usa o ROE do banco como fallback
                    current_roe = trade.roe if trade.roe is not None else 0
            else:
                # Usa o ROE do banco como fallback se o cliente não puder ser instanciado
                current_roe = trade.roe if trade.roe is not None else 0

            total_roe_percentage += current_roe
            
            if current_roe >= 0:
                positive_count += 1
            else:
                negative_count += 1

        # 3. Contar usuários e administradores
        total_users = db.session.query(func.count(User.id)).scalar()
        active_users = db.session.query(func.count(User.id)).filter_by(is_active=True).scalar()
        admin_users = db.session.query(func.count(User.id)).filter_by(is_admin=True).scalar()
        
        return jsonify({
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users,
            'total_under_management_usd': round(total_under_management, 2),
            'open_positions': {
                'positive_count': positive_count,
                'negative_count': negative_count,
                'total_roe_percentage': round(total_roe_percentage, 2)
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do dashboard admin: {e}")
        return jsonify({
            'error': 'Erro interno do servidor',
            'message': str(e)
        }), 500

@admin_bp.route('/user/<int:user_id>/dashboard', methods=['GET'])
@admin_required  
def get_user_dashboard_view(user_id):
    """Obter visão do dashboard de um usuário, usando o DB como fonte de verdade."""
    try:
        user = User.query.get_or_404(user_id)
        
        # Obter estatísticas gerais do usuário a partir do banco de dados
        stats = Trade.get_user_stats(user_id)
        
        # Obter posições abertas do banco de dados
        open_trades = Trade.query.filter_by(user_id=user_id, status='open').all()
        open_positions_data = []

        # Instanciar o Bitget client para buscar preços atuais
        bitget_client = None
        try:
            from api.bitget_client import BitgetAPI
            bitget_client = BitgetAPI(api_key="", secret_key="", passphrase="")
        except Exception as e:
            logger.error(f"Não foi possível instanciar o BitgetAPI client para ROE: {e}")

        for trade in open_trades:
            current_roe = trade.roe or 0
            if bitget_client:
                try:
                    # Calcula o ROE em tempo real
                    current_roe = trade.calculate_current_roe(bitget_client)
                except Exception as e:
                    logger.error(f"Erro ao calcular ROE em tempo real para trade {trade.id}: {e}")
            
            open_positions_data.append({
                'id': trade.id, # Adicionado o ID do trade para o botão de fechar
                'symbol': trade.symbol,
                'side': trade.side,
                'size': trade.size,
                'entry_price': trade.entry_price,
                'leverage': trade.leverage,
                'pnl': trade.pnl, # Note: PNL do DB pode não estar em tempo real
                'roe_percentage': current_roe, # ROE em tempo real
                'opened_at': trade.opened_at.isoformat() if trade.opened_at else None,
            })
            
        # Buscar trades fechados do banco de dados
        closed_trades = Trade.query.filter_by(
            user_id=user_id, 
            status='closed'
        ).order_by(Trade.closed_at.desc()).limit(20).all()
        
        closed_trades_data = [t.to_dict() for t in closed_trades]
        
        return jsonify({
            'user_info': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email
            },
            'stats': stats,
            'open_positions': open_positions_data,
            'closed_trades': closed_trades_data,
            'operational_balance_usd': user.operational_balance_usd or 0
        }), 200

    except Exception as e:
        logger.error(f"Erro ao obter visão do dashboard do usuário {user_id}: {e}")
        return jsonify({'error': 'Erro interno do servidor', 'message': str(e)}), 500

@admin_bp.route('/trades/<int:trade_id>/close', methods=['POST'])
@admin_required
def close_trade(trade_id):
    """Fecha uma operação de um usuário específico."""
    trade = Trade.query.get_or_404(trade_id)
    if trade.status != 'open':
        return jsonify({'message': 'Este trade não está aberto.'}), 400
        
    user = User.query.get(trade.user_id)
    if not user:
        return jsonify({'message': 'Usuário do trade não encontrado.'}), 404

    try:
        from utils.security import decrypt_api_key
        from api.bitget_client import BitgetAPI

        api_key = decrypt_api_key(user.bitget_api_key_encrypted)
        api_secret = decrypt_api_key(user.bitget_api_secret_encrypted)
        passphrase = decrypt_api_key(user.bitget_passphrase_encrypted)

        if not (api_key and api_secret and passphrase):
            return jsonify({'message': 'Credenciais de API inválidas para o usuário.'}), 400
            
        bitget_client = BitgetAPI(api_key=api_key, secret_key=api_secret, passphrase=passphrase)
        
        # Lógica para fechar a posição na Bitget
        # A API da Bitget exige o lado oposto para fechar a mercado
        close_side = 'buy' if trade.side == 'short' else 'sell'
        
        response = bitget_client.place_order(
            symbol=trade.symbol,
            margin_coin='USDT',
            size=str(trade.size),
            side=close_side,
            order_type='market',
            trade_side='close' # Indica que é uma ordem de fechamento
        )
        
        if response and response.get('code') == '00000':
            # A ordem de fechamento foi enviada. A sincronização vai atualizar o status.
            logger.info(f"Ordem de fechamento para o trade {trade.id} enviada com sucesso. ID da Ordem: {response['data'].get('orderId')}")
            
            # O ideal é não mudar o status aqui, mas esperar o sync service confirmar.
            # No entanto, para uma resposta mais rápida na UI, podemos ser otimistas.
            # O sync vai corrigir se algo der errado.
            trade.status = 'closing' # Um estado intermediário
            db.session.commit()
            
            return jsonify({'message': 'Ordem de fechamento enviada com sucesso!'}), 200
        else:
            error_msg = response.get('msg', 'Erro desconhecido da API') if response else "Sem resposta da API"
            logger.error(f"Falha ao enviar ordem de fechamento para o trade {trade.id}. Resposta da API: {error_msg}")
            return jsonify({'message': f'Falha ao fechar a operação: {error_msg}'}), 500
            
    except Exception as e:
        logger.error(f"Exceção ao tentar fechar o trade {trade_id}: {e}", exc_info=True)
        return jsonify({'message': 'Erro interno do servidor ao fechar a operação.'}), 500

@admin_bp.route('/user/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Ativar/desativar status do usuário no Nautilus"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Alternar status Nautilus
        user.nautilus_active = not user.nautilus_active
        db.session.commit()
        
        status_text = "ativo" if user.nautilus_active else "inativo"
        
        return jsonify({
            'message': f'Status Nautilus do usuário {user.full_name} alterado para {status_text}',
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'is_active': user.is_active,
                'nautilus_active': user.nautilus_active
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao alterar status Nautilus: {str(e)}")
        return jsonify({'message': f'Erro ao alterar status Nautilus: {str(e)}'}), 500

@admin_bp.route('/sync-nautilus-status', methods=['POST'])
@admin_required
def sync_nautilus_status():
    """Sincronizar status Nautilus de todos os usuários manualmente"""
    try:
        from services.sync_service import sync_nautilus_status_for_all_users
        
        # Executar sincronização
        sync_nautilus_status_for_all_users()
        
        # Obter contagem atualizada
        users_active = User.query.filter_by(nautilus_active=True).count()
        users_total = User.query.count()
        
        return jsonify({
            'message': 'Sincronização do status Nautilus concluída com sucesso',
            'stats': {
                'users_nautilus_active': users_active,
                'users_total': users_total,
                'sync_timestamp': datetime.now().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na sincronização manual do Nautilus: {str(e)}")
        return jsonify({
            'message': f'Erro na sincronização: {str(e)}'
        }), 500

@admin_bp.route('/user/<int:user_id>/trades', methods=['GET'])
@admin_required
def get_user_trades(user_id):
    """Obter histórico completo de trades de um usuário específico"""
    try:
        user = User.query.get_or_404(user_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status', 'all')  # all, open, closed
        symbol_filter = request.args.get('symbol', '')
        
        # Construir query base
        query = Trade.query.filter_by(user_id=user_id)
        
        # Aplicar filtros
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)
        
        if symbol_filter:
            query = query.filter(Trade.symbol.ilike(f'%{symbol_filter}%'))
        
        # Ordenar por data de abertura (mais recentes primeiro)
        query = query.order_by(Trade.opened_at.desc())
        
        # Paginar
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        trades_data = []
        for trade in pagination.items:
            trade_dict = trade.to_dict()
            # Adicionar informações extras
            trade_dict['duration'] = None
            if trade.opened_at and trade.closed_at:
                duration = trade.closed_at - trade.opened_at
                trade_dict['duration'] = str(duration)
            
            trades_data.append(trade_dict)
        
        return jsonify({
            'user_info': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email
            },
            'trades': trades_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter trades do usuário {user_id}: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@admin_bp.route('/trades/overview', methods=['GET'])
@admin_required
def get_trades_overview():
    """Obter visão geral de todas as operações do sistema"""
    try:
        # Estatísticas gerais
        total_trades = Trade.query.count()
        open_trades = Trade.query.filter_by(status='open').count()
        closed_trades = Trade.query.filter_by(status='closed').count()
        
        # PNL total realizado
        total_realized_pnl = db.session.query(
            func.sum(Trade.pnl)
        ).filter_by(status='closed').scalar() or 0
        
        # Trades vencedores
        winning_trades = Trade.query.filter(
            Trade.status == 'closed',
            Trade.pnl > 0
        ).count()
        
        # Taxa de vitória geral
        win_rate = (winning_trades / closed_trades * 100) if closed_trades > 0 else 0
        
        # Top símbolos mais negociados
        top_symbols = db.session.query(
            Trade.symbol,
            func.count(Trade.id).label('count'),
            func.sum(Trade.pnl).label('total_pnl')
        ).filter_by(status='closed').group_by(Trade.symbol).order_by(
            func.count(Trade.id).desc()
        ).limit(10).all()
        
        top_symbols_data = [{
            'symbol': symbol,
            'trade_count': count,
            'total_pnl': float(total_pnl) if total_pnl else 0
        } for symbol, count, total_pnl in top_symbols]
        
        # Usuários mais ativos
        top_users = db.session.query(
            User.id,
            User.full_name,
            func.count(Trade.id).label('trade_count'),
            func.sum(Trade.pnl).label('total_pnl')
        ).join(Trade).filter(
            Trade.status == 'closed'
        ).group_by(User.id, User.full_name).order_by(
            func.count(Trade.id).desc()
        ).limit(10).all()
        
        top_users_data = [{
            'user_id': user_id,
            'full_name': full_name,
            'trade_count': trade_count,
            'total_pnl': float(total_pnl) if total_pnl else 0
        } for user_id, full_name, trade_count, total_pnl in top_users]
        
        return jsonify({
            'overview': {
                'total_trades': total_trades,
                'open_trades': open_trades,
                'closed_trades': closed_trades,
                'total_realized_pnl': round(total_realized_pnl, 2),
                'winning_trades': winning_trades,
                'win_rate': round(win_rate, 2)
            },
            'top_symbols': top_symbols_data,
            'top_users': top_users_data
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter visão geral de trades: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@admin_bp.route('/user/<int:user_id>/stats/detailed', methods=['GET'])
@admin_required
def get_user_detailed_stats(user_id):
    """Obter estatísticas detalhadas de um usuário específico"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Estatísticas básicas
        basic_stats = Trade.get_user_stats(user_id)
        
        # Estatísticas por símbolo
        symbol_stats = db.session.query(
            Trade.symbol,
            func.count(Trade.id).label('count'),
            func.sum(Trade.pnl).label('total_pnl'),
            func.avg(Trade.roe).label('avg_roe'),
            func.sum(case((Trade.pnl > 0, 1), else_=0)).label('wins')
        ).filter(
            Trade.user_id == user_id,
            Trade.status == 'closed'
        ).group_by(Trade.symbol).all()
        
        symbol_stats_data = []
        for symbol, count, total_pnl, avg_roe, wins in symbol_stats:
            win_rate = (wins / count * 100) if count > 0 else 0
            symbol_stats_data.append({
                'symbol': symbol,
                'trade_count': count,
                'total_pnl': float(total_pnl) if total_pnl else 0,
                'avg_roe': float(avg_roe) if avg_roe else 0,
                'wins': wins,
                'win_rate': round(win_rate, 2)
            })
        
        # Estatísticas por lado (long/short)
        side_stats = db.session.query(
            Trade.side,
            func.count(Trade.id).label('count'),
            func.sum(Trade.pnl).label('total_pnl'),
            func.avg(Trade.roe).label('avg_roe'),
            func.sum(case((Trade.pnl > 0, 1), else_=0)).label('wins')
        ).filter(
            Trade.user_id == user_id,
            Trade.status == 'closed'
        ).group_by(Trade.side).all()
        
        side_stats_data = []
        for side, count, total_pnl, avg_roe, wins in side_stats:
            win_rate = (wins / count * 100) if count > 0 else 0
            side_stats_data.append({
                'side': side,
                'trade_count': count,
                'total_pnl': float(total_pnl) if total_pnl else 0,
                'avg_roe': float(avg_roe) if avg_roe else 0,
                'wins': wins,
                'win_rate': round(win_rate, 2)
            })
        
        # Últimos 10 trades
        recent_trades = Trade.query.filter_by(
            user_id=user_id
        ).order_by(Trade.opened_at.desc()).limit(10).all()
        
        recent_trades_data = [trade.to_dict() for trade in recent_trades]
        
        return jsonify({
            'user_info': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'operational_balance_usd': user.operational_balance_usd or 0,
                'nautilus_active': user.nautilus_active
            },
            'basic_stats': basic_stats,
            'symbol_stats': symbol_stats_data,
            'side_stats': side_stats_data,
            'recent_trades': recent_trades_data
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas detalhadas do usuário {user_id}: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@admin_bp.route('/user/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    """Resetar senha de um usuário específico"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        new_password = data.get('new_password')
        if not new_password or len(new_password) < 6:
            return jsonify({'message': 'Nova senha deve ter pelo menos 6 caracteres'}), 400
        
        # Atualizar senha
        user.set_password(new_password)
        db.session.commit()
        
        logger.info(f"Admin resetou senha do usuário {user.full_name} (ID: {user_id})")
        
        return jsonify({
            'message': f'Senha do usuário {user.full_name} foi resetada com sucesso'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao resetar senha do usuário {user_id}: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@admin_bp.route('/user/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_user_admin_status(user_id):
    """Alternar status de administrador de um usuário"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Não permitir remover admin do próprio usuário logado
        from flask import session
        if user_id == session.get('user_id') and user.is_admin:
            return jsonify({'message': 'Você não pode remover seu próprio status de administrador'}), 400
        
        # Alternar status admin
        user.is_admin = not user.is_admin
        db.session.commit()
        
        status_text = "administrador" if user.is_admin else "usuário comum"
        
        logger.info(f"Status admin do usuário {user.full_name} alterado para {status_text}")
        
        return jsonify({
            'message': f'Usuário {user.full_name} agora é {status_text}',
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'is_admin': user.is_admin
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao alterar status admin do usuário {user_id}: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@admin_bp.route('/system/stats', methods=['GET'])
@admin_required
def get_system_stats():
    """Obter estatísticas gerais do sistema"""
    try:
        # Estatísticas de usuários
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(is_admin=True).count()
        nautilus_active_users = User.query.filter_by(nautilus_active=True).count()
        
        # Estatísticas de trades
        total_trades = Trade.query.count()
        open_trades = Trade.query.filter_by(status='open').count()
        closed_trades = Trade.query.filter_by(status='closed').count()
        
        # PNL total do sistema
        total_realized_pnl = db.session.query(
            func.sum(Trade.pnl)
        ).filter_by(status='closed').scalar() or 0
        
        # Saldo total sob gestão
        total_under_management = db.session.query(
            func.sum(User.operational_balance_usd)
        ).scalar() or 0
        
        # Trades por dia (últimos 30 dias)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        daily_trades = db.session.query(
            func.date(Trade.opened_at).label('date'),
            func.count(Trade.id).label('count')
        ).filter(
            Trade.opened_at >= thirty_days_ago
        ).group_by(func.date(Trade.opened_at)).order_by(
            func.date(Trade.opened_at)
        ).all()
        
        daily_trades_data = [{
            'date': date.isoformat() if date else None,
            'count': count
        } for date, count in daily_trades]
        
        return jsonify({
            'users': {
                'total': total_users,
                'active': active_users,
                'admin': admin_users,
                'nautilus_active': nautilus_active_users
            },
            'trades': {
                'total': total_trades,
                'open': open_trades,
                'closed': closed_trades
            },
            'financial': {
                'total_realized_pnl': round(total_realized_pnl, 2),
                'total_under_management': round(total_under_management, 2)
            },
            'daily_trades': daily_trades_data
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do sistema: {str(e)}")
        return jsonify({'message': 'Erro interno do servidor'}), 500

@admin_bp.route('/user/<int:user_id>/sync-nautilus', methods=['POST'])
@admin_required  
def sync_user_nautilus_status(user_id):
    """Sincronizar status Nautilus de um usuário específico"""
    try:
        from services.sync_service import sync_nautilus_status_for_user
        
        user = User.query.get_or_404(user_id)
        
        # Executar sincronização para usuário específico
        updated = sync_nautilus_status_for_user(user_id)
        
        # Recarregar usuário para obter dados atualizados
        user = User.query.get(user_id)
        
        return jsonify({
            'message': 'Sincronização individual concluída com sucesso' if updated else 'Usuário já estava com status correto',
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'nautilus_active': user.nautilus_active,
                'has_api_credentials': bool(user.bitget_api_key_encrypted and user.bitget_api_secret_encrypted)
            },
            'updated': updated
        }), 200
        
    except Exception as e:
        logger.error(f"Erro na sincronização individual do Nautilus: {str(e)}")
        return jsonify({
            'message': f'Erro na sincronização: {str(e)}'
        }), 500