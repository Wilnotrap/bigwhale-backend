import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './AdminDashboard.css';
import API_CONFIG from '../../config/api';

const AdminDashboard = ({ user }) => {
  console.log('AdminDashboard: Componente carregando...');
  const { logout } = useAuth();
  
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState({
    total_under_management: 0,
    total_trades: 0,
    total_users: 0,
    active_users: 0,
    total_pnl: 0,
    avg_roe: 0,
    win_rate: 0,
    open_positions: 0,
    closed_positions: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('todos');
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [isAutoUpdating, setIsAutoUpdating] = useState(false);

  useEffect(() => {
    console.log('AdminDashboard: useEffect inicial - carregando dados...');
    fetchAdminData();
  }, []);

  useEffect(() => {
    console.log('AdminDashboard: Filtrando usuários...');
    filterUsers();
  }, [users, searchTerm, statusFilter]);

  // Auto-atualização a cada 30 segundos
  useEffect(() => {
    const interval = setInterval(async () => {
      console.log('🔄 [AUTO-UPDATE] Atualizando dados admin silenciosamente...');
      setIsAutoUpdating(true);
      await fetchAdminData(false); // Carregamento silencioso
      setTimeout(() => setIsAutoUpdating(false), 1000);
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const fetchAdminData = useCallback(async (showLoading = true) => {
    if (showLoading) setLoading(true);
    setError(null);
    
    try {
      console.log('AdminDashboard: Fazendo requisições para backend...');
      
      // Fazer login primeiro para garantir que a sessão está ativa
      const loginResponse = await fetch(`${API_CONFIG.baseURL}/api/auth/session`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!loginResponse.ok) {
        throw new Error('Sessão não autenticada');
      }
      
      const sessionData = await loginResponse.json();
      console.log('AdminDashboard: Dados da sessão:', sessionData);
      
      if (!sessionData.user || !sessionData.user.is_admin) {
        throw new Error('Usuário não é administrador');
      }
      
      // Agora fazer as requisições de admin
      const [usersResponse, statsResponse] = await Promise.all([
        fetch(`${API_CONFIG.baseURL}/api/admin/users`, { 
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        }),
        fetch(`${API_CONFIG.baseURL}/api/admin/dashboard/stats`, { 
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        })
      ]);

      console.log('AdminDashboard: Status das respostas:', {
        users: usersResponse.status,
        stats: statsResponse.status
      });

      if (!usersResponse.ok || !statsResponse.ok) {
        const usersError = !usersResponse.ok ? await usersResponse.text() : null;
        const statsError = !statsResponse.ok ? await statsResponse.text() : null;
        console.error('AdminDashboard: Erros nas respostas:', { usersError, statsError });
        throw new Error('Falha ao carregar dados do administrador.');
      }

      const [usersData, statsData] = await Promise.all([
        usersResponse.json(),
        statsResponse.json()
      ]);

      console.log('AdminDashboard: Dados recebidos:', { usersData, statsData });

      setUsers(usersData.users || []);
      setStats(statsData);
      
    } catch (error) {
      console.error('Erro ao carregar dados do admin:', error);
      setError(error.message);
    } finally {
      if (showLoading) setLoading(false);
    }
  }, []);

  const filterUsers = useCallback(() => {
    let filtered = users;

    if (searchTerm) {
      filtered = filtered.filter(user => 
        user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (statusFilter !== 'todos') {
      filtered = filtered.filter(user => {
        switch (statusFilter) {
          case 'ativos':
            return user.is_active;
          case 'inativos':
            return !user.is_active;
          case 'admins':
            return user.is_admin;
          default:
            return true;
        }
      });
    }

    setFilteredUsers(filtered);
  }, [users, searchTerm, statusFilter]);

  const handleUserAction = (user, action) => {
    console.log(`AdminDashboard: Ação ${action} para usuário:`, user);
    
    switch (action) {
      case 'view':
        console.log(`AdminDashboard: Navegando para o dashboard do usuário: ${user.full_name}`);
        // Navegar para a página de dashboard do usuário
        window.location.href = `/admin/user/${user.id}/dashboard`;
        break;
      case 'edit':
        console.log(`AdminDashboard: Editando usuário: ${user.full_name}`);
        break;
      case 'delete':
        console.log(`AdminDashboard: Deletando usuário: ${user.full_name}`);
        break;
      default:
        console.log(`AdminDashboard: Ação desconhecida: ${action}`);
    }
  };

  const handleAdminDashboard = () => {
    console.log('AdminDashboard: Navegando para dashboard do admin');
    // Encontrar o usuário admin atual e navegar para seu dashboard
    if (user && user.id) {
      window.location.href = `/admin/user/${user.id}/dashboard`;
    } else {
      // Fallback: navegar para dashboard regular
      window.location.href = '/dashboard';
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD'
    }).format(value || 0);
  };

  const formatPercentage = (value) => {
    return `${(value || 0).toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="admin-dashboard">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Carregando dados do administrador...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-dashboard">
        <div className="error-container">
          <h2>Erro ao carregar dados</h2>
          <p>{error}</p>
          <button onClick={() => fetchAdminData()} className="retry-button">
            Tentar novamente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <div className="header-content">
          <div className="header-left">
            <h1>🛡️ Admin Dashboard</h1>
            <p>Bem-vindo, {user?.full_name || 'Administrador'}</p>
          </div>
          <div className="header-right">
            {isAutoUpdating && (
              <div className="auto-update-indicator">
                <span className="update-dot"></span>
                Atualizando...
              </div>
            )}
            <button 
              onClick={() => fetchAdminData()} 
              className="refresh-button"
              disabled={loading}
            >
              🔄 Atualizar
            </button>
          </div>
        </div>
      </div>

      {/* Cards de Estatísticas */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <h3>Ordens Abertas</h3>
            <span className="stat-icon">📊</span>
          </div>
          <div className="stat-content">
            <div className="stat-main">
              <span className="positive">✅ 0 Positivas</span>
              <span className="negative">❌ 0 Negativas</span>
            </div>
            <div className="stat-footer">
              <span className="roe-display">ROE Total: +0.00%</span>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <h3>Valor Sob Gestão (USD)</h3>
            <span className="stat-icon">💰</span>
          </div>
          <div className="stat-content">
            <div className="stat-value">
              {formatCurrency(stats.total_under_management)}
            </div>
          </div>
        </div>

        <div className="stat-card total">
          <div className="stat-number">{stats.total_users}</div>
          <div className="stat-label">Total</div>
        </div>

        <div className="stat-card active">
          <div className="stat-number">{stats.active_users}</div>
          <div className="stat-label">Ativos</div>
        </div>

        <div className="stat-card inactive">
          <div className="stat-number">{stats.total_users - stats.active_users}</div>
          <div className="stat-label">Inativos</div>
        </div>
      </div>

      {/* Seção de Usuários */}
      <div className="users-section">
        <div className="section-header">
          <h2>Usuários</h2>
          <div className="search-controls">
            <input
              type="text"
              placeholder="Buscar usuários..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="filter-select"
            >
              <option value="todos">Todos</option>
              <option value="ativos">Ativos</option>
              <option value="inativos">Inativos</option>
              <option value="admins">Administradores</option>
            </select>
          </div>
        </div>



        <div className="users-table-container">
          <table className="users-table">
            <thead>
              <tr>
                <th>Usuário</th>
                <th>Status</th>
                <th>Último Login</th>
                <th>Total de Trades</th>
                <th>Total PNL (USD)</th>
                <th>Total sob Gestão (USD)</th>
                <th>Status Nautilus</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.length > 0 ? (
                filteredUsers.map((user) => (
                  <tr key={user.id}>
                    <td>
                      <div className="user-info">
                        <div className="user-name">{user.full_name}</div>
                        <div className="user-email">{user.email}</div>
                        {user.is_admin && <span className="admin-badge">Admin</span>}
                      </div>
                    </td>
                    <td>
                      <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                        {user.is_active ? 'Ativo' : 'Inativo'}
                      </span>
                    </td>
                    <td>-</td>
                    <td>{user.stats?.total_trades || 0}</td>
                    <td>{formatCurrency(user.stats?.total_pnl || 0)}</td>
                    <td>{formatCurrency(user.operational_balance_usd || 0)}</td>
                    <td>
                      <span className={`nautilus-badge ${user.nautilus_active ? 'active' : 'inactive'}`}>
                        {user.nautilus_active ? 'Ativo' : 'Inativo'}
                      </span>
                    </td>
                    <td>
                      <div className="action-buttons">
                        <button 
                          onClick={() => handleUserAction(user, 'view')}
                          className="action-btn view"
                          title="Ver Dashboard"
                        >
                          👁️
                        </button>
                        <button 
                          onClick={() => handleUserAction(user, 'edit')}
                          className="action-btn edit"
                          title="Editar"
                        >
                          ✏️
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="8" className="no-users">
                    Nenhum usuário encontrado
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Footer */}
      <div className="admin-footer">
        <div className="footer-actions">
          <button 
            onClick={() => window.location.href = '/admin/dashboard'}
            className="footer-btn"
            title="Ver Dashboard Consolidado"
          >
            📊 Dashboard Consolidado
          </button>
          <button 
            onClick={async () => {
              console.log('AdminDashboard: Logout');
              try {
                await logout();
              } catch (error) {
                console.error('Erro no logout:', error);
                // Fallback para redirecionamento direto
                window.location.href = '/login';
              }
            }}
            className="footer-btn logout"
          >
            🚪 Logout
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;