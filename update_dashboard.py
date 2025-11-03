#!/usr/bin/env python3
"""
Script de atualização da escala e dashboard
Orquestra:
1. Extração dos dados da escala (extracao_inteligente.py)
2. Geração do dashboard (gerar_dashboard_executivo.py)
"""

import subprocess
import sys
import shutil
import os
from pathlib import Path

def run_command(cmd, description):
    """Execute um comando e retorna o status"""
    print(f"\n📋 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - OK")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ERRO")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False

def main():
    print("🚀 Iniciando atualização da escala e dashboard...")

    # Passo 1: Executar extração
    if not run_command("python3 extracao_inteligente.py", "Extração de dados"):
        print("❌ Falha na extração - abortando")
        return 1

    # Passo 2: Copiar arquivo de dados para o local esperado
    source = "/tmp/extracao_inteligente.json"
    dest = "/tmp/escalas_multiplos_dias.json"

    if Path(source).exists():
        print(f"\n📁 Copiando dados para {dest}...")
        try:
            shutil.copy(source, dest)
            print(f"✅ Arquivo copiado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao copiar arquivo: {e}")
            return 1
    else:
        print(f"❌ Arquivo de origem não encontrado: {source}")
        return 1

    # Passo 3: Gerar dashboard
    if not run_command("python3 gerar_dashboard_executivo.py", "Geração do dashboard"):
        print("❌ Falha na geração do dashboard - abortando")
        return 1

    # Passo 4: Verificar se dashboard foi gerado
    dashboard_file = "/tmp/dashboard_executivo.html"
    if not Path(dashboard_file).exists():
        print(f"❌ Dashboard não foi gerado: {dashboard_file}")
        return 1

    print("\n✅ Atualização concluída com sucesso!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
