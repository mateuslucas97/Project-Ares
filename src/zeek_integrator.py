#!/usr/bin/env python3
import json
import sqlite3
from pathlib import Path
import subprocess
from datetime import datetime

class ZeekIntegrator:
    def __init__(self):
        self.zeek_path = "/opt/zeek/logs/current/"
        self.db_path = "/opt/ids/network_data.db"
        self.init_database()

    def ensure_db_directory(self):
        """Garante que o diretório do banco existe"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, mode=0o755, exist_ok=True)
            except PermissionError:
                print(f"❌ Sem permissão para criar {db_dir}")
                self.db_path = os.path.expanduser("~/ids-network_data.db")
        
    def init_database(self):
        """Inicializa banco de dados para correlacionar eventos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS zeek_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                src_ip TEXT,
                dest_ip TEXT,
                protocol TEXT,
                port INTEGER,
                event_type TEXT,
                description TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ Banco Zeek inicializado: {self.db_path}")
        except sqlite3.Error as e:
            print(f"❌ Erro banco Zeek: {e}")
            self.db_path = os.path.expanduser("~/ids-network_data.db")
            self.init_database_fallback()

    def init_database_fallback(self):
        """Fallback para diretório home"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS zeek_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    src_ip TEXT,
                    dest_ip TEXT,
                    protocol TEXT,
                    port INTEGER,
                    event_type TEXT,
                    description TEXT
                )
            ''')
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"❌ Erro crítico banco Zeek: {e}")
            self.db_path = None
        
    def process_zeek_logs(self):
        """Processa logs do Zeek periodicamente"""
        import time
        while True:
            self.parse_recent_zeek_logs()
            time.sleep(60)  # Processa a cada 60 segundos
                
    def parse_recent_zeek_logs(self):
        """Parseia logs recentes do Zeek"""
        for log_file in Path(self.zeek_path).glob("*.log"):
            self.process_zeek_file(log_file)
                
    def process_zeek_file(self, file_path):
        """Processa arquivo individual do Zeek"""
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if line.startswith('#'):  # Ignora linhas de comentário
                        continue
                    
                    # Processa linha do Zeek (formato TSV)
                    fields = line.strip().split('\t')
                    if len(fields) >= 7:
                        self.store_zeek_event(fields, file_path.name)
                        
        except Exception as e:
            print(f"Erro processando {file_path}: {e}")
            
    def store_zeek_event(self, fields, filename):
        """Armazena eventos do Zeek no banco"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Converte timestamp do Zeek
            zeek_ts = float(fields[0])
            dt = datetime.fromtimestamp(zeek_ts)
            
            cursor.execute('''
                INSERT INTO zeek_events 
                (timestamp, src_ip, dest_ip, protocol, port, event_type, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                dt.isoformat(),
                fields[2] if len(fields) > 2 else '',  # src_ip
                fields[4] if len(fields) > 4 else '',  # dest_ip
                fields[6] if len(fields) > 6 else '',  # protocol
                int(fields[5]) if len(fields) > 5 and fields[5].isdigit() else 0,
                filename.replace('.log', ''),
                f"Zeek event from {filename}"
            ))
            
            conn.commit()
        except Exception as e:
            print(f"Erro armazenando evento: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    integrator = ZeekIntegrator()
    integrator.process_zeek_logs()
