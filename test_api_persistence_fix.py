#!/usr/bin/env python3
"""
Teste para validar a correção do APIPersistence.__init__()
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_api_persistence_import():
    """Testa se a importação do APIPersistence funciona"""
    try:
        from utils.api_persistence import APIPersistence
        print("✅ Importação do APIPersistence: SUCESSO")
        return True
    except Exception as e:
        print(f"❌ Importação do APIPersistence: FALHA - {e}")
        return False

def test_api_persistence_init_without_args():
    """Testa se APIPersistence() funciona sem argumentos"""
    try:
        from utils.api_persistence import APIPersistence
        api_persistence = APIPersistence()
        print("✅ APIPersistence() sem argumentos: SUCESSO")
        print(f"   📁 Caminho do banco: {api_persistence.db_path}")
        return True
    except Exception as e:
        print(f"❌ APIPersistence() sem argumentos: FALHA - {e}")
        return False

def test_api_persistence_init_with_args():
    """Testa se APIPersistence(db_path) funciona com argumentos"""
    try:
        from utils.api_persistence import APIPersistence
        test_path = "/tmp/test.db"
        api_persistence = APIPersistence(test_path)
        print("✅ APIPersistence(db_path) com argumentos: SUCESSO")
        print(f"   📁 Caminho do banco: {api_persistence.db_path}")
        return True
    except Exception as e:
        print(f"❌ APIPersistence(db_path) com argumentos: FALHA - {e}")
        return False

def test_api_persistence_init_with_none():
    """Testa se APIPersistence(None) funciona"""
    try:
        from utils.api_persistence import APIPersistence
        api_persistence = APIPersistence(None)
        print("✅ APIPersistence(None): SUCESSO")
        print(f"   📁 Caminho do banco: {api_persistence.db_path}")
        return True
    except Exception as e:
        print(f"❌ APIPersistence(None): FALHA - {e}")
        return False

def test_backup_directory_creation():
    """Testa se o diretório de backup é criado corretamente"""
    try:
        from utils.api_persistence import APIPersistence
        api_persistence = APIPersistence()
        
        # Verificar se o diretório de backup existe
        backup_dir = api_persistence.backup_dir
        if os.path.exists(backup_dir):
            print("✅ Diretório de backup criado: SUCESSO")
            print(f"   📁 Diretório: {backup_dir}")
            return True
        else:
            print(f"❌ Diretório de backup não criado: {backup_dir}")
            return False
    except Exception as e:
        print(f"❌ Teste de diretório de backup: FALHA - {e}")
        return False

def run_all_tests():
    """Executa todos os testes"""
    print("🧪 TESTE DE VALIDAÇÃO - APIPersistence.__init__() CORREÇÃO")
    print("=" * 60)
    print()
    
    tests = [
        ("Importação", test_api_persistence_import),
        ("Inicialização sem argumentos", test_api_persistence_init_without_args),
        ("Inicialização com argumentos", test_api_persistence_init_with_args),
        ("Inicialização com None", test_api_persistence_init_with_none),
        ("Criação de diretório de backup", test_backup_directory_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"🔍 Executando teste: {test_name}")
        result = test_func()
        results.append(result)
        print()
    
    # Resumo
    print("📊 RESUMO DOS TESTES:")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASSOU" if results[i] else "❌ FALHOU"
        print(f"{status} - {test_name}")
    
    print()
    print(f"📈 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ A correção do APIPersistence.__init__() foi aplicada com sucesso!")
    else:
        print("⚠️ ALGUNS TESTES FALHARAM!")
        print("❌ A correção do APIPersistence.__init__() precisa ser revisada.")
    
    print()
    print("📞 VERIFICAÇÃO ADICIONAL:")
    print("Para confirmar a correção, verifique se todos os arquivos api_persistence.py")
    print("contêm a seguinte assinatura:")
    print("def __init__(self, db_path: str = None):")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 