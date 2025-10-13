
# 🛡️ Sistema IDS/IPS - SCPMSO

https://img.shields.io/badge/Python-3.8+-blue.svg

https://img.shields.io/badge/Flask-2.3+-green.svg

https://img.shields.io/badge/Suricata-8.0+-orange.svg

https://img.shields.io/badge/License-MIT-yellow.svg

Sistema completo de Detecção e Prevenção de Intrusões (IDS/IPS) desenvolvido para monitoramento e segurança de redes corporativas.




## 📋 Índice
•	Visão Geral

•	Funcionalidades

•	Arquitetura

•	Instalação

•	Uso

•	Documentação

•	Desenvolvimento

## 🎯 Visão Geral

Sistema IDS/IPS desenvolvido para a SCPMSO com foco em:

•	Monitoramento em tempo real de redes corporativas

•	Detecção proativa de ameaças e intrusões

•	Prevenção automática através de bloqueio de IPs maliciosos

•	Dashboard web intuitivo para gestão e visualização

## 🚀 Funcionalidades Principais

🎨 Dashboard Web -> Interface moderna e responsiva com Bootstrap 5

📊 Monitoramento -> Gráficos em tempo real com Chart.js

🛡️ Detecção -> Integração com Suricata para análise de tráfego

🔍 Análise -> Correlação de eventos com Zeek (Bro)

⚡ Prevenção -> Bloqueio automático e manual de IPs

📈 Histórico -> Busca e filtros avançados em eventos

🔔 Notificações -> Sistema de alertas em tempo real


## 🏗️ Arquitetura do Sistema

<img width="1939" height="1946" alt="Diagrama-IDS-IPS-1" src="https://github.com/user-attachments/assets/09055756-1978-45fc-b93c-72804c979e61" />


## Stack Tecnológica

•	Backend: Python 3.8+, Flask

•	IDS/IPS: Suricata 8.0+

•	Análise de Rede: Zeek 4.0+

•	Frontend: Bootstrap 5, Chart.js

•	Banco de Dados: SQLite

•	Monitoramento: API REST personalizada

## ⚡ Instalação Rápida

Pré-requisitos

Ubuntu/Debian/Kali Linux

sudo apt update

sudo apt install python3 python3-pip python3-venv suricata zeek

## 🛠️ Configuração do Sistema

1. Clonar repositório

git clone https://github.com/mateuslucas97/IDS-IPS-System.git

cd IDS-IPS-System

2. Configurar ambiente virtual

python3 -m venv ids-env

source ids-env/bin/activate

3. Instalar dependências

pip install -r requirements.txt

4. Configurar diretórios

sudo mkdir -p /opt/ids

sudo chown $USER:$USER /opt/ids

5. Configurar permissões de rede

sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/suricata

sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/zeek

## Configuração do Suricata

Edite /etc/suricata/suricata.yaml:

vars:
  address-groups:
    HOME_NET: "[SUA_REDE_CORPORATIVA_AQUI]"
    
af-packet:
  - interface: eth0
    cluster-id: 99
    cluster-type: cluster_flow

## 🚀 Uso do Sistema

## Inicialização

Ambiente virtual

source ids-env/bin/activate

Dashboard completo

cd src

python3 ids_dashboard_completo.py

## 📊 Acesso ao Dashboard

•	URL Principal: http://localhost:5001

•	URL Rede: http://[SEU_IP]:5001

## 🎯 Funcionalidades do Dashboard

1. Visão Geral
•	Cards de status em tempo real

•	Métricas de alertas e bloqueios

•	Indicador de saúde do sistema

2. Gráficos em Tempo Real
•	Tráfego de rede (packets/segundo)

•	Distribuição de severidade de alertas

•	Atualização automática configurável

3. Gestão de Alertas

# Filtros disponíveis
- Por severidade (Crítico, Alto, Médio, Baixo)
- Por período (1h, 24h, 1 semana, 1 mês)
- Busca textual em tempo real

4. Controles de Segurança

•	Bloqueio manual de IPs

•	Desbloqueio com um clique

•	Configuração de limiares automáticos

## 🔧 API REST

Estatísticas do sistema

curl http://localhost:5001/api/stats

Alertas recentes

curl http://localhost:5001/api/alerts/today

IPs bloqueados

curl http://localhost:5001/api/ips/blocked

Endpoints Principais:

•	GET /api/stats - Métricas do sistema

•	GET /api/alerts/today - Alertas do dia

•	POST /api/ips/block - Bloquear IP

•	GET /api/traffic - Dados de tráfego


## 📁 Estrutura do Projeto

IDS-IPS-System/
├── src/                    # Código fonte principal

│   ├── ids_dashboard_completo.py    # Dashboard web

│   ├── log_processor.py             # Processador de logs

│   ├── zeek_integrator.py           # Integrador Zeek

│   └── start_system.py              # Orquestrador

├── scripts/               # Scripts de suporte

├── docs/                 # Documentação técnica

├── configs/              # Arquivos de configuração

├── requirements.txt      # Dependências Python

├── LICENSE              # Licença MIT

└── README.md           # Este arquivo

## 🛠️ Desenvolvimento

Scripts Funcionais

ids_dashboard_completo.py -> Dashboard web completo

log_processor.py -> Processamento de logs do Suricata

zeek_integrator.py -> Integração com análise Zeek

start_system.py -> Inicialização coordenada

## 🔍 Monitoramento e Debug

Verificar serviços

./scripts/diagnose_system.sh

Logs do Suricata

tail -f /var/log/suricata/eve.json

Status da API

curl http://localhost:5001/api/stats

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Fork o projeto

2. Crie uma branch: git checkout -b feature/nova-funcionalidade

3. Commit suas mudanças: git commit -m 'Adiciona nova funcionalidade'

4. Push para a branch: git push origin feature/nova-funcionalidade

5. Abra um Pull Request

## 📝 Padrões de Commit

•	feat: Nova funcionalidade

•	fix: Correção de bugs

•	docs: Documentação

•	style: Formatação

•	refactor: Refatoração de código


## 🐛 Solução de Problemas

Problemas Comuns

Dashboard não carrega -> Verificar porta 5001 e processo Python
Sem dados nos gráficos -> Checar banco SQLite e logs do Suricata
Bloqueio não funciona -> Verificar permissões iptables
Erro de importação -> Reativar ambiente virtual

Logs Importantes

•	Application: Terminal de execução

•	Suricata: /var/log/suricata/eve.json

•	Zeek: /opt/zeek/logs/current/

•	Database: /opt/ids/network_data.db

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## 👨‍💻 Autor

Mateus Lucas Cassimiro

•	GitHub: @mateuslucas97

•	Desenvolvido para SCPMSO

## 🙏 Agradecimentos

•	Equipe Suricata pelo excelente IDS/IPS

•	Equipe Zeek pela análise de tráfego avançada

•	Comunidade Flask pelo framework web

•	SCPMSO pelo apoio ao desenvolvimento

⭐ Se este projeto foi útil, considere dar uma estrela no repositório!


Última atualização: Outubro 2024
*Versão: 2.0 - Dashboard Completo*
