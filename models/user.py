# backend/models/user.py
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from database import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # API keys criptografadas
    bitget_api_key_encrypted = db.Column(db.Text, nullable=True)
    bitget_api_secret_encrypted = db.Column(db.Text, nullable=True)
    bitget_passphrase_encrypted = db.Column(db.Text, nullable=True)
    
    # Status e configurações
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # 🆕 CAMPOS DE PAGAMENTO/ASSINATURA
    has_paid = db.Column(db.Boolean, default=False, nullable=False)
    subscription_type = db.Column(db.String(50), nullable=True)  # 'monthly' ou 'annual'
    subscription_start_date = db.Column(db.DateTime, nullable=True)
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True)
    
    # Integração Nautilus
    nautilus_token = db.Column(db.Text, nullable=True)
    nautilus_user_id = db.Column(db.Integer, nullable=True)
    nautilus_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Saldo operacional
    operational_balance = db.Column(db.Float, default=0.0)
    operational_balance_usd = db.Column(db.Float, default=0.0)
    last_conversion_rate = db.Column(db.Float, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Taxa de comissão personalizada
    commission_rate = db.Column(db.Float, default=0.35)

    # Relacionamento com trades
    trades = relationship('Trade', back_populates='user', lazy='dynamic', cascade="all, delete-orphan")

    def set_password(self, password):
        """Criptografa e define a senha do usuário usando Werkzeug."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha fornecida está correta usando Werkzeug."""
        return check_password_hash(self.password_hash, password)
    
    # 🆕 MÉTODO PARA VERIFICAR ASSINATURA ATIVA
    def is_subscription_active(self):
        """Verifica se a assinatura está ativa"""
        if not self.has_paid or not self.subscription_end_date:
            return False
        return datetime.utcnow() <= self.subscription_end_date
    
    def get_operational_balance_percentage(self):
        """Calcula a porcentagem do saldo operacional já utilizado"""
        try:
            from sqlalchemy import text
            result = db.session.execute(
                text("""
                    SELECT COALESCE(SUM(t.pnl * :commission_rate), 0) as total_commissions
                    FROM trades t 
                    WHERE t.user_id = :user_id 
                    AND t.status = 'closed' 
                    AND t.pnl > 0
                """),
                {
                    'user_id': self.id,
                    'commission_rate': self.commission_rate
                }
            ).fetchone()
            
            total_commissions = float(result[0]) if result and result[0] else 0.0
            current_balance = getattr(self, 'operational_balance_usd', 0.0) or 0.0
            initial_balance = current_balance + total_commissions
            
            if initial_balance <= 0:
                return 0.0
            
            percentage_used = (total_commissions / initial_balance) * 100
            return min(percentage_used, 100.0)
            
        except Exception as e:
            print(f"Erro ao calcular porcentagem do saldo operacional: {e}")
            return 0.0
    
    def can_open_new_positions(self):
        """Verifica se o usuário pode abrir novas posições"""
        try:
            if self.is_admin:
                return True
            
            usage_percentage = self.get_operational_balance_percentage()
            
            if usage_percentage >= 95.0:
                return False
            
            return True
            
        except Exception as e:
            print(f"Erro ao verificar se pode abrir posições: {e}")
            return False
    
    def get_remaining_balance_usd(self):
        """Calcula o saldo operacional restante em USD"""
        try:
            current_balance = getattr(self, 'operational_balance_usd', 0.0) or 0.0
            return max(current_balance, 0.0)
            
        except Exception as e:
            print(f"Erro ao calcular saldo restante: {e}")
            return 0.0
    
    def to_dict(self):
        """Converte o usuário para dicionário"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            # 🆕 NOVOS CAMPOS
            'has_paid': self.has_paid,
            'subscription_active': self.is_subscription_active(),
            'subscription_type': self.subscription_type,
            'subscription_end_date': self.subscription_end_date.isoformat() if self.subscription_end_date else None,
            # Campos existentes
            'nautilus_user_id': self.nautilus_user_id,
            'nautilus_active': self.nautilus_active,
            'operational_balance': self.operational_balance,
            'operational_balance_usd': self.operational_balance_usd,
            'commission_rate': self.commission_rate,
            'can_open_positions': self.can_open_new_positions(),
            'operational_balance_percentage': self.get_operational_balance_percentage(),
            'remaining_balance_usd': self.get_remaining_balance_usd()
        }

    def __repr__(self):
        return f'<User {self.email}>'


## ✅ **Verificação dos Dados do Webhook**

Sim, os dados principais do webhook estão **PERFEITOS**! ✅

### **Dados Confirmados:**
- ✅ **ID do destino**: `we_1RhCK1P3XTQ0qlpkkENLzs0l`
- ✅ **URL do endpoint**: `https://bwhale.site/webhook/stripe`
- ✅ **Versão da API**: `2025-03-31.manjericão`
- ✅ **Segredo da assinatura**: `whsec_IBYH8SrkEmay1AvbYgzBXOlmTaqeYLNb` (corresponde ao configurado no Render)
- ✅ **Evento**: `checkout.session.completed` (1 evento configurado)

**Tudo está correto e funcionando!** 🎯

---

## 🚀 **O que Precisa Subir Agora**

### **1. BACKEND (Render) - Atualizar Pasta `backend`**

Você precisa atualizar a pasta <mcfolder name="backend" path="c:\Nautilus Aut\back\backend"></mcfolder> no Render com as seguintes modificações:

#### **A. Atualizar o Modelo User**
```python
# backend/models/user.py
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from database import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # API keys criptografadas
    bitget_api_key_encrypted = db.Column(db.Text, nullable=True)
    bitget_api_secret_encrypted = db.Column(db.Text, nullable=True)
    bitget_passphrase_encrypted = db.Column(db.Text, nullable=True)
    
    # Status e configurações
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
    # 🆕 CAMPOS DE PAGAMENTO/ASSINATURA
    has_paid = db.Column(db.Boolean, default=False, nullable=False)
    subscription_type = db.Column(db.String(50), nullable=True)  # 'monthly' ou 'annual'
    subscription_start_date = db.Column(db.DateTime, nullable=True)
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True)
    
    # Integração Nautilus
    nautilus_token = db.Column(db.Text, nullable=True)
    nautilus_user_id = db.Column(db.Integer, nullable=True)
    nautilus_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Saldo operacional
    operational_balance = db.Column(db.Float, default=0.0)
    operational_balance_usd = db.Column(db.Float, default=0.0)
    last_conversion_rate = db.Column(db.Float, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Taxa de comissão personalizada
    commission_rate = db.Column(db.Float, default=0.35)

    # Relacionamento com trades
    trades = relationship('Trade', back_populates='user', lazy='dynamic', cascade="all, delete-orphan")

    def set_password(self, password):
        """Criptografa e define a senha do usuário usando Werkzeug."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha fornecida está correta usando Werkzeug."""
        return check_password_hash(self.password_hash, password)
    
    # 🆕 MÉTODO PARA VERIFICAR ASSINATURA ATIVA
    def is_subscription_active(self):
        """Verifica se a assinatura está ativa"""
        if not self.has_paid or not self.subscription_end_date:
            return False
        return datetime.utcnow() <= self.subscription_end_date
    
    def get_operational_balance_percentage(self):
        """Calcula a porcentagem do saldo operacional já utilizado"""
        try:
            from sqlalchemy import text
            result = db.session.execute(
                text("""
                    SELECT COALESCE(SUM(t.pnl * :commission_rate), 0) as total_commissions
                    FROM trades t 
                    WHERE t.user_id = :user_id 
                    AND t.status = 'closed' 
                    AND t.pnl > 0
                """),
                {
                    'user_id': self.id,
                    'commission_rate': self.commission_rate
                }
            ).fetchone()
            
            total_commissions = float(result[0]) if result and result[0] else 0.0
            current_balance = getattr(self, 'operational_balance_usd', 0.0) or 0.0
            initial_balance = current_balance + total_commissions
            
            if initial_balance <= 0:
                return 0.0
            
            percentage_used = (total_commissions / initial_balance) * 100
            return min(percentage_used, 100.0)
            
        except Exception as e:
            print(f"Erro ao calcular porcentagem do saldo operacional: {e}")
            return 0.0
    
    def can_open_new_positions(self):
        """Verifica se o usuário pode abrir novas posições"""
        try:
            if self.is_admin:
                return True
            
            usage_percentage = self.get_operational_balance_percentage()
            
            if usage_percentage >= 95.0:
                return False
            
            return True
            
        except Exception as e:
            print(f"Erro ao verificar se pode abrir posições: {e}")
            return False
    
    def get_remaining_balance_usd(self):
        """Calcula o saldo operacional restante em USD"""
        try:
            current_balance = getattr(self, 'operational_balance_usd', 0.0) or 0.0
            return max(current_balance, 0.0)
            
        except Exception as e:
            print(f"Erro ao calcular saldo restante: {e}")
            return 0.0
    
    def to_dict(self):
        """Converte o usuário para dicionário"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            # 🆕 NOVOS CAMPOS
            'has_paid': self.has_paid,
            'subscription_active': self.is_subscription_active(),
            'subscription_type': self.subscription_type,
            'subscription_end_date': self.subscription_end_date.isoformat() if self.subscription_end_date else None,
            # Campos existentes
            'nautilus_user_id': self.nautilus_user_id,
            'nautilus_active': self.nautilus_active,
            'operational_balance': self.operational_balance,
            'operational_balance_usd': self.operational_balance_usd,
            'commission_rate': self.commission_rate,
            'can_open_positions': self.can_open_new_positions(),
            'operational_balance_percentage': self.get_operational_balance_percentage(),
            'remaining_balance_usd': self.get_remaining_balance_usd()
        }

    def __repr__(self):
        return f'<User {self.email}>'