#!/usr/bin/env python3
"""
Script de diagnóstico para entender o que está acontecendo na extração
Execute antes de rodar o workflow para identificar problemas
"""

import os
import json
import subprocess
from pathlib import Path

def check_credentials():
    """Verifica se credenciais estão disponíveis"""
    print(f"\n{'='*80}")
    print(f"🔐 VERIFICANDO CREDENCIAIS")
    print(f"{'='*80}\n")

    username = os.getenv('ESCALA_USERNAME')
    password = os.getenv('ESCALA_PASSWORD')

    if username:
        print(f"✅ ESCALA_USERNAME configurado: {username[:10]}***")
    else:
        print(f"❌ ESCALA_USERNAME NÃO configurado!")

    if password:
        print(f"✅ ESCALA_PASSWORD configurado: {'*' * len(password)}")
    else:
        print(f"❌ ESCALA_PASSWORD NÃO configurado!")

    return bool(username and password)


def check_dependencies():
    """Verifica dependências necessárias"""
    print(f"\n{'='*80}")
    print(f"📦 VERIFICANDO DEPENDÊNCIAS")
    print(f"{'='*80}\n")

    # Verificar Python modules
    modules = ['selenium', 'beautifulsoup4', 'requests']
    all_ok = True

    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} instalado")
        except ImportError:
            print(f"❌ {module} NÃO instalado!")
            all_ok = False

    # Verificar ChromeDriver
    print(f"\nVerificando Chrome/ChromeDriver...")
    result = subprocess.run("which chromedriver", shell=True, capture_output=True)
    if result.returncode == 0:
        print(f"✅ ChromeDriver encontrado")
    else:
        print(f"⚠️  ChromeDriver não encontrado em PATH")
        print(f"   → Será tentado baixar automaticamente pelo Selenium")

    return all_ok


def check_network():
    """Verifica conexão com site"""
    print(f"\n{'='*80}")
    print(f"🌐 VERIFICANDO CONEXÃO COM ESCALA.MED.BR")
    print(f"{'='*80}\n")

    import requests
    try:
        response = requests.head('https://escala.med.br', timeout=5)
        if response.status_code < 400:
            print(f"✅ Site acessível (status {response.status_code})")
            return True
        else:
            print(f"⚠️  Site retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return False


def check_extraction_files():
    """Verifica arquivos de extração"""
    print(f"\n{'='*80}")
    print(f"📁 VERIFICANDO ARQUIVOS DE EXTRAÇÃO")
    print(f"{'='*80}\n")

    files_to_check = [
        '/Users/joaoperes/escalaHRO/extracao_inteligente.py',
        '/Users/joaoperes/escalaHRO/ramais_hro.json',
        '/Users/joaoperes/escalaHRO/setor_ramais_mapping.json',
    ]

    all_ok = True
    for file in files_to_check:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file.split('/')[-1]} ({size} bytes)")
        else:
            print(f"❌ {file} NÃO ENCONTRADO!")
            all_ok = False

    return all_ok


def test_extraction():
    """Tenta fazer uma extração de teste"""
    print(f"\n{'='*80}")
    print(f"🧪 TESTANDO EXTRAÇÃO")
    print(f"{'='*80}\n")

    print("Executando: python3 extracao_inteligente.py")
    print("(Isso pode levar 1-2 minutos)\n")

    result = subprocess.run(
        "python3 extracao_inteligente.py",
        shell=True,
        cwd="/Users/joaoperes/escalaHRO",
        capture_output=True,
        timeout=300,
        text=True
    )

    print("STDOUT:")
    print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)

    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)

    if result.returncode == 0:
        print(f"\n✅ Extração concluída com sucesso!")

        # Verificar se arquivo foi gerado
        arquivo = '/tmp/extracao_inteligente.json'
        if os.path.exists(arquivo):
            with open(arquivo, 'r') as f:
                data = json.load(f)

            print(f"\n📊 Dados extraídos:")
            print(f"   - Data atual: {data.get('atual', {}).get('data', 'N/A')}")
            print(f"   - Registros: {len(data.get('atual', {}).get('registros', []))}")
            print(f"   - Ramais embarcados: {len(data.get('ramais_hro', []))}")
            print(f"   - Mapeamentos: {len(data.get('setor_ramais_mapping', []))}")

            return True
        else:
            print(f"❌ Arquivo de extração não foi criado!")
            return False
    else:
        print(f"\n❌ Extração falhou com código: {result.returncode}")
        return False


def main():
    """Executa todos os diagnósticos"""
    print(f"\n")
    print(f"╔{'='*78}╗")
    print(f"║ 🔍 DIAGNÓSTICO DE EXTRAÇÃO - ESCALA HRO                                    ║")
    print(f"║ Ferramenta de troubleshooting para GitHub Actions workflow                ║")
    print(f"╚{'='*78}╝")

    results = {
        'Credenciais': check_credentials(),
        'Dependências': check_dependencies(),
        'Conexão': check_network(),
        'Arquivos': check_extraction_files(),
        'Extração': test_extraction(),
    }

    # Resumo
    print(f"\n{'='*80}")
    print(f"📋 RESUMO DE DIAGNÓSTICO")
    print(f"{'='*80}\n")

    for item, resultado in results.items():
        status = "✅ OK" if resultado else "❌ PROBLEMA"
        print(f"{status} - {item}")

    print(f"\n{'='*80}")

    if all(results.values()):
        print(f"✅ TODOS OS DIAGNÓSTICOS PASSARAM!")
        print(f"   O workflow deve funcionar corretamente.")
        print(f"\n   Próximos passos:")
        print(f"   1. Ir para GitHub Actions")
        print(f"   2. Rodar workflow manualmente: 'Atualizar Escala Diária HRO'")
        print(f"   3. Verificar se dashboard atualiza com dados reais")
    else:
        print(f"❌ ALGUNS PROBLEMAS ENCONTRADOS!")
        failed = [k for k, v in results.items() if not v]
        print(f"   Itens com problema: {', '.join(failed)}")
        print(f"\n   Ações sugeridas:")
        if not results['Credenciais']:
            print(f"   - Configurar ESCALA_USERNAME e ESCALA_PASSWORD no GitHub Secrets")
        if not results['Dependências']:
            print(f"   - Rodar: pip install -r requirements.txt")
        if not results['Conexão']:
            print(f"   - Verificar conexão com internet")
        if not results['Arquivos']:
            print(f"   - Verificar que todos os arquivos estão no repositório")
        if not results['Extração']:
            print(f"   - Executar novamente após corrigir os itens acima")

    print(f"{'='*80}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERRO NO DIAGNÓSTICO: {e}")
        import traceback
        traceback.print_exc()
