#!/usr/bin/env python3
import json
import time
import subprocess
from pathlib import Path
import sqlite3  # Já incluso no Python
from datetime import datetime

class LogProcessor:
    def __init__(self):
        self.suricata_log = "/var/log/suricata/eve.json"
        self.zeek_logs = "/opt/zeek/logs/current/"
        self.db_path = "/opt/ids/network_data.db"
        self.init_database()
        
    def ensure_db_directory(self):
        """Garante que o diretório do banco existe e tem permissões"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, mode=0o755, exist_ok=True)
                print(f"✅ Diretório criado: {db_dir}")
            except PermissionError:
                print(f"❌ Sem permissão para criar {db_dir}")
                # Usa diretório home como fallback
                self.db_path = os.path.expanduser("~/ids-network_data.db")
                print(f"📁 Usando fallback: {self.db_path}")

    def init_database(self):
        """Inicializa banco de dados SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                src_ip TEXT,
                dest_ip TEXT,
                alert_id INTEGER,
                signature TEXT,
                severity INTEGER,
                action_taken TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print(f"✅ Banco de dados inicializado: {self.db_path}")
        except sqlite3.Error as e:
            print(f"❌ Erro ao inicializar banco: {e}")
            # Fallback para diretório home
            self.db_path = os.path.expanduser("~/ids-network_data.db")
            print(f"📁 Tentando fallback: {self.db_path}")
            self.init_database_fallback()

    def init_database_fallback(self):
        """Tenta inicializar no diretório home"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    src_ip TEXT,
                    dest_ip TEXT,
                    alert_id INTEGER,
                    signature TEXT,
                    severity INTEGER,
                    action_taken TEXT
                )
            ''')
            conn.commit()
            conn.close()
            print(f"✅ Banco de dados fallback criado: {self.db_path}")
        except sqlite3.Error as e:
            print(f"❌ Erro crítico com banco de dados: {e}")
            # Continua sem banco de dados
            self.db_path = None

        
    def tail_suricata_logs(self):
        """Monitora logs do Suricata em tempo real"""
        try:
            with open(self.suricata_log, 'r') as file:
                file.seek(0, 2)  # Vai para o final do arquivo
                while True:
                    line = file.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    try:
                        log_entry = json.loads(line)
                        self.process_suricata_event(log_entry)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            print(f"Arquivo {self.suricata_log} não encontrado")
            
    def process_suricata_event(self, event):
        """Processa eventos do Suricata"""
        if 'alert' in event.get('event_type', ''):
            self.handle_alert(event)
            
    def handle_alert(self, alert):
        """Processa alertas críticos"""
        severity = alert.get('alert', {}).get('severity', 1)
        
        # Salva no banco de dados
        self.save_alert_to_db(alert)
        
        if severity >= 2:  # Alertas médios ou altos
            self.send_alert_notification(alert)
            if severity >= 3:  # Só bloqueia automaticamente se for alta severidade
                self.block_suspicious_ip(alert)
    
    def save_alert_to_db(self, alert):
        """Salva alerta no banco SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts 
            (timestamp, src_ip, dest_ip, alert_id, signature, severity, action_taken)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            alert.get('src_ip'),
            alert.get('dest_ip'),
            alert.get('alert', {}).get('signature_id'),
            alert.get('alert', {}).get('signature'),
            alert.get('alert', {}).get('severity', 1),
            'pending'
        ))
        
        conn.commit()
        conn.close()
            
    def send_alert_notification(self, alert):
        """Envia notificação de alerta"""
        message = {
            "timestamp": datetime.now().isoformat(),
            "alert_id": alert.get('alert', {}).get('signature_id'),
            "message": alert.get('alert', {}).get('signature'),
            "src_ip": alert.get('src_ip'),
            "dest_ip": alert.get('dest_ip'),
            "severity": alert.get('alert', {}).get('severity', 1)
        }
        print(f"ALERTA: {message}")
            
    def block_suspicious_ip(self, alert):
        """Bloqueia IPs maliciosos via iptables (modo IPS)"""
        src_ip = alert.get('src_ip')
        signature = alert.get('alert', {}).get('signature', '')
        
        if src_ip and not self.is_internal_ip(src_ip):
            try:
                # Verifica se já está bloqueado
                result = subprocess.run([
                    'iptables', '-C', 'INPUT', '-s', src_ip, '-j', 'DROP'
                ], capture_output=True, text=True)
                
                # Se não existe (returncode != 0), adiciona
                if result.returncode != 0:
                    subprocess.run([
                        'iptables', '-A', 'INPUT', '-s', src_ip, '-j', 'DROP'
                    ], check=True)
                    print(f"IP {src_ip} bloqueado devido a {signature}")
                    
                    # Atualiza banco
                    self.update_alert_action(src_ip, 'blocked')
            except subprocess.CalledProcessError as e:
                print(f"Erro ao bloquear IP {src_ip}: {e}")
    
    def is_internal_ip(self, ip):
        """Verifica se é IP interno para não bloquear acidentalmente"""
        internal_nets = ['10.16.85.', '10.16.83.', '10.16.89.', '10.16.90.', '10.16.91.']
        return any(ip.startswith(net) for net in internal_nets)
    
    def update_alert_action(self, src_ip, action):
        """Atualiza ação tomada no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE alerts SET action_taken = ? WHERE src_ip = ? AND action_taken = ?',
            (action, src_ip, 'pending')
        )
        conn.commit()
        conn.close()

if __name__ == "__main__":
    processor = LogProcessor()
    processor.tail_suricata_logs()
