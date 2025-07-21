#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inicializar códigos de convite
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from database import db
from models.invite_code import initialize_invite_codes, InviteCode

def create_app():
    """Cria aplicação Flask para inicialização"""
    app = Flask(__name__)
    
    # Configuração básica
    app.config['SECRET_KEY'] = 'uma-chave-secreta-bem-dificil-de-adivinhar-987654'
    db_path = os.path.join(os.getcwd(), 'backend', 'instance', 'site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app

def init_codes():
    """Inicializa códigos de convite"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🎫 Inicializando códigos de convite...")
            print("=" * 50)
            
            # Inicializar códigos
            initialize_invite_codes(app)
            
            # Verificar códigos criados
            print("\n📋 Códigos disponíveis:")
            codes = InviteCode.query.all()
            
            for code in codes:
                status = f"{code.used_count}/{code.max_uses or '∞'}"
                print(f"   {code.code} - {code.description} - Usos: {status}")
            
            # Verificar especificamente o código Bigwhale81#
            bigwhale_code = InviteCode.query.filter_by(code='Bigwhale81#').first()
            if bigwhale_code:
                print(f"\n✅ Código 'Bigwhale81#' configurado:")
                print(f"   Descrição: {bigwhale_code.description}")
                print(f"   Máximo usos: {bigwhale_code.max_uses}")
                print(f"   Usos atuais: {bigwhale_code.used_count}")
                print(f"   Pode ser usado: {'Sim' if bigwhale_code.can_be_used() else 'Não'}")
                print(f"   Criado em: {bigwhale_code.created_at}")
            else:
                print("❌ Código 'Bigwhale81#' não foi criado!")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = init_codes()
    
    if success:
        print("\n✅ Códigos de convite inicializados!")
    else:
        print("\n❌ Erro na inicialização!")