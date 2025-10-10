#!/bin/bash

# Ativa o ambiente virtual
source ../ids-env/bin/activate

echo "=== INICIANDO SISTEMA IDS/IPS ==="
echo "Python: $(which python3)"

# Executa o sistema com o Python do venv
sudo ../ids-env/bin/python3 start_system.py
