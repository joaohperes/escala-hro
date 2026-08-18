#!/usr/bin/env python3
"""
Script de atualização da escala e dashboard
Orquestra:
1. Tenta extrair dados frescos da escala (extracao_inteligente.py)
2. Gera o dashboard com os dados disponíveis

Workflow simplificado:
- extracao_inteligente.py → /tmp/extracao_inteligente.json
- gerar_dashboard_executivo.py → busca os dados e gera o dashboard
  (Prioriza extracao_inteligente.json, fallback para escalas_multiplos_dias.json)
"""

import subprocess
import sys
from pathlib import Path

def run_extraction():
    """Tenta executar a extração de dados da escala.med.br"""
    print("\n📋 Tentando extrair dados de escala.med.br...")
    try:
        # 600s: o login agora tem esperas explícitas + retentativas (até ~210s no
        # pior caso) antes da extração em si, que leva ~60s.
        result = subprocess.run("python3 extracao_inteligente.py",
                              shell=True,
                              check=False,
                              timeout=600)
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

def generate_dashboard():
    """Executa a geração do dashboard"""
    print(f"\n📋 Gerando dashboard...")
    try:
        result = subprocess.run("python3 gerar_dashboard_executivo.py",
                              shell=True,
                              check=True,
                              timeout=60)
        print(f"✅ Dashboard gerado com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao gerar dashboard (código: {e.returncode})")
        return False
    except subprocess.TimeoutExpired:
        print(f"❌ Geração de dashboard expirou")
        return False
    except Exception as e:
        print(f"❌ Erro ao gerar dashboard: {e}")
        return False

def main():
    print("🚀 Iniciando atualização da escala e dashboard...")

    # Passo 1: Tentar extração de dados frescos
    extraction_ok = run_extraction()

    # Passo 2: Gerar dashboard
    # (gerar_dashboard_executivo.py buscará os dados automaticamente)
    if not generate_dashboard():
        return 1

    # Passo 3: Verificar se dashboard foi gerado
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
        print("\n⚠️  Atualização do dashboard concluída")
        print("   (Extração falhou, mas dashboard foi gerado com dados disponíveis)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
