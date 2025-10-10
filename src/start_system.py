#!/usr/bin/env python3
import subprocess
import time
import sys
import os

def run_command(cmd, description):
    """Executa um comando e mostra o resultado"""
    print(f"🚀 {description}...")
    try:
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        return process
    except Exception as e:
        print(f"❌ Erro ao {description}: {e}")
        return None

def main():
    print("=" * 50)
    print("🛡️  INICIANDO SISTEMA IDS/IPS")
    print("=" * 50)
    
    # Verifica permissões do banco
    db_dir = "/opt/ids"
    if not os.path.exists(db_dir):
        print(f"📁 Criando diretório do banco: {db_dir}")
        os.makedirs(db_dir, mode=0o755, exist_ok=True)
    
    processes = []
    
    # 1. Inicia Suricata
    suricata_cmd = ["suricata", "-c", "/etc/suricata/suricata.yaml", "-i", "eth0"]
    processes.append(run_command(suricata_cmd, "Suricata"))
    
    time.sleep(5)  # Mais tempo para Suricata inicializar
    
    # 2. Inicia Zeek
    zeek_cmd = ["/opt/zeek/bin/zeek", "-i", "eth0"]
    processes.append(run_command(zeek_cmd, "Zeek"))
    
    time.sleep(5)  # Mais tempo para Zeek inicializar
    
    # 3. Inicia processadores Python
    python_cmd = sys.executable
    
    print("📊 Iniciando processadores Python...")
    
    # Log Processor
    log_proc = run_command([python_cmd, "log_processor.py"], "Log Processor")
    processes.append(log_proc)
    
    time.sleep(3)
    
    # Zeek Integrator
    zeek_proc = run_command([python_cmd, "zeek_integrator.py"], "Zeek Integrator")
    processes.append(zeek_proc)
    
    time.sleep(3)
    
    # API
    api_proc = run_command([python_cmd, "ids_api_fixed.py"], "API Web")
    processes.append(api_proc)
    
    print("\n" + "=" * 50)
    print("✅ SISTEMA INICIADO COM SUCESSO!")
    print("=" * 50)
    print("📊 Serviços em execução:")
    print("   - Suricata (IDS/IPS)")
    print("   - Zeek (Análise de rede)")
    print("   - Log Processor")
    print("   - Zeek Integrator")
    print("   - API Web: http://localhost:5001")
    print("\n📈 Verifique os logs:")
    print("   tail -f /var/log/suricata/eve.json")
    print("\n⏹️  Pressione Ctrl+C para parar")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Parando serviços...")
        for proc in processes:
            if proc:
                proc.terminate()
        print("✅ Serviços parados.")

if __name__ == "__main__":
    main()
