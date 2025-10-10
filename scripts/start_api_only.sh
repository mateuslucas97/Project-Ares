#!/bin/bash

# Ativa o ambiente virtual
source ../ids-env/bin/activate

echo "=== INICIANDO APENAS API ==="
echo "Python: $(which python3)"
echo "Usuário: $(whoami)"

# Executa a API sem sudo
python3 ids_api.py
