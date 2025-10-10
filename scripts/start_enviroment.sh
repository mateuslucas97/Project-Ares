#!/bin/bash

echo "=== ATIVANDO AMBIENTE VIRTUAL DO IDS ==="

# Navega para o diretório do projeto
cd ~/ids-project

# Verifica se o venv existe
if [ ! -d "ids-env" ]; then
    echo "❌ Ambiente virtual não encontrado. Criando..."
    python3 -m venv ids-env
fi

# Ativa o venv
source ids-env/bin/activate

echo "✅ Ambiente virtual ativado!"
echo "📁 Diretório: $(pwd)"
echo "🐍 Python: $(which python3)"
echo "📦 Pip: $(which pip)"

# Verifica dependências
echo "📋 Verificando dependências..."
pip list | grep -E "(flask|redis|requests|pandas)" || {
    echo "📥 Instalando dependências..."
    pip install flask redis requests pandas
}

echo ""
echo "🎯 Para executar o sistema:"
echo "   cd scripts/"
echo "   sudo python3 start_system.py"
echo ""
echo "🔍 Scripts disponíveis:"
ls -la scripts/*.py
