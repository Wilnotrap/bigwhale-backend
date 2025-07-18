# backend/api/dashboard.py
from flask import Blueprint, request, jsonify, session
from models.user import User
from models.trade import Trade
from database import db
from utils.security import decrypt_api_key
from api.bitget_client import BitgetAPI
from services.secure_api_service_corrigido import SecureAPIService # Importar SecureAPIService
from datetime import datetime
import json
import logging
from flask_cors import cross_origin
import requests

# Configurar logging básico
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

dashboard_bp = Blueprint('dashboard', __name__)

def require_login(f):
    """Decorator para verificar se o usuário está logado"""
    def decorated_function(*args, **kwargs):
        logging.info(f"Verificando login para a rota: {f.__name__}")
        if 'user_id' not in session:
            logging.warning(f"Acesso não autorizado à rota {f.__name__} - user_id não encontrado na sessão.")
            return jsonify({'message': 'Login necessário'}), 401
        
        # Renovar sessão automaticamente para evitar expiração
        session.permanent = True
        
        logging.info(f"Usuário {session['user_id']} acessando rota {f.__name__}")
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@dashboard_bp.route('/stats', methods=['GET'])
@require_login
def get_user_stats():
    """Retorna estatísticas do usuário, incluindo PnL realizado e não realizado, buscando diretamente da Bitget."""
    logging.info(f"Rota /stats chamada pelo usuário {session.get('user_id')}")
    try:
        user_id = session['user_id']
        logging.info(f"[DEBUG] Iniciando get_user_stats para usuário {user_id}")
        
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        logging.info(f"[DEBUG] Filtros de data recebidos - Start: {start_date}, End: {end_date}")
        
        # Inicializa um dicionário de estatísticas zerado. Fonte de dados será a Bitget.
        stats = {
            'realized_pnl': 0,
            'unrealized_pnl': 0,
            'margin_size': 0,
            'open_positions_count': 0,
            'total_pnl': 0,
            'win_rate': 0,
            'total_trades': 0,
            'winning_trades': 0,
        }
        
        try:
            user = User.query.get(user_id)
            if user and user.bitget_api_key_encrypted and user.bitget_api_secret_encrypted:
                api_key = decrypt_api_key(user.bitget_api_key_encrypted)
                api_secret = decrypt_api_key(user.bitget_api_secret_encrypted)
                passphrase = decrypt_api_key(user.bitget_passphrase_encrypted) if user.bitget_passphrase_encrypted else None
                
                if api_key and api_secret:
                    bitget_client = BitgetAPI(api_key=api_key, secret_key=api_secret, passphrase=passphrase)
                    
                    # 1. CALCULAR PNL DE POSIÇÕES ABERTAS (NÃO REALIZADO)
                    try:
                        open_positions_response = bitget_client.get_all_positions_info('umcbl', 'USDT')
                        if open_positions_response and open_positions_response.get('code') == '00000':
                            open_positions_data = open_positions_response.get('data', [])
                            if isinstance(open_positions_data, list):
                                stats['open_positions_count'] = len(open_positions_data)
                                for pos in open_positions_data:
                                    stats['unrealized_pnl'] += float(pos.get('unrealizedPnl', 0))
                                    stats['margin_size'] += float(pos.get('margin', 0))
                                logging.info(f"[DEBUG] PnL não realizado (aberto): {stats['unrealized_pnl']}, Margem total: {stats['margin_size']}")
                        else:
                            logging.warning(f"Não foi possível obter posições abertas: {open_positions_response.get('msg')}")
                    except Exception as e:
                        logging.error(f"[ERROR] Erro ao buscar posições abertas da Bitget: {str(e)}")

                    # 2. CALCULAR PNL DE POSIÇÕES FECHADAS (REALIZADO) COM FILTRO DE DATA
                    history_response = bitget_client.get_closed_positions_history(limit=100)
                    if history_response and history_response.get('code') == '00000':
                        data_section = history_response.get('data', {})
                        positions_data = data_section.get('list', []) if isinstance(data_section, dict) else []
                        
                        from datetime import datetime
                        # Aplicar filtro do mês atual apenas quando não há filtros de data especificados
                        use_current_month_filter = not start_date and not end_date
                        
                        start_datetime = None
                        if start_date:
                            try:
                                start_datetime = datetime.strptime(start_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
                            except ValueError:
                                logging.error(f"Formato de data inválido para start_date: {start_date}")

                        end_datetime = None
                        if end_date:
                            try:
                                end_datetime = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
                            except ValueError:
                                logging.error(f"Formato de data inválido para end_date: {end_date}")

                        current_month = datetime.now().month
                        current_year = datetime.now().year

                        closed_trades_count = 0
                        winning_trades_bitget = 0
                        realized_pnl_from_bitget = 0

                        for position in positions_data:
                            utime = position.get('utime')
                            if utime:
                                try:
                                    position_date = datetime.fromtimestamp(int(utime) / 1000)
                                    should_include = False
                                    
                                    if use_current_month_filter:
                                        # Filtro automático para o mês atual quando não há filtros especificados
                                        if position_date.month == current_month and position_date.year == current_year:
                                            should_include = True
                                    else:
                                        # Aplicar filtros de data especificados pelo usuário
                                        if start_datetime and end_datetime:
                                            should_include = start_datetime <= position_date <= end_datetime
                                        elif start_datetime:
                                            should_include = position_date >= start_datetime
                                        elif end_datetime:
                                            should_include = position_date <= end_datetime
                                        else:
                                            should_include = True
                                    
                                    if should_include:
                                        pnl = float(position.get('pnl', 0))
                                        realized_pnl_from_bitget += pnl
                                        closed_trades_count += 1
                                        if pnl > 0:
                                            winning_trades_bitget += 1
                                            
                                        logging.debug(f"[DEBUG] Posição incluída - Data: {position_date}, PnL: {pnl}")
                                except (ValueError, TypeError, OSError):
                                    continue
                        
                        stats['realized_pnl'] = realized_pnl_from_bitget
                        if closed_trades_count > 0:
                            stats['win_rate'] = (winning_trades_bitget / closed_trades_count) * 100
                            stats['total_trades'] = closed_trades_count
                            stats['winning_trades'] = winning_trades_bitget
                        
                        logging.info(f"[DEBUG] PnL Realizado calculado: {realized_pnl_from_bitget} (de {closed_trades_count} trades, filtro mês atual: {use_current_month_filter})")

        except Exception as e:
            logging.error(f"[ERROR] Erro geral ao calcular estatísticas da Bitget: {str(e)}")
        
        # ATUALIZAR PNL TOTAL
        stats['total_pnl'] = stats['realized_pnl'] + stats['unrealized_pnl']
        
        logging.info(f"Estatísticas FINAIS para usuário {user_id}: {stats}")
        return jsonify({'success': True, 'data': stats}), 200
        
    except Exception as e:
        logging.error(f"[ERROR] Erro fatal ao obter estatísticas para usuário {session.get('user_id')}: {str(e)}", exc_info=True)
        return jsonify({'message': 'Erro ao carregar estatísticas'}), 500

@dashboard_bp.route('/trades/open', methods=['GET'])
@require_login
def get_open_trades():
    """Retorna trades abertos do usuário"""
    logging.info(f"Rota /trades/open chamada pelo usuário {session.get('user_id')}")
    try:
        user_id = session['user_id']
        open_trades = Trade.query.filter_by(user_id=user_id, status='open').all()
        
        trades_data = [trade.to_dict() for trade in open_trades]
        logging.info(f"Trades abertos para usuário {user_id}: {len(trades_data)} trades encontrados.")
        return jsonify({
            'success': True,
            'data': trades_data
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter trades abertos para usuário {session.get('user_id')}: {e}", exc_info=True)
        return jsonify({'message': 'Erro ao carregar trades abertos'}), 500

@dashboard_bp.route('/profit-curve', methods=['GET'])
@require_login
def get_profit_curve():
    """Retorna dados para o gráfico de curva de lucro"""
    logging.info(f"Rota /profit-curve chamada pelo usuário {session.get('user_id')}")
    try:
        user_id = session['user_id']
        
        closed_trades = Trade.query.filter_by(
            user_id=user_id, 
            status='closed'
        ).order_by(Trade.closed_at.asc()).all()
        
        if not closed_trades:
            logging.info(f"Nenhum trade fechado encontrado para usuário {user_id} para a curva de lucro.")
            return jsonify({
                'success': True,
                'data': []
            }), 200
        
        cumulative_pnl = 0
        profit_curve = []
        
        for trade in closed_trades:
            # Converter pnl para float se for string
            trade_pnl = trade.pnl or 0
            if isinstance(trade_pnl, str):
                try:
                    trade_pnl = float(trade_pnl)
                except (ValueError, TypeError):
                    trade_pnl = 0
            
            cumulative_pnl += trade_pnl
            profit_curve.append({
                'date': trade.closed_at.isoformat(),
                'cumulative_pnl': cumulative_pnl,
                'trade_pnl': trade_pnl,
                'symbol': trade.symbol
            })
        logging.info(f"Curva de lucro gerada para usuário {user_id} com {len(profit_curve)} pontos.")
        return jsonify({
            'success': True,
            'data': profit_curve
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao gerar curva de lucro para usuário {session.get('user_id')}: {e}", exc_info=True)
        return jsonify({'message': 'Erro ao gerar curva de lucro'}), 500

@dashboard_bp.route('/trades/closed', methods=['GET'])
@require_login
def get_closed_trades():
    """Retorna trades fechados do usuário do banco de dados local"""
    logging.info(f"Rota /trades/closed chamada pelo usuário {session.get('user_id')}")
    try:
        user_id = session['user_id']
        closed_trades = Trade.query.filter_by(user_id=user_id, status='closed').order_by(Trade.closed_at.desc()).all()
        
        trades_data = [trade.to_dict() for trade in closed_trades]
        logging.info(f"Trades fechados para usuário {user_id}: {len(trades_data)} trades encontrados.")
        return jsonify({
            'success': True,
            'data': trades_data
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter trades fechados para usuário {session.get('user_id')}: {e}", exc_info=True)
        return jsonify({'message': 'Erro ao carregar trades fechados'}), 500

@dashboard_bp.route('/sync-trades', methods=['POST', 'OPTIONS'])
@require_login
def sync_trades():
    if request.method == 'OPTIONS':
        return '', 200
    """Sincroniza trades do usuário com a Bitget - Versão melhorada"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            logging.error("Tentativa de sincronização sem user_id na sessão")
            return jsonify({'error': 'Usuário não autenticado'}), 401

        user = User.query.get(user_id)
        if not user:
            logging.error(f"Usuário {user_id} não encontrado no banco de dados")
            return jsonify({'error': 'Usuário não encontrado'}), 404

        # Verificar se as credenciais existem
        if not all([user.bitget_api_key_encrypted, user.bitget_api_secret_encrypted, user.bitget_passphrase_encrypted]):
            logging.warning(f"Credenciais da API não configuradas para usuário {user_id}")
            return jsonify({'error': 'Credenciais da API não configuradas. Configure suas credenciais no perfil.'}), 400

        # Descriptografar credenciais com tratamento de erro
        try:
            api_key = decrypt_api_key(user.bitget_api_key_encrypted)
            api_secret = decrypt_api_key(user.bitget_api_secret_encrypted)
            passphrase = decrypt_api_key(user.bitget_passphrase_encrypted)
        except Exception as e:
            logging.error(f"Erro ao descriptografar credenciais para usuário {user_id}: {e}")
            return jsonify({'error': 'Erro ao acessar credenciais da API. Reconfigure suas credenciais.'}), 500

        if not all([api_key, api_secret, passphrase]):
            logging.error(f"Credenciais descriptografadas inválidas para usuário {user_id}")
            return jsonify({'error': 'Credenciais da API corrompidas. Reconfigure suas credenciais.'}), 400

        # Criar cliente Bitget com tratamento de erro robusto
        try:
            bitget_client = BitgetAPI(api_key=api_key, secret_key=api_secret, passphrase=passphrase)
        except Exception as e:
            logging.error(f"Erro ao criar cliente Bitget para usuário {user_id}: {e}")
            return jsonify({'error': 'Erro ao conectar com a API da Bitget'}), 500

        # Validar credenciais antes de prosseguir
        try:
            if not bitget_client.validate_credentials():
                logging.error(f"Credenciais da API inválidas para usuário {user_id}")
                return jsonify({'error': 'Credenciais da API inválidas. Verifique suas configurações.'}), 400
        except Exception as e:
            logging.error(f"Erro ao validar credenciais para usuário {user_id}: {e}")
            return jsonify({'error': 'Erro ao validar credenciais da API'}), 500

        # Buscar posições abertas com tratamento de erro robusto
        try:
            positions_response = bitget_client.get_all_positions()
            if not positions_response:
                logging.error(f"Resposta vazia da API para usuário {user_id}")
                return jsonify({'error': 'Erro de comunicação com a API da Bitget'}), 500
                
            if positions_response.get('code') != '00000':
                error_msg = positions_response.get('msg', 'Erro desconhecido')
                logging.error(f"Erro da API Bitget para usuário {user_id}: {error_msg}")
                return jsonify({'error': f'Erro da API Bitget: {error_msg}'}), 500
                
        except Exception as e:
            logging.error(f"Exceção ao buscar posições para usuário {user_id}: {e}")
            return jsonify({'error': 'Erro ao buscar posições na Bitget'}), 500

        positions_data = positions_response.get('data', [])
        new_trades = 0
        updated_trades = 0
        closed_trades = 0

        # Processar posições com tratamento de erro individual
        current_open_positions = set()
        
        for position in positions_data:
            try:
                # Verificar se a posição tem tamanho válido
                total_size = float(position.get('total', 0))
                if total_size == 0:
                    continue

                symbol = position.get('symbol')
                side = 'long' if position.get('holdSide') == 'long' else 'short'
                size = abs(total_size)
                entry_price = float(position.get('openPriceAvg', 0))
                unrealized_pnl = float(position.get('unrealizedPL', 0))
                leverage = float(position.get('leverage', 1.0))
                margin_used = float(position.get('margin', 0)) or float(position.get('marginSize', 0))

                current_open_positions.add((symbol, side))

                # Atualizar ou criar trade
                existing_trade = Trade.query.filter_by(
                    user_id=user_id,
                    symbol=symbol,
                    side=side,
                    status='open'
                ).first()

                if existing_trade:
                    existing_trade.size = str(size)
                    existing_trade.entry_price = str(entry_price)
                    existing_trade.pnl = unrealized_pnl
                    existing_trade.leverage = leverage
                    existing_trade.margin = margin_used
                    if existing_trade.fees is None:
                        existing_trade.fees = 0.0
                    updated_trades += 1
                else:
                    new_trade = Trade(
                        user_id=user_id,
                        symbol=symbol,
                        side=side,
                        size=str(size),
                        entry_price=str(entry_price),
                        pnl=unrealized_pnl,
                        leverage=leverage,
                        margin=margin_used,
                        fees=0.0,
                        status='open'
                    )
                    db.session.add(new_trade)
                    new_trades += 1
                    
            except Exception as e:
                logging.error(f"Erro ao processar posição {position} para usuário {user_id}: {e}")
                continue

        # Fechar trades que não estão mais abertos
        try:
            open_trades = Trade.query.filter_by(user_id=user_id, status='open').all()
            for trade in open_trades:
                if (trade.symbol, trade.side) not in current_open_positions:
                    try:
                        trade.close_trade(exit_price=0, fees=0)
                        trade.closed_at = datetime.utcnow()
                        closed_trades += 1
                    except Exception as e:
                        logging.error(f"Erro ao fechar trade {trade.id} para usuário {user_id}: {e}")
                        continue
        except Exception as e:
            logging.error(f"Erro ao processar fechamento de trades para usuário {user_id}: {e}")

        # Commit com tratamento de erro
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao salvar sincronização para usuário {user_id}: {e}")
            return jsonify({'error': 'Erro ao salvar dados de sincronização'}), 500
        
        logging.info(f"Sincronização concluída para usuário {user_id}: {new_trades} novos, {updated_trades} atualizados, {closed_trades} fechados")
        return jsonify({
            'success': True,
            'message': f'Sincronização concluída: {new_trades} novos, {updated_trades} atualizados, {closed_trades} fechados'
        }), 200
        
    except Exception as e:
        logging.error(f"Erro geral na sincronização para usuário {session.get('user_id')}: {e}", exc_info=True)
        return jsonify({'error': f'Erro interno na sincronização: {str(e)}'}), 500

@dashboard_bp.route('/open-positions', methods=['GET'])
@require_login
def get_open_positions():
    """Retorna posições abertas do usuário"""
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Verificar se as credenciais da API estão configuradas
        if not user.bitget_api_key_encrypted or not user.bitget_api_secret_encrypted:
            return jsonify({
                'success': True,
                'data': [],
                'message': 'API não configurada'
            }), 200
        
        # Descriptografar credenciais da API
        api_key = decrypt_api_key(user.bitget_api_key_encrypted)
        api_secret = decrypt_api_key(user.bitget_api_secret_encrypted)
        passphrase = decrypt_api_key(user.bitget_passphrase_encrypted) if user.bitget_passphrase_encrypted else None
        
        if not api_key or not api_secret:
            return jsonify({
                'success': True,
                'data': [],
                'message': 'Erro ao descriptografar credenciais'
            }), 200
        
        # Criar cliente Bitget
        bitget_client = BitgetAPI(api_key=api_key, secret_key=api_secret, passphrase=passphrase)
        
        # Obter posições abertas usando o endpoint all-position que fornece dados completos
        positions_response = bitget_client.get_all_positions()
        
        if not positions_response or positions_response.get('code') != '00000':
            return jsonify({
                'success': True,
                'data': [],
                'message': 'Erro ao conectar com a API da Bitget'
            }), 200
        
        # Processar dados das posições
        positions_data = positions_response.get('data', [])
        
        # Função auxiliar para converter valores para float de forma segura
        def safe_float(value, default=0):
            try:
                if value is None or value == '' or value == 'null':
                    return default
                return float(value)
            except (ValueError, TypeError):
                return default
        
        # Função para calcular ROE com leverage
        def calculate_roe(unrealized_pnl, margin_real):
            """Calcula ROE usando a margem real investida pelo usuário"""
            try:
                unrealized_pnl = safe_float(unrealized_pnl)
                margin_real = safe_float(margin_real)
                
                if margin_real <= 0:
                    return 0
                
                # ROE = (PnL não realizado / margem real investida) * 100
                roe = (unrealized_pnl / margin_real) * 100
                return roe
                
            except Exception as e:
                print(f"Erro ao calcular ROE: {e}")
                return 0
        
        # Filtrar apenas posições com tamanho > 0 (posições realmente abertas)
        open_positions = []
        for position in positions_data:
            total_size = safe_float(position.get('total', 0))
            if total_size > 0:
                leverage = safe_float(position.get('leverage', 1))
                unrealized_pnl = safe_float(position.get('unrealizedPL', 0))
                entry_price = safe_float(position.get('openPriceAvg', 0))
                symbol = position.get('symbol', '')
                side = position.get('holdSide', '')
                
                # Obter margem real da API
                margin_real = safe_float(position.get('marginSize') or position.get('margin', 0))
                
                # Calcular ROE usando margem real
                roe = calculate_roe(unrealized_pnl, margin_real)
                
                # Salvar operação no banco de dados se ainda não existir
                try:
                    from models.trade import Trade
                    existing_trade = Trade.query.filter_by(
                        user_id=user_id,
                        symbol=symbol,
                        side=side,
                        status='open'
                    ).first()
                    
                    if not existing_trade:
                        # Criar nova operação no banco
                        new_trade = Trade(
                            user_id=user_id,
                            symbol=symbol,
                            side=side,
                            size=str(total_size),
                            entry_price=str(entry_price),
                            leverage=leverage,
                            status='open',
                            margin=margin_real,
                            fees=0.0,  # Valor padrão para operações abertas
                            opened_at=datetime.utcnow()
                        )
                        db.session.add(new_trade)
                        db.session.commit()
                        print(f"Nova operação salva no banco: {symbol} {side} - Margem: {margin_real}")
                    else:
                        # Atualizar dados da operação existente
                        existing_trade.size = str(total_size)
                        existing_trade.entry_price = str(entry_price)
                        existing_trade.leverage = leverage
                        existing_trade.margin = margin_real
                        existing_trade.roe = roe  # Atualizar ROE calculado
                        existing_trade.pnl = unrealized_pnl  # Atualizar PnL não realizado
                        db.session.commit()
                        
                except Exception as e:
                    print(f"Erro ao salvar operação no banco: {e}")
                    db.session.rollback()
                
                open_positions.append({
                    'symbol': symbol,
                    'side': side,
                    'size': total_size,
                    'available': safe_float(position.get('available', 0)),
                    'locked': safe_float(position.get('locked', 0)),
                    'leverage': leverage,
                    'margin_mode': position.get('marginMode', ''),
                    'position_mode': position.get('posMode', ''),
                    'entry_price': entry_price,
                    'mark_price': safe_float(position.get('markPrice', 0)),
                    'unrealized_pnl': unrealized_pnl,
                    'margin_size': safe_float(position.get('marginSize', 0)),
                    'liquidation_price': safe_float(position.get('liquidationPrice', 0)),
                    'margin_ratio': safe_float(position.get('marginRatio', 0)),
                    'margin_coin': position.get('marginCoin', 'USDT'),
                    'achieved_profits': safe_float(position.get('achievedProfits', 0)),
                    'break_even_price': safe_float(position.get('breakEvenPrice', 0)),
                    'total_fee': safe_float(position.get('totalFee', 0)),
                    'take_profit': position.get('takeProfit', ''),
                    'stop_loss': position.get('stopLoss', ''),
                    'created_time': position.get('cTime', ''),
                    'updated_time': position.get('uTime', ''),
                    'roe': roe,  # ROE calculado com leverage
                    # Campos adicionais da API Bitget v2
                    'open_delegate_size': safe_float(position.get('openDelegateSize', 0)),
                    'keep_margin_rate': safe_float(position.get('keepMarginRate', 0)),
                    'deducted_fee': safe_float(position.get('deductedFee', 0)),
                    'take_profit_id': position.get('takeProfitId', ''),
                    'stop_loss_id': position.get('stopLossId', ''),
                    'asset_mode': position.get('assetMode', 'single')
                })
        
        return jsonify({
            'success': True,
            'data': open_positions,
            'total_positions': len(open_positions)
        }), 200
        
    except Exception as e:
        print(f"Erro ao obter posições abertas: {e}")
        return jsonify({
            'success': True,
            'data': [],
            'message': f'Erro interno: {str(e)}'
        }), 200

@dashboard_bp.route('/account-balance', methods=['GET'])
@require_login
def get_account_balance():
    """Retorna saldo da conta Bitget"""
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Verificar se as credenciais da API estão configuradas
        if not user.bitget_api_key_encrypted or not user.bitget_api_secret_encrypted:
            return jsonify({
                'success': True,
                'available_balance': 0,
                'total_balance': 0,
                'unrealized_pnl': 0,
                'margin_ratio': 0,
                'currency': 'USDT',
                'api_configured': False
            }), 200
        
        # Descriptografar credenciais da API
        api_key = decrypt_api_key(user.bitget_api_key_encrypted)
        api_secret = decrypt_api_key(user.bitget_api_secret_encrypted)
        passphrase = decrypt_api_key(user.bitget_passphrase_encrypted) if user.bitget_passphrase_encrypted else None
        
        if not api_key or not api_secret:
            return jsonify({
                'success': True,
                'available_balance': 0,
                'total_balance': 0,
                'unrealized_pnl': 0,
                'margin_ratio': 0,
                'currency': 'USDT',
                'api_configured': False
            }), 200
        
        # Criar cliente Bitget
        bitget_client = BitgetAPI(api_key=api_key, secret_key=api_secret, passphrase=passphrase)
        
        try:
            futures_balance = bitget_client.get_futures_balance()
            if not futures_balance or futures_balance.get('code') != '00000':
                # Se falhar, retornar dados padrão com estrutura completa
                print(f"❌ Erro na API Bitget: {futures_balance}")
                return jsonify({
                    'success': True,
                    'api_configured': True,
                    'available_balance': 0,
                    'total_balance': 0,
                    'unrealized_pnl': 0,
                    'margin_ratio': 0,
                    'currency': 'USDT',
                    'message': 'API Bitget temporariamente indisponível',
                    'error': 'Erro ao conectar com a API da Bitget'
                }), 200
        except Exception as api_error:
            # Se houver exceção na API, retornar dados padrão
            print(f"❌ Exceção na API Bitget: {api_error}")
            return jsonify({
                'success': True,
                'api_configured': True,
                'available_balance': 0,
                'total_balance': 0,
                'unrealized_pnl': 0,
                'margin_ratio': 0,
                'currency': 'USDT',
                'message': 'API Bitget temporariamente indisponível',
                'error': str(api_error)
            }), 200
        
        # Processar dados do saldo
        balance_data_list = futures_balance.get('data', [])
        
        # A API retorna uma lista, pegar o primeiro elemento (USDT)
        if balance_data_list and len(balance_data_list) > 0:
            balance_data = balance_data_list[0]  # Primeiro elemento da lista
        else:
            balance_data = {}
        
        # Log dos dados brutos para debug
        print(f"--- DEBUG: Dados do saldo processados ---")
        print(f"Available: {balance_data.get('available', 0)}")
        print(f"Account Equity: {balance_data.get('accountEquity', 0)}")
        print(f"Unrealized PnL: {balance_data.get('unrealizedPL', 0)}")
        print(f"Margin Ratio: {balance_data.get('crossedRiskRate', 0)}")
        print("-------------------------------------")
        
        # Retornar dados estruturados corretamente
        response_data = {
            'success': True,
            'api_configured': True,
            'available_balance': float(balance_data.get('available', 0)),
            'total_balance': float(balance_data.get('accountEquity', 0)),
            'unrealized_pnl': float(balance_data.get('unrealizedPL', 0)),
            'margin_ratio': float(balance_data.get('crossedRiskRate', 0)) * 100,
            'currency': 'USDT'
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ Erro geral ao obter saldo: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        
        # Verificar se o usuário tem credenciais configuradas
        api_configured = False
        try:
            user = User.query.get(session['user_id'])
            api_configured = bool(user and user.bitget_api_key_encrypted and user.bitget_api_secret_encrypted)
        except:
            pass
        
        return jsonify({
            'success': True,
            'api_configured': api_configured,
            'available_balance': 0,
            'total_balance': 0,
            'unrealized_pnl': 0,
            'margin_ratio': 0,
            'currency': 'USDT',
            'message': 'Erro interno do servidor',
            'error': str(e)
        }), 200

@dashboard_bp.route('/close-position', methods=['POST'])
@require_login
def close_position():
    """Fecha uma posição usando flash close"""
    try:
        from flask import request
        
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Verificar se as credenciais da API estão configuradas
        if not user.bitget_api_key_encrypted or not user.bitget_api_secret_encrypted:
            return jsonify({
                'success': False,
                'message': 'Credenciais da API não configuradas'
            }), 400
        
        # Obter dados da requisição
        data = request.get_json()
        symbol = data.get('symbol')
        side = data.get('side')
        
        if not symbol:
            return jsonify({
                'success': False,
                'message': 'Symbol é obrigatório'
            }), 400
        
        # Descriptografar credenciais da API
        api_key = decrypt_api_key(user.bitget_api_key_encrypted)
        api_secret = decrypt_api_key(user.bitget_api_secret_encrypted)
        passphrase = decrypt_api_key(user.bitget_passphrase_encrypted) if user.bitget_passphrase_encrypted else None
        
        if not api_key or not api_secret:
            return jsonify({
                'success': False,
                'message': 'Erro ao descriptografar credenciais da API'
            }), 500
        
        # Criar cliente Bitget
        bitget_client = BitgetAPI(api_key=api_key, secret_key=api_secret, passphrase=passphrase)
        
        # Mapear side para holdSide da API Bitget
        hold_side = None
        if side:
            hold_side = 'long' if side.lower() == 'long' else 'short'
        
        # Fechar posição usando flash close
        result = bitget_client.flash_close_position(symbol=symbol, hold_side=hold_side)
        
        if result and result.get('code') == '00000':
            return jsonify({
                'success': True,
                'message': 'Posição fechada com sucesso',
                'data': result.get('data', {})
            }), 200
        else:
            error_msg = result.get('msg', 'Erro desconhecido') if result else 'Erro na comunicação com a API'
            return jsonify({
                'success': False,
                'message': f'Erro ao fechar posição: {error_msg}'
            }), 400
        
    except Exception as e:
        logging.error(f"Erro ao fechar posição para usuário {session.get('user_id')}: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@dashboard_bp.route('/api-status', methods=['GET'])
@require_login
def api_status():
    """Verifica o status da configuração da API"""
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"success": False, "configured": False, "message": "User not found"}), 404
        
        is_configured = bool(user.bitget_api_key_encrypted and 
                           user.bitget_api_secret_encrypted and 
                           user.bitget_passphrase_encrypted)
        
        if is_configured:
            return jsonify({"success": True, "configured": True, "message": "API is configured."})
        else:
            return jsonify({"success": True, "configured": False, "message": "API not configured."})
            
    except Exception as e:
        logging.error(f"Erro ao verificar status da API: {e}")
        return jsonify({"success": False, "configured": False, "message": "Error checking API status"}), 500

@dashboard_bp.route('/auto-sync/status', methods=['GET'])
@require_login
def get_auto_sync_status():
    """Retorna o status da sincronização automática"""
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        api_configured = bool(user.bitget_api_key_encrypted and 
                            user.bitget_api_secret_encrypted and 
                            user.bitget_passphrase_encrypted)
        
        # Para agora, retornamos um status padrão
        # Em uma implementação mais avançada, isso viria de um serviço de sincronização
        return jsonify({
            "success": True,
            "api_configured": api_configured,
            "status": "running" if api_configured else "stopped",
            "last_sync": None,
            "next_sync": None,
            "interval": 300,  # 5 minutos
            "running": api_configured
        })
        
    except Exception as e:
        logging.error(f"Erro ao obter status da sincronização: {e}")
        return jsonify({"success": False, "message": "Error getting sync status"}), 500

@dashboard_bp.route('/auto-sync/start', methods=['POST'])
@require_login
def start_auto_sync():
    """Inicia a sincronização automática"""
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        api_configured = bool(user.bitget_api_key_encrypted and 
                            user.bitget_api_secret_encrypted and 
                            user.bitget_passphrase_encrypted)
        
        if not api_configured:
            return jsonify({
                "success": False,
                "message": "API não configurada",
                "api_configured": False
            }), 400
        
        # Para agora, apenas retornamos sucesso
        # Em uma implementação mais avançada, isso iniciaria um serviço de background
        return jsonify({
            "success": True,
            "message": "Sincronização automática iniciada",
            "status": "running",
            "api_configured": True
        })
        
    except Exception as e:
        logging.error(f"Erro ao iniciar sincronização: {e}")
        return jsonify({"success": False, "message": "Error starting sync"}), 500

@dashboard_bp.route('/all-positions', methods=['GET'])
@require_login
def get_all_positions():
    """Retorna todas as posições do usuário usando o endpoint all-position da Bitget"""
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Verificar se as credenciais da API estão configuradas
        if not user.bitget_api_key_encrypted or not user.bitget_api_secret_encrypted:
            return jsonify({
                'success': True,
                'positions': [],
                'message': 'API não configurada'
            }), 200
        
        # Descriptografar credenciais da API
        api_key = decrypt_api_key(user.bitget_api_key_encrypted)
        api_secret = decrypt_api_key(user.bitget_api_secret_encrypted)
        passphrase = decrypt_api_key(user.bitget_passphrase_encrypted) if user.bitget_passphrase_encrypted else None
        
        if not api_key or not api_secret:
            return jsonify({
                'success': True,
                'positions': [],
                'message': 'Erro ao descriptografar credenciais'
            }), 200
        
        # Criar cliente Bitget
        bitget_client = BitgetAPI(api_key=api_key, secret_key=api_secret, passphrase=passphrase)
        
        # Obter todas as posições usando o endpoint all-position
        positions_response = bitget_client.get_all_positions()
        
        if not positions_response or positions_response.get('code') != '00000':
            return jsonify({
                'success': True,
                'positions': [],
                'message': 'Erro ao conectar com a API da Bitget'
            }), 200
        
        positions_data = positions_response.get('data', [])
        
        # Retornar todas as posições com todos os campos da API
        all_positions = []
        for position in positions_data:
            all_positions.append({
                'marginCoin': position.get('marginCoin', ''),
                'symbol': position.get('symbol', ''),
                'holdSide': position.get('holdSide', ''),
                'openDelegateSize': position.get('openDelegateSize', ''),
                'marginSize': position.get('marginSize', ''),
                'available': position.get('available', ''),
                'locked': position.get('locked', ''),
                'total': position.get('total', ''),
                'leverage': position.get('leverage', ''),
                'achievedProfits': position.get('achievedProfits', ''),
                'openPriceAvg': position.get('openPriceAvg', ''),
                'marginMode': position.get('marginMode', ''),
                'posMode': position.get('posMode', ''),
                'unrealizedPL': position.get('unrealizedPL', ''),
                'liquidationPrice': position.get('liquidationPrice', ''),
                'keepMarginRate': position.get('keepMarginRate', ''),
                'markPrice': position.get('markPrice', ''),
                'breakEvenPrice': position.get('breakEvenPrice', ''),
                'totalFee': position.get('totalFee', ''),
                'deductedFee': position.get('deductedFee', ''),
                'takeProfit': position.get('takeProfit', ''),
                'stopLoss': position.get('stopLoss', ''),
                'takeProfitId': position.get('takeProfitId', ''),
                'stopLossId': position.get('stopLossId', ''),
                'marginRatio': position.get('marginRatio', ''),
                'assetMode': position.get('assetMode', ''),
                'cTime': position.get('cTime', ''),
                'uTime': position.get('uTime', '')
            })
        
        return jsonify({
            'success': True,
            'positions': all_positions,
            'total_positions': len(all_positions)
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter todas as posições: {e}")
        return jsonify({
            'success': True,
            'positions': [],
            'message': f'Erro interno: {str(e)}'
        }), 200

@dashboard_bp.route('/finished-positions', methods=['GET'])
@require_login
def get_finished_positions():
    """Retorna o histórico de posições finalizadas do usuário usando o endpoint history-position da Bitget com filtro de data"""
    try:
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'message': 'Usuário não encontrado'}), 404
        
        # Obter parâmetros de filtro de data da query string (mesmo padrão das estatísticas)
        start_date = request.args.get('start_date')  # Formato: YYYY-MM-DD
        end_date = request.args.get('end_date')      # Formato: YYYY-MM-DD
        
        logging.info(f"[DEBUG] Filtros de data para posições finalizadas - Start: {start_date}, End: {end_date}")
        
        # Verificar se as credenciais da API estão configuradas
        if not user.bitget_api_key_encrypted or not user.bitget_api_secret_encrypted:
            return jsonify({
                'success': True,
                'positions': [],
                'message': 'API não configurada'
            }), 200
        
        # Descriptografar credenciais da API
        api_key = decrypt_api_key(user.bitget_api_key_encrypted)
        api_secret = decrypt_api_key(user.bitget_api_secret_encrypted)
        passphrase = decrypt_api_key(user.bitget_passphrase_encrypted) if user.bitget_passphrase_encrypted else None
        
        if not api_key or not api_secret:
            return jsonify({
                'success': True,
                'positions': [],
                'message': 'Erro ao descriptografar credenciais'
            }), 200
        
        # Criar cliente Bitget
        bitget_client = BitgetAPI(api_key=api_key, secret_key=api_secret, passphrase=passphrase)
        
        # Obter histórico de posições finalizadas
        history_response = bitget_client.get_closed_positions_history(limit=100)
        
        if not history_response or history_response.get('code') != '00000':
            return jsonify({
                'success': True,
                'positions': [],
                'message': 'Erro ao conectar com a API da Bitget'
            }), 200
        
        # A resposta da API da Bitget tem estrutura: data.list
        data_section = history_response.get('data', {})
        positions_data = data_section.get('list', []) if isinstance(data_section, dict) else []
        
        # Aplicar o mesmo filtro de data usado nas estatísticas
        filtered_positions = []
        if positions_data:
            from datetime import datetime
            
            # Aplicar filtro do mês atual apenas quando não há filtros de data especificados (mesma lógica da rota /stats)
            use_current_month_filter = not start_date and not end_date
            
            # Converter strings de data para datetime
            start_datetime = None
            end_datetime = None
            
            if start_date:
                try:
                    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                    start_datetime = start_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
                except ValueError:
                    logging.error(f"[ERROR] Data inicial inválida: {start_date}")
            
            if end_date:
                try:
                    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                    end_datetime = end_datetime.replace(hour=23, minute=59, second=59, microsecond=999000)
                except ValueError:
                    logging.error(f"[ERROR] Data final inválida: {end_date}")
            
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            # Filtrar posições por data (exatamente a mesma lógica da rota /stats)
            for position in positions_data:
                utime = position.get('utime')
                if utime:
                    try:
                        # Converter timestamp para datetime
                        position_date = datetime.fromtimestamp(int(utime) / 1000)
                        
                        # Aplicar filtro de data
                        should_include = False
                        
                        if use_current_month_filter:
                            # Filtro automático para o mês atual quando não há filtros especificados
                            if position_date.month == current_month and position_date.year == current_year:
                                should_include = True
                        else:
                            # Aplicar filtros de data especificados pelo usuário
                            if start_datetime and end_datetime:
                                should_include = start_datetime <= position_date <= end_datetime
                            elif start_datetime:
                                should_include = position_date >= start_datetime
                            elif end_datetime:
                                should_include = position_date <= end_datetime
                            else:
                                should_include = True
                        
                        if should_include:
                            filtered_positions.append(position)
                    except (ValueError, TypeError, OSError):
                        continue
        
        # Obter histórico de ordens para pegar informações de leverage
        orders_response = bitget_client.get_orders_history(limit=500)
        orders_data = []
        if orders_response and orders_response.get('code') == '00000':
            orders_section = orders_response.get('data', {})
            orders_data = orders_section.get('entrustedList', []) if isinstance(orders_section, dict) else []
        
        # Criar um mapeamento de symbol -> leverage baseado nas ordens
        leverage_map = {}
        for order in orders_data:
            symbol = order.get('symbol', '').upper()
            leverage = order.get('leverage')
            if symbol and leverage:
                leverage_map[symbol] = leverage
        
        # Retornar posições finalizadas filtradas com informações de leverage adicionadas
        finished_positions = []
        for position in filtered_positions:
            # Adicionar leverage se disponível
            symbol = position.get('symbol', '').upper()
            if symbol in leverage_map:
                position['leverage'] = leverage_map[symbol]
            
            finished_positions.append(position)
        
        logging.info(f"[DEBUG] Posições finalizadas filtradas: {len(finished_positions)} de {len(positions_data)} total")
        
        return jsonify({
            'success': True,
            'positions': finished_positions,
            'total_positions': len(finished_positions),
            'filters_applied': {
                'start_date': start_date,
                'end_date': end_date,
                'total_before_filter': len(positions_data),
                'total_after_filter': len(finished_positions)
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao obter posições finalizadas: {e}")
        return jsonify({
            'success': True,
            'positions': [],
            'message': f'Erro interno: {str(e)}'
        }), 200

@dashboard_bp.route('/auto-sync/stop', methods=['POST'])
@require_login
def stop_auto_sync():
    """Para a sincronização automática"""
    try:
        # Para agora, apenas retornamos sucesso
        # Em uma implementação mais avançada, isso pararia um serviço de background
        return jsonify({
            "success": True,
            "message": "Sincronização automática parada",
            "status": "stopped"
        })
        
    except Exception as e:
        logging.error(f"Erro ao parar sincronização: {e}")
        return jsonify({"success": False, "message": "Error stopping sync"}), 500

@dashboard_bp.route('/reconnect-api', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def reconnect_api():
    if request.method == 'OPTIONS':
        return '', 200
    """
    Reconecta a API buscando credenciais criptografadas do banco de dados
    """
    try:
        # Verificar se o usuário está logado
        if 'user_id' not in session:
            return jsonify({
                'success': False, 
                'message': 'Usuário não autenticado. Faça login novamente.',
                'code': 'UNAUTHORIZED'
            }), 401
        
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({
                'success': False, 
                'message': 'Usuário não encontrado.',
                'code': 'USER_NOT_FOUND'
            }), 404
        
        # Verificar se o usuário tem credenciais da API configuradas
        has_credentials = bool(
            user.bitget_api_key_encrypted and 
            user.bitget_api_secret_encrypted and 
            user.bitget_passphrase_encrypted
        )
        
        if not has_credentials:
            # Verificar se tem credenciais parciais
            partial_credentials = []
            if user.bitget_api_key_encrypted:
                partial_credentials.append('API Key')
            if user.bitget_api_secret_encrypted:
                partial_credentials.append('API Secret')
            if user.bitget_passphrase_encrypted:
                partial_credentials.append('Passphrase')
            
            if partial_credentials:
                message = f'Credenciais incompletas detectadas: {", ".join(partial_credentials)}. Configure todas as credenciais no seu perfil.'
            else:
                message = 'Nenhuma credencial da API encontrada. Configure suas credenciais da API Bitget no seu perfil para usar esta funcionalidade.'
            
            return jsonify({
                'success': False,
                'message': message,
                'code': 'CREDENTIALS_NOT_CONFIGURED',
                'needs_config': True,
                'redirect_to_profile': True,
                'partial_credentials': partial_credentials
            }), 400
        
        # Descriptografar credenciais
        try:
            from utils.security import decrypt_api_key
            
            api_key = decrypt_api_key(user.bitget_api_key_encrypted)
            api_secret = decrypt_api_key(user.bitget_api_secret_encrypted)
            passphrase = decrypt_api_key(user.bitget_passphrase_encrypted)
            
            if not (api_key and api_secret and passphrase):
                return jsonify({
                    'success': False,
                    'message': 'Erro ao descriptografar credenciais da API. Reconfigure suas credenciais no perfil.',
                    'code': 'DECRYPTION_ERROR',
                    'needs_config': True,
                    'redirect_to_profile': True
                }), 500
                
        except Exception as e:
            logging.error(f"Erro ao descriptografar credenciais para usuário {user_id}: {e}")
            return jsonify({
                'success': False,
                'message': 'Erro ao processar credenciais da API. Reconfigure suas credenciais no perfil.',
                'code': 'DECRYPTION_ERROR',
                'needs_config': True,
                'redirect_to_profile': True
            }), 500
        
        # Criar cliente Bitget e testar conexão
        try:
            bitget_client = BitgetAPI(
                api_key=api_key,
                secret_key=api_secret,
                passphrase=passphrase
            )
            
            # Testar a conexão obtendo as informações da conta (corrigido)
            account_info = bitget_client.get_account_balance()
            
            if account_info and account_info.get('code') == '00000':
                logging.info(f"✅ API do usuário {user_id} reconectada com sucesso.")
                
                # Retornar sucesso com dados da API
                return jsonify({
                    'success': True,
                    'message': 'API reconectada com sucesso! Dados atualizados.',
                    'data': {
                        'api_status': 'connected',
                        'reconnected_at': datetime.now().isoformat(),
                        'api_configured': True,
                        'account_balance': account_info.get('data', {})
                    }
                }), 200

            else:
                # Conexão falhou na Bitget
                error_msg = account_info.get('msg', 'Erro desconhecido na Bitget') if account_info else 'Resposta vazia da Bitget'
                logging.warning(f"❌ Falha na reconexão da API para usuário {user_id}: {error_msg}")
                return jsonify({
                    'success': False,
                    'message': f'Falha ao conectar com a API Bitget: {error_msg}',
                    'error_type': 'CONNECTION_ERROR',
                    'redirect_to_profile': True
                }), 400
        except Exception as e:
            logging.error(f"❌ ERRO ao conectar ou testar a API Bitget para usuário {user_id}: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Erro ao testar a conexão da API: {str(e)}',
                'error_type': 'BITGET_API_CONNECTION_FAILED'
            }), 500
            
    except Exception as e:
        logging.error(f"Erro interno no reconnect_api: {e}")
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor. Tente novamente em alguns instantes.',
            'code': 'INTERNAL_ERROR'
        }), 500

# Novo endpoint para verificar status das credenciais
# @dashboard_bp.route('/credentials/status', methods=['GET'])
# @cross_origin(supports_credentials=True)
# def check_credentials_status():
#     """
#     Verifica o status das credenciais da API do usuário
#     """
#     try:
#         # Verificar se o usuário está logado
#         if 'user_id' not in session:
#             return jsonify({
#                 'success': False,
#                 'message': 'Usuário não autenticado.',
#                 'code': 'UNAUTHORIZED'
#             }), 401
#         
#         user_id = session['user_id']
#         user = User.query.get(user_id)
#         
#         if not user:
#             return jsonify({
#                 'success': False,
#                 'message': 'Usuário não encontrado.',
#                 'code': 'USER_NOT_FOUND'
#             }), 404
#         
#         # Verificar status das credenciais
#         has_api_key = bool(user.bitget_api_key_encrypted)
#         has_api_secret = bool(user.bitget_api_secret_encrypted)
#         has_passphrase = bool(user.bitget_passphrase_encrypted)
#         
#         has_all_credentials = has_api_key and has_api_secret and has_passphrase
#         
#         status = {
#             'has_credentials': has_all_credentials,
#             'has_api_key': has_api_key,
#             'has_api_secret': has_api_secret,
#             'has_passphrase': has_passphrase,
#             'user_email': user.email,
#             'user_id': user_id,
#             'checked_at': datetime.utcnow().isoformat()
#         }
#         
#         # Determinar mensagem baseada no status
#         if has_all_credentials:
#             message = 'Todas as credenciais da API estão configuradas.'
#         elif has_api_key or has_api_secret or has_passphrase:
#             missing = []
#             if not has_api_key:
#                 missing.append('API Key')
#             if not has_api_secret:
#                 missing.append('API Secret')
#             if not has_passphrase:
#                 missing.append('Passphrase')
#             message = f'Credenciais incompletas. Faltam: {", ".join(missing)}'
#         else:
#             message = 'Nenhuma credencial da API configurada.'
#         
#         return jsonify({
#             'success': True,
#             'message': message,
#             'status': status
#         }), 200
#         
#     except Exception as e:
#         logging.error(f"Erro ao verificar status das credenciais: {e}")
#         return jsonify({
#             'success': False,
#             'message': 'Erro interno do servidor.',
#             'code': 'INTERNAL_ERROR'
#         }), 500

# Endpoints para integração com Nautilus Automação
@dashboard_bp.route('/nautilus/login', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def nautilus_login():
    """Proxy para autenticação no Nautilus"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Usar credenciais fixas do admin Nautilus
        login_data = {
            "email": "admin@bigwhale.com",
            "password": "bigwhale"
        }
        
        response = requests.post(
            "https://bw.mdsa.com.br/login",
            json=login_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'token': data.get('token'),
                'userId': data.get('userId')
            })
        else:
            return jsonify({'error': 'Falha na autenticação'}), response.status_code
            
    except Exception as e:
        logging.error(f"Erro na autenticação Nautilus: {str(e)}")
        return jsonify({'error': 'Erro interno na autenticação'}), 500


@dashboard_bp.route('/nautilus/active-operations', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def nautilus_active_operations():
    """Proxy para operações ativas do Nautilus"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        # Extrair headers de autorização
        auth_token = request.headers.get('Authorization', '')
        user_id = request.headers.get('auth-userid', '')
        
        if not auth_token or not user_id:
            return jsonify({'error': 'Headers de autenticação necessários'}), 400
        
        response = requests.get(
            "https://bw.mdsa.com.br/operation/active-operations",
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': auth_token,
                'auth-userid': user_id,
                'Origin': 'https://bw-admin.mdsa.com.br',
                'Referer': 'https://bw-admin.mdsa.com.br/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return jsonify({'error': 'Erro ao buscar operações'}), response.status_code
            
    except Exception as e:
        logging.error(f"Erro nas operações ativas Nautilus: {str(e)}")
        return jsonify({'error': 'Erro interno ao buscar operações'}), 500