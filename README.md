SISTEMA IDS/IPS PARA A SCPMSO 

Autor: Mateus Lucas Cassimiro 

Documentação: Este arquivo 

 

Visão Geral 

Objetivo 

Sistema de Detecção e Prevenção de Intrusões (IDS/IPS) para monitoramento de redes internas corporativas da SCPMSO. 

 

Redes Monitoradas 

10.16.90.0/24 - Rede principal 

10.16.91.0/24 - Rede de enlace (Firewall: 10.16.91.2) 

10.16.89.0/24 - Rede de gerência de equipamentos e de tráfego de Voz (VoIP) 

10.16.85.0/24 - Rede Wi-Fi corporativa 

10.16.83.0/24 - Rede Wi-Fi Visitantes 

 

Tecnologias Utilizadas 

Suricata – IDS/IPS 

Zeek - Análise de tráfego de rede 

Elastic Stack – Kibana, Logstash 

Python - integração e automação 

SQLite – Armazenamento de eventos 

Flask – API web 

 

Arquitetura do Sistema 

[Redes Monitoradas] 

        ↓ 

[Suricata + Zeek] → Coleta de tráfego 

        ↓ 

[Scripts Python] → Processamento e correlação 

        ↓ 

[SQLite DB] ←→ [API Flask] ←→ [Kibana] 

        ↓ 

[Alertas/Ações] → Bloqueio automático 

Fluxo de Dados 

Coleta: suricata e zeek monitoram interface eth0 

Processamento: scripts Python correlacionam eventos 

Armazenamento: SQLite para dados estruturados 

Visualização: Kibana para dashboards 

Ação: Bloqueio automático via iptables 

 

Configuração da Rede 

Arquivo Suricata (/etc/suricata/suricata.yaml) 

vars: 

  address-groups:           HOME_NET:”[#Insira os IPs que serão monitorados]" 

 

Interface de Monitoramento 

Interface: eth0 

Modo: AF_PACKET (alta performance) 

Cluster: cluster_flow para balanceamento 

 

Instalação e SETUP 

Estrutura de Diretórios 

~/ids-project/ 
├── ids-env/                                                     # Ambiente virtual Python 
├── scripts/                                                      # Scripts do sistema 
│   ├── ids_dashboard_completo.py    # Dashboard principal 
│   ├── log_processor.py                            # Processador de logs 
│   ├── zeek_integrator.py                         # Integrador Zeek 
│   ├── start_system.py                              # Inicializador do sistema 
│   └── start_ids.sh                                        # Script de ativação 
└── configs/                                                     # Configurações 

 

Comandos de Instalação 

1. Criar ambiente virtual 

cd ~/ids-project python3 -m venv ids-env 

2. Ativar ambiente virtual 

source ids-env/bin/activate 

3. Instalar dependências 

pip install flask redis requests pandas 

4. Configurar diretórios 

sudo mkdir -p /opt/ids sudo chown $USER:$USER /opt/ids 

5. Configurar permissões 

sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/suricata sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/zeek 

 

Scripts e API 

Script Principal: ids_dashboard_completo.py 

Função: Dashboard web completo com API REST 

Endpoints da API: 

GET / - Interface web principal 

GET /api/stats - Estatísticas do sistema 

GET /api/traffic - Dados de tráfego para gráficos 

GET /api/history - Histórico de eventos 

GET /api/alerts/today - Alertas com filtros 

GET /api/ips/blocked - IPs bloqueados 

POST /api/ips/block - Bloquear IP 

POST /api/ips/unblock - Desbloquear IP 

GET/POST /api/settings - Configurações do sistema 

Scripts de Suporte 

log_processor.py 

Processamento em tempo real de logs do Suricata 

Bloqueio automático de IPs maliciosos 

Armazenamento em banco SQLite 

zeek_integrator.py 

Integração e correlação com logs do Zeek 

Processamento periódico de logs 

Enriquecimento de dados de alertas 

start_system.py 

Orquestrador do sistema completo 

Inicialização coordenada de serviços 

Gestão de processos 

 

Operação e Monitoramento 

Inicialização do Sistema 

# Método 1: Sistema completo 

cd ~/ids-project/scripts ./start_ids.sh 

# Método 2: Apenas dashboard 

cd ~/ids-project/scripts source ../ids-env/bin/activate python3 ids_dashboard_completo.py 

# Método 3: Sistema com orquestração 

sudo ../ids-env/bin/python3 start_system.py 

 

Verificação de Serviços 

# API/Dashboard respondendo? 

curl http://localhost:5001/api/stats 

# Suricata rodando? 

pgrep suricata 

# Zeek rodando? 

pgrep zeek 

# Ver logs em tempo real 

tail -f /var/log/suricata/eve.json 

 

Comandos úteis de Gestão 

# Ver IPs bloqueados 

sudo iptables -L INPUT -n --line-numbers 

# Desbloquear IP específico 

sudo iptables -D INPUT -s IP_BLOQUEADO -j DROP 

# Ver espaço em disco do banco 

du -h /opt/ids/network_data.db 

 

Monitoramento via API 

Estatísticas do sistema 

curl http://localhost:5000/stats | jq 

Alertas de hoje 

curl http://localhost:5000/alerts/today | jq 

IPs bloqueados 

curl http://localhost:5000/ips/blocked | jq 

 

Interface Web Dashboard 

Acesso 

URL Principal: http://10.16.90.128:5001 

URL Alternativas: 

http://localhost:5001 

http://127.0.0.1:5001 

 

Seções do Dashboard 

Cards de Status 

Total de Alertas: Contador geral de alertas detectados 

Alertas Críticos: Alertas com severidade alta (≥3) 

IPs Bloqueados: Número de IPs atualmente bloqueados 

Status do Sistema: Indicador online/offline 

Gráficos em Tempo Real 

Gráfico de Linha: Tráfego de rede (packets/segundo) 

Botões: Alternar tipo (linha/barra), Download 

Gráfico de Pizza: Distribuição de alertas por severidade 

Controles Rápidos 

Bloqueio Manual: Campo para inserir IP + botão de bloqueio 

Exportação: Botão para exportar dados do sistema 

Limpeza: Remoção de dados antigos 

Busca e Filtros 

Busca em Tempo Real: Pesquisa textual em alertas 

Filtro por Severidade: Crítico, Alto, Médio, Baixo 

Filtro por Período: 1h, 24h, 1 semana, 1 mês 

Abas de Conteúdo 

Alertas Recentes: Lista detalhada com ações rápidas 

Histórico: Tabela com timeline de eventos 

IPs Bloqueados: Lista de IPs bloqueados com opção de desbloqueio 

Configurações (Modal) 

Bloqueio Automático: Ativa/desativa bloqueio automático 

Limiar de Alerta: Define nível mínimo para alertas 

Intervalo de Atualização: 5-300 segundos 

Notificações: Controla sistema de notificações 

 

Monitoramento via Dashboard 

Acesse http://10.16.90.128:5001 

Verifique os cards de status 

Analise gráficos em tempo real 

Revise alertas recentes na aba correspondente 

Configure sistema conforme necessidade 

 

Solução de Problemas 

Problemas Comuns e Soluções 

Dashboard Não Acessível 

# Verificar se processo está rodando 
ps aux | grep ids_dashboard_completo 
 
# Verificar porta 
netstat -tulpn | grep :5001 
 
# Reiniciar dashboard 
sudo fuser -k 5001/tcp 
python3 ids_dashboard_completo.py 

Sem Dados nos Gráficos 

# Verificar banco de dados 
ls -la /opt/ids/network_data.db 
 
# Verificar se Suricata está gerando logs 
tail -f /var/log/suricata/eve.json 
 
# Verificar permissões 
sudo chown $USER:$USER /opt/ids/network_data.db 

Bloqueio de IPs Não Funciona 

# Verificar permissões iptables 
sudo iptables -L 
 
# Testar bloqueio manual 
sudo iptables -A INPUT -s 192.168.1.100 -j DROP 
 
# Verificar se usuário tem permissão 
groups $USER 

Erro de Ambiente Virtual 

# Verificar se venv está ativado 
which python3 
# Deve mostrar: ~/ids-project/ids-env/bin/python3 
 
# Reativar venv 
source ~/ids-project/ids-env/bin/activate 

 

Logs Importantes 

Dashboard: Output do terminal onde foi executado 

Suricata: /var/log/suricata/eve.json 

Zeek: /opt/zeek/logs/current/ 

Banco de Dados: /opt/ids/network_data.db 

Sistema: Mensagens no dashboard web 

 

Script de Diagnóstico 

~/ids-project/scripts/diagnose_system.sh 

#!/bin/bash 
echo "=== DIAGNÓSTICO DO SISTEMA IDS/IPS ===" 
echo "1. Processos:" 
ps aux | grep -E "(suricata|zeek|python)" | grep -v grep 
echo -e "\n2. Porta 5001:" 
netstat -tulpn | grep :5001 || echo "Porta não em uso" 
echo -e "\n3. Banco de dados:" 
ls -la /opt/ids/network_data.db 2>/dev/null || echo "Banco não encontrado" 
echo -e "\n4. Teste API:" 
curl -s http://localhost:5001/api/stats | head -2 || echo "API offline" 
echo -e "\n=== FIM DO DIAGNÓSTICO ===" 

 

Status do Sistema 

Funcionalidades Operacionais 

Dashboard web completo e responsivo 

Gráficos em tempo real funcionando 

Sistema de notificações ativo 

Busca e filtros operacionais 

Configurações do sistema funcionais 

Bloqueio manual/automático de IPs 

Acesso 

Dashboard: http://10.16.90.128:5001 ✅ OPERACIONAL 

API REST: http://10.16.90.128:5001/api/ ✅ OPERACIONAL 

Métricas de Performance 

Tempo de resposta: < 500ms 

Atualização automática: 30 segundos 

Capacidade de alertas: 10.000+ registros 

Suporte a usuários: Múltiplos simultâneos 

 

Conclusão 

Sistema IDS/IPS completo e em produção!  

O sistema agora oferece: 

Monitoramento em tempo real de 5 redes internas 

Dashboard web moderno e intuitivo 

Gráficos e visualizações em tempo real 

Sistema completo de detecção e prevenção 

Controles administrativos via interface web 

Notificações e alertas em tempo real 

Histórico completo e busca avançada 

Configurações flexíveis do sistema 

 

Status atual: OPERACIONAL E FUNCIONANDO 

 
