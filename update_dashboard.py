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
    """Execute um comando e retorna o status com output completo"""
    print(f"\n📋 {description}...")
    try:
        # Não redirecionar output para que possamos ver logs em tempo real
        result = subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} - OK")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ERRO (código de saída: {e.returncode})")
        return False

def main():
    print("🚀 Iniciando atualização da escala e dashboard...")

    # Passo 1: Executar extração
    if not run_command("python3 extracao_inteligente.py", "Extração de dados"):
        print("❌ Falha na extração - abortando")
        return 1

    # Passo 2: Verificar se arquivo foi criado
    source = "/tmp/extracao_inteligente.json"
    dest = "/tmp/escalas_multiplos_dias.json"

    print(f"\n📁 Verificando se arquivo foi criado...")
    print(f"   Procurando por: {source}")

    if not Path(source).exists():
        print(f"❌ Arquivo de origem não encontrado: {source}")
        # Listar arquivos em /tmp para debug
        print(f"\n📂 Conteúdo de /tmp:")
        try:
            result = subprocess.run("ls -la /tmp/ | grep -E 'escala|extracao|dashboard'",
                                  shell=True, capture_output=True, text=True)
            print(result.stdout)
        except:
            pass
        return 1

    print(f"✅ Arquivo encontrado: {source}")

    # Passo 3: Copiar arquivo de dados para o local esperado
    print(f"\n📁 Copiando dados para {dest}...")
    try:
        shutil.copy(source, dest)
        print(f"✅ Arquivo copiado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao copiar arquivo: {e}")
        return 1

    # Passo 4: Gerar dashboard
    if not run_command("python3 gerar_dashboard_executivo.py", "Geração do dashboard"):
        print("❌ Falha na geração do dashboard - abortando")
        return 1

    # Passo 5: Verificar se dashboard foi gerado
    dashboard_file = "/tmp/dashboard_executivo.html"
    print(f"\n📁 Verificando se dashboard foi gerado...")
    print(f"   Procurando por: {dashboard_file}")

    if not Path(dashboard_file).exists():
        print(f"❌ Dashboard não foi gerado: {dashboard_file}")
        return 1

    print(f"✅ Dashboard encontrado: {dashboard_file}")

    print("\n✅ Atualização concluída com sucesso!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
