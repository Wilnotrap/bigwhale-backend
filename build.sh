#!/usr/bin/env bash
# Script de build para o Render

echo "=== INICIANDO BUILD PERSONALIZADO ==="

# Instalar psycopg2-binary explicitamente
echo "Instalando psycopg2-binary..."
pip install psycopg2-binary==2.9.9

# Instalar outras dependências
echo "Instalando dependências do requirements.txt..."
pip install -r requirements.txt

echo "=== BUILD CONCLUÍDO COM SUCESSO ==="