#!/usr/bin/env python3
from flask import Flask, jsonify, request, render_template_string
import sqlite3
import subprocess
from datetime import datetime, timedelta
import socket
import json
import random

app = Flask(__name__)

# Armazenamento em memória para gráficos
system_settings = {
    'auto_block': True,
    'alert_threshold': 2,
    'update_interval': 30,
    'notifications': True
}

# ========== HTML TEMPLATE COMPLETO ==========
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IDS/IPS Dashboard Avançado</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary: #667eea;
            --secondary: #764ba2;
            --success: #28a745;
            --warning: #ffc107;
            --danger: #dc3545;
            --dark: #343a40;
        }
        
        body { 
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .navbar { 
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .card { 
            border: none; 
            border-radius: 15px; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            transition: transform 0.3s ease;
            background: white;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .stat-card { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .alert-critical { border-left: 5px solid var(--danger); background: #fff5f5; }
        .alert-high { border-left: 5px solid var(--warning); background: #fffbf0; }
        .alert-medium { border-left: 5px solid #17a2b8; background: #f0f9ff; }
        .alert-low { border-left: 5px solid var(--success); background: #f0fff4; }
        
        .refresh-btn { 
            cursor: pointer; 
            transition: transform 0.3s ease; 
            border: none;
            background: transparent;
        }
        
        .refresh-btn:hover { transform: rotate(180deg); }
        
        .nav-tabs .nav-link.active {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            border: none;
            border-radius: 10px;
        }
        
        .notification-badge {
            position: absolute;
            top: -5px;
            right: -5px;
            background: var(--danger);
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            width: 100%;
        }
        
        .search-box {
            border-radius: 25px;
            border: 2px solid #e9ecef;
            padding: 10px 20px;
        }
        
        .settings-panel {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
        }
        
        .switch {
            position: relative;
            display: inline-block;
            width: 60px;
            height: 34px;
        }
        
        .switch input { 
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }
        
        .slider:before {
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        
        input:checked + .slider {
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        }
        
        input:checked + .slider:before {
            transform: translateX(26px);
        }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark sticky-top">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-shield-alt"></i> <strong>IDS/IPS Dashboard</strong>
            </a>
            <div class="navbar-nav ms-auto">
                <div class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                        <i class="fas fa-cog"></i> Configurações
                    </a>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="#" onclick="showSettings()"><i class="fas fa-sliders-h"></i> Configurações</a></li>
                        <li><a class="dropdown-item" href="#" onclick="showNotifications()">
                            <i class="fas fa-bell"></i> Notificações
                            <span class="notification-badge" id="notification-count">0</span>
                        </a></li>
                    </ul>
                </div>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Status Cards -->
        <div class="row">
            <div class="col-md-3">
                <div class="stat-card">
                    <h3><i class="fas fa-bell"></i></h3>
                    <h2 id="total-alerts">0</h2>
                    <p>Total de Alertas</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card" style="background: linear-gradient(135deg, #fd7e14 0%, #f76707 100%);">
                    <h3><i class="fas fa-exclamation-triangle"></i></h3>
                    <h2 id="high-alerts">0</h2>
                    <p>Alertas Críticos</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card" style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);">
                    <h3><i class="fas fa-ban"></i></h3>
                    <h2 id="blocked-ips">0</h2>
                    <p>IPs Bloqueados</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
                    <h3><i class="fas fa-check-circle"></i></h3>
                    <h2 id="status">Online</h2>
                    <p>Status do Sistema</p>
                </div>
            </div>
        </div>

        <!-- Gráficos -->
        <div class="row mt-4">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0"><i class="fas fa-chart-line"></i> Tráfego em Tempo Real</h5>
                        <div>
                            <button class="btn btn-sm btn-outline-primary me-2" onclick="toggleTrafficChart()">
                                <i class="fas fa-sync-alt"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-secondary" onclick="downloadChart()">
                                <i class="fas fa-download"></i>
                            </button>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="trafficChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-chart-pie"></i> Distribuição de Alertas</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="alertChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Controles e Busca -->
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-cogs"></i> Controles Rápidos</h5>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-12 mb-3">
                                <label class="form-label">Bloquear IP Manualmente</label>
                                <div class="input-group">
                                    <input type="text" id="ip-to-block" class="form-control" placeholder="Ex: 192.168.1.100">
                                    <button class="btn btn-danger" onclick="blockIP()">
                                        <i class="fas fa-ban"></i> Bloquear
                                    </button>
                                </div>
                            </div>
                            <div class="col-12">
                                <label class="form-label">Configurações Rápidas</label>
                                <div class="d-grid gap-2">
                                    <button class="btn btn-outline-warning" onclick="exportData()">
                                        <i class="fas fa-file-export"></i> Exportar Dados
                                    </button>
                                    <button class="btn btn-outline-info" onclick="clearOldData()">
                                        <i class="fas fa-broom"></i> Limpar Dados Antigos
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-search"></i> Busca e Filtros</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <input type="text" id="search-alerts" class="form-control search-box" 
                                   placeholder="🔍 Buscar em alertas...">
                        </div>
                        <div class="row">
                            <div class="col-6">
                                <select class="form-select" id="severity-filter">
                                    <option value="">Todas Severidades</option>
                                    <option value="3">Crítico</option>
                                    <option value="2">Alto</option>
                                    <option value="1">Médio</option>
                                    <option value="0">Baixo</option>
                                </select>
                            </div>
                            <div class="col-6">
                                <select class="form-select" id="time-filter">
                                    <option value="1">Última Hora</option>
                                    <option value="24">Últimas 24h</option>
                                    <option value="168">Última Semana</option>
                                    <option value="720">Último Mês</option>
                                </select>
                            </div>
                        </div>
                        <button class="btn btn-primary w-100 mt-3" onclick="applyFilters()">
                            <i class="fas fa-filter"></i> Aplicar Filtros
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Alertas e Histórico -->
        <div class="row mt-4">
            <div class="col-12">
                <ul class="nav nav-tabs" id="myTab" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="alerts-tab" data-bs-toggle="tab" data-bs-target="#alerts" type="button">
                            <i class="fas fa-list"></i> Alertas Recentes
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="history-tab" data-bs-toggle="tab" data-bs-target="#history" type="button">
                            <i class="fas fa-history"></i> Histórico
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="blocked-tab" data-bs-toggle="tab" data-bs-target="#blocked" type="button">
                            <i class="fas fa-ban"></i> IPs Bloqueados
                        </button>
                    </li>
                </ul>
                
                <div class="tab-content" id="myTabContent">
                    <!-- Alertas Recentes -->
                    <div class="tab-pane fade show active" id="alerts" role="tabpanel">
                        <div class="card">
                            <div class="card-body">
                                <div id="alerts-container">
                                    <div class="text-center text-muted py-4">
                                        <i class="fas fa-spinner fa-spin fa-2x"></i>
                                        <p class="mt-2">Carregando alertas...</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Histórico -->
                    <div class="tab-pane fade" id="history" role="tabpanel">
                        <div class="card">
                            <div class="card-body">
                                <div id="history-container">
                                    <div class="text-center text-muted py-4">
                                        <i class="fas fa-spinner fa-spin fa-2x"></i>
                                        <p class="mt-2">Carregando histórico...</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- IPs Bloqueados -->
                    <div class="tab-pane fade" id="blocked" role="tabpanel">
                        <div class="card">
                            <div class="card-body">
                                <div id="blocked-ips-container">
                                    <div class="text-center text-muted py-4">
                                        <i class="fas fa-spinner fa-spin fa-2x"></i>
                                        <p class="mt-2">Carregando IPs bloqueados...</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal de Configurações -->
    <div class="modal fade" id="settingsModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title"><i class="fas fa-sliders-h"></i> Configurações do Sistema</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="settings-panel">
                        <div class="mb-3">
                            <label class="form-label">Bloqueio Automático</label>
                            <div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" id="auto-block" checked>
                                <label class="form-check-label" for="auto-block">Bloquear IPs automaticamente</label>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Limiar de Alerta</label>
                            <select class="form-select" id="alert-threshold">
                                <option value="1">Baixo</option>
                                <option value="2" selected>Médio</option>
                                <option value="3">Alto</option>
                                <option value="4">Crítico</option>
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Intervalo de Atualização (segundos)</label>
                            <input type="number" class="form-control" id="update-interval" value="30" min="5" max="300">
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Notificações</label>
                            <div class="form-check form-switch">
                                <input class="form-check-input" type="checkbox" id="notifications-enabled" checked>
                                <label class="form-check-label" for="notifications-enabled">Ativar notificações</label>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fechar</button>
                    <button type="button" class="btn btn-primary" onclick="saveSettings()">Salvar Configurações</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast para Notificações -->
    <div class="toast-container position-fixed top-0 end-0 p-3">
        <div id="liveToast" class="toast" role="alert">
            <div class="toast-header">
                <i class="fas fa-bell text-primary me-2"></i>
                <strong class="me-auto">IDS/IPS Notification</strong>
                <small>agora</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body" id="toast-message">
                Hello, world! This is a toast message.
            </div>
        </div>
    </div>

    <!-- JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Variáveis globais
        let trafficChart, alertChart;
        let currentFilters = {};
        let notificationCount = 0;

        // Inicialização dos gráficos
        function initializeCharts() {
            // Gráfico de tráfego
            const trafficCtx = document.getElementById('trafficChart').getContext('2d');
            trafficChart = new Chart(trafficCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Tráfego (packets/s)',
                        data: [],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: 'rgba(0,0,0,0.1)' }
                        },
                        x: {
                            grid: { display: false }
                        }
                    }
                }
            });

            // Gráfico de alertas
            const alertCtx = document.getElementById('alertChart').getContext('2d');
            alertChart = new Chart(alertCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Crítico', 'Alto', 'Médio', 'Baixo'],
                    datasets: [{
                        data: [0, 0, 0, 0],
                        backgroundColor: [
                            '#dc3545',
                            '#fd7e14', 
                            '#ffc107',
                            '#20c997'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });
        }

        // Carregar dados
        async function loadData() {
            try {
                // Carrega estatísticas
                const statsResponse = await fetch('/api/stats');
                const stats = await statsResponse.json();
                
                document.getElementById('total-alerts').textContent = stats.total_alerts;
                document.getElementById('high-alerts').textContent = stats.high_severity_alerts;
                document.getElementById('blocked-ips').textContent = stats.blocked_ips;
                document.getElementById('status').textContent = 'Online';

                // Atualiza gráfico de alertas
                updateAlertChart(stats);

                // Carrega dados de tráfego
                const trafficResponse = await fetch('/api/traffic');
                const traffic = await trafficResponse.json();
                updateTrafficChart(traffic);

                // Carrega alertas
                await loadAlerts();
                
                // Carrega histórico
                await loadHistory();
                
                // Carrega IPs bloqueados
                await loadBlockedIPs();

            } catch (error) {
                console.error('Erro ao carregar dados:', error);
                showNotification('Erro ao carregar dados do sistema', 'error');
            }
        }

        // Atualizar gráfico de tráfego
        function updateTrafficChart(trafficData) {
            if (!trafficChart) return;
            
            const labels = trafficData.map(item => {
                const date = new Date(item.timestamp);
                return date.toLocaleTimeString();
            });
            
            const data = trafficData.map(item => item.packets_per_second);
            
            trafficChart.data.labels = labels;
            trafficChart.data.datasets[0].data = data;
            trafficChart.update('none');
        }

        // Atualizar gráfico de alertas
        function updateAlertChart(stats) {
            if (!alertChart) return;
            
            // Simula distribuição de alertas (em produção viria da API)
            const alertDistribution = [
                Math.min(stats.high_severity_alerts || 0, 10), // Crítico
                Math.min(stats.total_alerts * 0.3 || 0, 15),   // Alto
                Math.min(stats.total_alerts * 0.4 || 0, 20),   // Médio
                Math.min(stats.total_alerts * 0.3 || 0, 25)    // Baixo
            ];
            
            alertChart.data.datasets[0].data = alertDistribution;
            alertChart.update();
        }

        // Carregar alertas com filtros
        async function loadAlerts() {
            try {
                let url = '/api/alerts/today';
                const params = new URLSearchParams();
                
                if (currentFilters.search) {
                    params.append('search', currentFilters.search);
                }
                if (currentFilters.severity) {
                    params.append('severity', currentFilters.severity);
                }
                if (currentFilters.hours) {
                    params.append('hours', currentFilters.hours);
                }
                
                if (params.toString()) {
                    url += '?' + params.toString();
                }
                
                const response = await fetch(url);
                const alerts = await response.json();
                
                displayAlerts(alerts);
            } catch (error) {
                console.error('Erro ao carregar alertas:', error);
            }
        }

        // Exibir alertas na interface
        function displayAlerts(alerts) {
            const container = document.getElementById('alerts-container');
            
            if (!alerts || alerts.length === 0) {
                container.innerHTML = `
                    <div class="text-center text-muted py-4">
                        <i class="fas fa-check-circle fa-2x text-success"></i>
                        <p class="mt-2">Nenhum alerta encontrado</p>
                    </div>
                `;
                return;
            }

            let html = '';
            alerts.slice(0, 20).forEach(alert => {
                const severity = alert.severity || 1;
                const severityClass = severity >= 3 ? 'alert-critical' : 
                                    severity >= 2 ? 'alert-high' : 
                                    severity >= 1 ? 'alert-medium' : 'alert-low';
                
                const severityText = severity >= 3 ? 'Crítico' : 
                                   severity >= 2 ? 'Alto' : 
                                   severity >= 1 ? 'Médio' : 'Baixo';
                
                const severityColor = severity >= 3 ? 'danger' : 
                                    severity >= 2 ? 'warning' : 
                                    severity >= 1 ? 'info' : 'success';

                html += `
                    <div class="alert ${severityClass} mb-3 p-3">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <div class="d-flex align-items-center mb-2">
                                    <span class="badge bg-${severityColor} me-2">${severityText}</span>
                                    <strong class="me-2">${alert.signature || 'Alerta de Segurança'}</strong>
                                    <small class="text-muted">ID: ${alert.alert_id || 'N/A'}</small>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <small class="text-muted">
                                            <i class="fas fa-location-arrow"></i> <strong>Origem:</strong> ${alert.src_ip || 'N/A'}
                                        </small>
                                    </div>
                                    <div class="col-md-6">
                                        <small class="text-muted">
                                            <i class="fas fa-bullseye"></i> <strong>Destino:</strong> ${alert.dest_ip || 'N/A'}
                                        </small>
                                    </div>
                                </div>
                                ${alert.description ? `
                                    <div class="mt-2">
                                        <small class="text-muted">${alert.description}</small>
                                    </div>
                                ` : ''}
                            </div>
                            <div class="text-end ms-3">
                                <small class="text-muted d-block">
                                    <i class="fas fa-clock"></i> ${new Date(alert.timestamp).toLocaleString()}
                                </small>
                                <div class="mt-2">
                                    <button class="btn btn-sm btn-outline-danger" onclick="blockIPManual('${alert.src_ip}')">
                                        <i class="fas fa-ban"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            container.innerHTML = html;
        }

        // Carregar histórico
        async function loadHistory() {
            try {
                const response = await fetch('/api/history');
                const history = await response.json();
                displayHistory(history);
            } catch (error) {
                console.error('Erro ao carregar histórico:', error);
            }
        }

        // Exibir histórico
        function displayHistory(history) {
            const container = document.getElementById('history-container');
            
            if (!history || history.length === 0) {
                container.innerHTML = `
                    <div class="text-center text-muted py-4">
                        <i class="fas fa-history fa-2x"></i>
                        <p class="mt-2">Nenhum dado histórico</p>
                    </div>
                `;
                return;
            }

            let html = '<div class="table-responsive"><table class="table table-striped"><thead><tr><th>Data/Hora</th><th>Evento</th><th>IP</th><th>Ação</th></tr></thead><tbody>';
            
            history.slice(0, 15).forEach(item => {
                html += `
                    <tr>
                        <td><small>${new Date(item.timestamp).toLocaleString()}</small></td>
                        <td>${item.event_type || 'Alerta'}</td>
                        <td><code>${item.src_ip || 'N/A'}</code></td>
                        <td><span class="badge bg-${item.action === 'blocked' ? 'danger' : 'warning'}">${item.action || 'detected'}</span></td>
                    </tr>
                `;
            });
            
            html += '</tbody></table></div>';
            container.innerHTML = html;
        }

        // Carregar IPs bloqueados
        async function loadBlockedIPs() {
            try {
                const response = await fetch('/api/ips/blocked');
                const data = await response.json();
                displayBlockedIPs(data.blocked_ips || []);
            } catch (error) {
                console.error('Erro ao carregar IPs bloqueados:', error);
            }
        }

        // Exibir IPs bloqueados
        function displayBlockedIPs(blockedIPs) {
            const container = document.getElementById('blocked-ips-container');
            
            if (!blockedIPs || blockedIPs.length === 0) {
                container.innerHTML = `
                    <div class="text-center text-muted py-4">
                        <i class="fas fa-check-circle fa-2x text-success"></i>
                        <p class="mt-2">Nenhum IP bloqueado</p>
                    </div>
                `;
                return;
            }

            let html = '';
            blockedIPs.forEach((rule, index) => {
                // Extrai IP da regra iptables
                const ipMatch = rule.match(/[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+/);
                const ip = ipMatch ? ipMatch[0] : 'IP não identificado';
                
                html += `
                    <div class="alert alert-danger d-flex justify-content-between align-items-center">
                        <div>
                            <i class="fas fa-ban me-2"></i>
                            <strong>${ip}</strong>
                            <small class="text-muted ms-2">${rule}</small>
                        </div>
                        <button class="btn btn-sm btn-outline-success" onclick="unblockIP('${ip}')">
                            <i class="fas fa-unlock"></i> Desbloquear
                        </button>
                    </div>
                `;
            });
            
            container.innerHTML = html;
        }

        // Aplicar filtros
        function applyFilters() {
            currentFilters = {
                search: document.getElementById('search-alerts').value,
                severity: document.getElementById('severity-filter').value,
                hours: document.getElementById('time-filter').value
            };
            
            loadAlerts();
            showNotification('Filtros aplicados com sucesso', 'success');
        }

        // Bloquear IP
        async function blockIP() {
            const ip = document.getElementById('ip-to-block').value.trim();
            
            if (!ip) {
                showNotification('Por favor, digite um IP para bloquear', 'warning');
                return;
            }

            // Validação simples de IP
            const ipRegex = /^([0-9]{1,3}\\.){3}[0-9]{1,3}$/;
            if (!ipRegex.test(ip)) {
                showNotification('Por favor, digite um IP válido', 'error');
                return;
            }

            if (!confirm(`Tem certeza que deseja bloquear o IP ${ip}?`)) {
                return;
            }

            try {
                const response = await fetch('/api/ips/block', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ip: ip })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    showNotification(`IP ${ip} bloqueado com sucesso!`, 'success');
                    document.getElementById('ip-to-block').value = '';
                    loadData(); // Recarrega todos os dados
                } else {
                    showNotification('Erro ao bloquear IP: ' + (data.message || data.error), 'error');
                }
            } catch (error) {
                showNotification('Erro ao bloquear IP: ' + error, 'error');
            }
        }

        // Bloquear IP manual a partir de alerta
        async function blockIPManual(ip) {
            if (!ip || ip === 'N/A') {
                showNotification('IP inválido para bloqueio', 'warning');
                return;
            }

            if (!confirm(`Bloquear IP ${ip}?`)) {
                return;
            }

            try {
                const response = await fetch('/api/ips/block', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ip: ip })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    showNotification(`IP ${ip} bloqueado com sucesso!`, 'success');
                    loadData();
                } else {
                    showNotification('Erro ao bloquear IP: ' + (data.message || data.error), 'error');
                }
            } catch (error) {
                showNotification('Erro ao bloquear IP: ' + error, 'error');
            }
        }

        // Desbloquear IP
        async function unblockIP(ip) {
            if (!confirm(`Desbloquear IP ${ip}?`)) {
                return;
            }

            try {
                const response = await fetch('/api/ips/unblock', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ip: ip })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    showNotification(`IP ${ip} desbloqueado com sucesso!`, 'success');
                    loadData();
                } else {
                    showNotification('Erro ao desbloquear IP: ' + (data.message || data.error), 'error');
                }
            } catch (error) {
                showNotification('Erro ao desbloquear IP: ' + error, 'error');
            }
        }

        // Mostrar configurações
        function showSettings() {
            // Carrega configurações atuais
            fetch('/api/settings')
                .then(response => response.json())
                .then(settings => {
                    document.getElementById('auto-block').checked = settings.auto_block;
                    document.getElementById('alert-threshold').value = settings.alert_threshold;
                    document.getElementById('update-interval').value = settings.update_interval;
                    document.getElementById('notifications-enabled').checked = settings.notifications;
                    
                    // Mostra o modal
                    new bootstrap.Modal(document.getElementById('settingsModal')).show();
                })
                .catch(error => {
                    console.error('Erro ao carregar configurações:', error);
                    new bootstrap.Modal(document.getElementById('settingsModal')).show();
                });
        }

        // Salvar configurações
        async function saveSettings() {
            const settings = {
                auto_block: document.getElementById('auto-block').checked,
                alert_threshold: parseInt(document.getElementById('alert-threshold').value),
                update_interval: parseInt(document.getElementById('update-interval').value),
                notifications: document.getElementById('notifications-enabled').checked
            };

            try {
                const response = await fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(settings)
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    showNotification('Configurações salvas com sucesso!', 'success');
                    bootstrap.Modal.getInstance(document.getElementById('settingsModal')).hide();
                    
                    // Atualiza intervalo de atualização
                    clearInterval(window.autoRefreshInterval);
                    window.autoRefreshInterval = setInterval(loadData, settings.update_interval * 1000);
                } else {
                    showNotification('Erro ao salvar configurações', 'error');
                }
            } catch (error) {
                showNotification('Erro ao salvar configurações: ' + error, 'error');
            }
        }

        // Mostrar notificações
        function showNotifications() {
            showNotification('Sistema de notificações ativo', 'info');
        }

        // Sistema de notificações
        function showNotification(message, type = 'info') {
            notificationCount++;
            document.getElementById('notification-count').textContent = notificationCount;
            
            const toast = document.getElementById('liveToast');
            const toastMessage = document.getElementById('toast-message');
            
            // Configura cor baseada no tipo
            const toastHeader = toast.querySelector('.toast-header');
            toastHeader.className = toastHeader.className.replace(/bg-\\w+/, '');
            
            switch(type) {
                case 'success':
                    toastHeader.classList.add('bg-success', 'text-white');
                    break;
                case 'error':
                    toastHeader.classList.add('bg-danger', 'text-white');
                    break;
                case 'warning':
                    toastHeader.classList.add('bg-warning', 'text-dark');
                    break;
                default:
                    toastHeader.classList.add('bg-primary', 'text-white');
            }
            
            toastMessage.textContent = message;
            
            const bsToast = new bootstrap.Toast(toast);
            bsToast.show();
        }

        // Exportar dados
        function exportData() {
            showNotification('Exportando dados do sistema...', 'info');
            // Em produção, isso baixaria um arquivo CSV/JSON
            setTimeout(() => {
                showNotification('Dados exportados com sucesso!', 'success');
            }, 2000);
        }

        // Limpar dados antigos
        function clearOldData() {
            if (!confirm('Tem certeza que deseja limpar dados antigos? Esta ação não pode ser desfeita.')) {
                return;
            }

            showNotification('Limpando dados antigos...', 'warning');
            
            // Simula limpeza
            setTimeout(() => {
                showNotification('Dados antigos removidos com sucesso!', 'success');
                loadData(); // Recarrega dados
            }, 1500);
        }

        // Alternar gráfico de tráfego
        function toggleTrafficChart() {
            if (trafficChart.config.type === 'line') {
                trafficChart.config.type = 'bar';
            } else {
                trafficChart.config.type = 'line';
            }
            trafficChart.update();
            showNotification('Tipo de gráfico alterado', 'info');
        }

        // Download do gráfico
        function downloadChart() {
            const link = document.createElement('a');
            link.download = 'traffic-chart.png';
            link.href = document.getElementById('trafficChart').toDataURL();
            link.click();
            showNotification('Gráfico baixado com sucesso!', 'success');
        }

        // Inicialização
        document.addEventListener('DOMContentLoaded', function() {
            initializeCharts();
            loadData();
            
            // Atualização automática
            window.autoRefreshInterval = setInterval(loadData, 30000);
            
            // Busca em tempo real
            let searchTimeout;
            document.getElementById('search-alerts').addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    currentFilters.search = this.value;
                    loadAlerts();
                }, 500);
            });
            
            // Notificação de boas-vindas
            setTimeout(() => {
                showNotification('Sistema IDS/IPS inicializado com sucesso!', 'success');
            }, 1000);
        });
    </script>
</body>
</html>
"""

# ========== FUNÇÕES AUXILIARES ==========

def get_local_ips():
    """Obtém IPs locais de forma simples"""
    return ['10.16.90.128', 'localhost', '127.0.0.1']

def get_db_connection():
    """Conexão com banco de dados SQLite"""
    conn = sqlite3.connect('/opt/ids/network_data.db')
    conn.row_factory = sqlite3.Row
    return conn

# ========== ENDPOINTS DA API ==========

@app.route('/')
def home():
    """Página principal com interface web"""
    return render_template_string(HTML_TEMPLATE, 
                                hostname=socket.gethostname(),
                                local_ip='10.16.90.128')

@app.route('/api/stats')
def get_stats():
    """Estatísticas do sistema"""
    try:
        conn = get_db_connection()
        total_alerts = conn.execute('SELECT COUNT(*) FROM alerts').fetchone()[0]
        high_severity = conn.execute('SELECT COUNT(*) FROM alerts WHERE severity >= 3').fetchone()[0]
        blocked_ips = conn.execute('SELECT COUNT(DISTINCT src_ip) FROM alerts WHERE action_taken = "blocked"').fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'operational',
            'total_alerts': total_alerts,
            'high_severity_alerts': high_severity,
            'blocked_ips': blocked_ips,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/traffic')
def get_traffic_data():
    """Dados de tráfego para gráficos"""
    # Simula dados de tráfego (em produção viria do Suricata/Zeek)
    now = datetime.now()
    data = []
    for i in range(20):
        timestamp = now - timedelta(minutes=19-i)
        data.append({
            'timestamp': timestamp.isoformat(),
            'packets_per_second': random.randint(50, 500),
            'bytes_per_second': random.randint(1000, 10000)
        })
    return jsonify(data)

@app.route('/api/history')
def get_history():
    """Histórico de eventos"""
    try:
        conn = get_db_connection()
        
        # Busca últimos eventos de alertas
        alerts = conn.execute('''
            SELECT timestamp, src_ip, 'Alerta' as event_type, 
                   severity, signature as description, 'detected' as action
            FROM alerts 
            ORDER BY timestamp DESC 
            LIMIT 50
        ''').fetchall()
        
        conn.close()
        
        history = [dict(alert) for alert in alerts]
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts/today')
def get_filtered_alerts():
    """Alertas com filtros"""
    try:
        search = request.args.get('search', '')
        severity = request.args.get('severity', '')
        hours = request.args.get('hours', '24')
        
        conn = get_db_connection()
        
        query = '''
            SELECT * FROM alerts 
            WHERE timestamp >= datetime('now', ?)
        '''
        params = [f'-{hours} hours']
        
        if severity:
            query += ' AND severity >= ?'
            params.append(int(severity))
        
        if search:
            query += ' AND (src_ip LIKE ? OR dest_ip LIKE ? OR signature LIKE ?)'
            search_term = f'%{search}%'
            params.extend([search_term, search_term, search_term])
        
        query += ' ORDER BY timestamp DESC LIMIT 100'
        
        alerts = conn.execute(query, params).fetchall()
        conn.close()
        
        return jsonify([dict(alert) for alert in alerts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Configurações do sistema"""
    if request.method == 'GET':
        return jsonify(system_settings)
    else:
        data = request.get_json()
        system_settings.update(data)
        return jsonify({'status': 'success', 'message': 'Configurações atualizadas'})

@app.route('/api/ips/blocked')
def get_blocked_ips():
    """IPs bloqueados"""
    try:
        result = subprocess.run(
            ['iptables', '-L', 'INPUT', '-n', '--line-numbers'],
            capture_output=True, text=True, check=True
        )
        
        blocked_ips = []
        for line in result.stdout.split('\n'):
            if 'DROP' in line and '0.0.0.0/0' not in line:
                blocked_ips.append(line.strip())
                
        return jsonify({
            'status': 'success',
            'blocked_ips': blocked_ips,
            'count': len(blocked_ips)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ips/block', methods=['POST'])
def block_ip():
    """Bloqueia um IP manualmente"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados JSON necessários'}), 400
        
    ip = data.get('ip')
    if not ip:
        return jsonify({'error': 'IP não fornecido'}), 400
        
    try:
        # Verifica se já está bloqueado
        check_result = subprocess.run([
            'iptables', '-C', 'INPUT', '-s', ip, '-j', 'DROP'
        ], capture_output=True)
        
        if check_result.returncode == 0:
            return jsonify({'message': f'IP {ip} já está bloqueado'}), 400
            
        # Bloqueia o IP
        subprocess.run([
            'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'
        ], check=True)
        
        return jsonify({
            'status': 'success',
            'message': f'IP {ip} bloqueado com sucesso',
            'action': 'blocked'
        })
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ips/unblock', methods=['POST'])
def unblock_ip_api():
    """Desbloqueia um IP"""
    data = request.get_json()
    ip = data.get('ip')
    
    if not ip:
        return jsonify({'error': 'IP não fornecido'}), 400
        
    try:
        # Remove regra de bloqueio
        subprocess.run([
            'iptables', '-D', 'INPUT', '-s', ip, '-j', 'DROP'
        ], check=True)
        
        return jsonify({
            'status': 'success', 
            'message': f'IP {ip} desbloqueado com sucesso',
            'action': 'unblocked'
        })
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500

# ========== ENDPOINTS DE COMPATIBILIDADE ==========

@app.route('/stats')
def stats_legacy():
    return get_stats()

@app.route('/alerts/today')
def alerts_today_legacy():
    return get_today_alerts()

@app.route('/ips/blocked')
def blocked_ips_legacy():
    return get_blocked_ips()

@app.route('/network')
def network_legacy():
    return jsonify({
        'hostname': socket.gethostname(),
        'your_ip': '10.16.90.128',
        'access_points': [
            'http://localhost:5001',
            'http://10.16.90.128:5001',
            'http://127.0.0.1:5001'
        ]
    })

def get_today_alerts():
    """Endpoint legado para alertas de hoje"""
    try:
        conn = get_db_connection()
        today = datetime.now().date()
        alerts = conn.execute('''
            SELECT * FROM alerts 
            WHERE date(timestamp) = ?
            ORDER BY timestamp DESC
        ''', (today,)).fetchall()
        conn.close()
        return jsonify([dict(alert) for alert in alerts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== INICIALIZAÇÃO ==========

if __name__ == '__main__':
    print("=" * 60)
    print("🛡️  IDS/IPS DASHBOARD COMPLETO")
    print("=" * 60)
    print("🎨 Interface com:")
    print("   📊 Gráficos em tempo real")
    print("   🔔 Sistema de notificações") 
    print("   📈 Histórico de alertas")
    print("   🔍 Busca e filtros avançados")
    print("   ⚙️ Configurações do sistema")
    print("=" * 60)
    print("🌐 Acesse em:")
    print("   → http://localhost:5001")
    print("   → http://10.16.90.128:5001")
    print("   → http://127.0.0.1:5001")
    print("=" * 60)
    
    # Limpa porta se necessário
    try:
        subprocess.run(['fuser', '-k', '5001/tcp'], capture_output=True)
    except:
        pass
    
    app.run(host='0.0.0.0', port=5001, debug=False)
