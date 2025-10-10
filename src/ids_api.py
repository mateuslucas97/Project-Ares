#!/usr/bin/env python3
from flask import Flask, jsonify, request
import sqlite3
import subprocess
from datetime import datetime, timedelta

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('/opt/ids/network_data.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/alerts/today', methods=['GET'])
def get_today_alerts():
    """Retorna alertas do dia"""
    conn = get_db_connection()
    
    today = datetime.now().date()
    alerts = conn.execute('''
        SELECT * FROM alerts 
        WHERE date(timestamp) = ?
        ORDER BY timestamp DESC
    ''', (today,)).fetchall()
    
    conn.close()
    return jsonify([dict(alert) for alert in alerts])

@app.route('/alerts/<int:severity>', methods=['GET'])
def get_alerts_by_severity(severity):
    """Retorna alertas por severidade"""
    conn = get_db_connection()
    
    alerts = conn.execute('''
        SELECT * FROM alerts 
        WHERE severity >= ?
        ORDER BY timestamp DESC
    ''', (severity,)).fetchall()
    
    conn.close()
    return jsonify([dict(alert) for alert in alerts])

@app.route('/ips/blocked', methods=['GET'])
def get_blocked_ips():
    """Lista IPs bloqueados"""
    try:
        result = subprocess.run(
            ['iptables', '-L', 'INPUT', '-n', '--line-numbers'],
            capture_output=True, text=True, check=True
        )
        
        blocked_ips = []
        for line in result.stdout.split('\n'):
            if 'DROP' in line and '0.0.0.0/0' not in line:
                blocked_ips.append(line.strip())
                
        return jsonify({'blocked_ips': blocked_ips})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ips/block', methods=['POST'])
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
        
        return jsonify({'message': f'IP {ip} bloqueado com sucesso'})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ips/unblock', methods=['POST'])
def unblock_ip():
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
        
        return jsonify({'message': f'IP {ip} desbloqueado com sucesso'})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Retorna estatísticas do sistema"""
    conn = get_db_connection()
    
    total_alerts = conn.execute('SELECT COUNT(*) FROM alerts').fetchone()[0]
    high_severity = conn.execute('SELECT COUNT(*) FROM alerts WHERE severity >= 3').fetchone()[0]
    blocked_ips = conn.execute('SELECT COUNT(DISTINCT src_ip) FROM alerts WHERE action_taken = "blocked"').fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_alerts': total_alerts,
        'high_severity_alerts': high_severity,
        'blocked_ips': blocked_ips
    })

if __name__ == '__main__':
    print("=== INICIANDO API IDS/IPS ===")
    print("📡 Endpoints disponíveis em:")
    local_ips = get_local_ips()
    for ip in local_ips:
        print(f"   http://{ip}:5001")  # MUDOU PARA 5001
    print("   http://localhost:5001")  # MUDOU PARA 5001
    print("=== INICIANDO API IDS/IPS ===")
    print("📡 Endpoints disponíveis em:")
    local_ips = get_local_ips()
    for ip in local_ips:
        print(f"   http://{ip}:5001")  # MUDOU PARA 5001
    print("   http://localhost:5001")  # MUDOU PARA 5001
    print("==============================")
    print("==============================")

    app.run(host='0.0.0.0', port=5000, debug=True)
