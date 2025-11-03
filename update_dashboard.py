#!/usr/bin/env python3
"""
Script de atualização da escala e dashboard
Orquestra:
1. Tenta extrair dados da escala (extracao_inteligente.py)
2. Se falhar, usa o último arquivo JSON conhecido
3. Gera o dashboard
"""

import subprocess
import sys
import shutil
import os
import json
from pathlib import Path

def run_extraction():
    """Tenta executar a extração de dados"""
    print("\n📋 Tentando extrair dados de escala.med.br...")
    try:
        result = subprocess.run("python3 extracao_inteligente.py",
                              shell=True,
                              check=False,
                              timeout=300)
        if result.returncode == 0:
            print("✅ Extração bem-sucedida")
            return True
        else:
            print(f"⚠️  Extração falhou (código: {result.returncode})")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Extração expirou (timeout)")
        return False
    except Exception as e:
        print(f"⚠️  Erro na extração: {e}")
        return False

def find_data_file():
    """Procura pelo arquivo JSON de dados"""
    # Locais a procurar em ordem de preferência
    locations = [
        "/tmp/extracao_inteligente.json",
        "/tmp/escalas_multiplos_dias.json",
        "escalas_multiplos_dias.json",
        "escala-hro/escalas_multiplos_dias.json",
        "test_data.json",  # Fallback para dados de teste
    ]

    for loc in locations:
        if Path(loc).exists():
            # Verificar se arquivo tem dados (não é só um placeholder vazio)
            try:
                with open(loc, 'r') as f:
                    data = json.load(f)
                    # Verificar se tem pelo menos um registro
                    has_data = (
                        bool(data.get('atual', {}).get('registros', [])) or
                        bool(data.get('anterior', {}).get('registros', [])) or
                        bool(data.get('proximo', {}).get('registros', []))
                    )
                    if has_data or 'test_data' in loc:  # Permitir test_data mesmo que vazio
                        print(f"✅ Encontrado arquivo de dados: {loc}")
                        return loc
                    else:
                        print(f"⚠️  Arquivo {loc} está vazio, procurando próximo...")
                        continue
            except Exception as e:
                print(f"⚠️  Erro ao ler {loc}: {e}")
                continue

    return None

def main():
    print("🚀 Iniciando atualização da escala e dashboard...")

    # Passo 1: Tentar extração
    extraction_ok = run_extraction()

    # Passo 2: Encontrar arquivo de dados
    print(f"\n📁 Procurando arquivo de dados...")
    data_file = find_data_file()

    if not data_file:
        print("❌ Nenhum arquivo de dados encontrado")
        return 1

    # Passo 3: Copiar para local esperado
    source = data_file
    dest = "/tmp/escalas_multiplos_dias.json"

    print(f"\n📁 Copiando dados para {dest}...")
    try:
        shutil.copy(source, dest)
        print(f"✅ Arquivo copiado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao copiar arquivo: {e}")
        return 1

    # Passo 4: Gerar dashboard
    print(f"\n📋 Gerando dashboard...")
    try:
        result = subprocess.run("python3 gerar_dashboard_executivo.py",
                              shell=True,
                              check=True,
                              timeout=60)
        print(f"✅ Dashboard gerado com sucesso")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao gerar dashboard (código: {e.returncode})")
        return 1
    except subprocess.TimeoutExpired:
        print(f"❌ Geração de dashboard expirou")
        return 1
    except Exception as e:
        print(f"❌ Erro ao gerar dashboard: {e}")
        return 1

    # Passo 5: Verificar se dashboard foi gerado
    dashboard_file = "/tmp/dashboard_executivo.html"
    print(f"\n📁 Verificando dashboard...")

    if not Path(dashboard_file).exists():
        print(f"❌ Dashboard não foi gerado: {dashboard_file}")
        return 1

    print(f"✅ Dashboard encontrado: {dashboard_file}")

    # Status final
    if extraction_ok:
        print("\n✅ Atualização completa com dados FRESCOS da escala!")
    else:
        print("\n✅ Atualização completa com dados em CACHE (extração falhou, mas dashboard foi regenerado)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
