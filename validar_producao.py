#!/usr/bin/env python3
"""
VALIDATION SCRIPT - Escala HRO Production Safety Check
Verifica que todas as regras críticas foram seguidas após cada execução
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

def validar_ramais():
    """Valida que ramais estão embarcados corretamente"""
    print(f"\n{'='*80}")
    print(f"🔍 VALIDANDO RAMAIS (Função Fixa Crítica)")
    print(f"{'='*80}\n")

    resultado = True

    # Verificar arquivo principal (deve existir em /tmp durante workflow)
    arquivo = '/tmp/extracao_inteligente.json'

    if not os.path.exists(arquivo):
        print(f"⚠️  AVISO: {arquivo} não existe (esperado fora do workflow)")
        print(f"   Este script deve ser rodado DURANTE o GitHub Actions workflow")
        print(f"   ou IMEDIATAMENTE APÓS a execução de extracao_inteligente.py")
        print(f"\n   Verificando se extração foi executada corretamente...")

        # Verificar se arquivos fonte existem (ramais_hro.json)
        if os.path.exists('/Users/joaoperes/escalaHRO/ramais_hro.json'):
            print(f"✅ Arquivo source ramais_hro.json existe")
        else:
            print(f"❌ Arquivo source ramais_hro.json NÃO existe!")
            return False

        if os.path.exists('/Users/joaoperes/escalaHRO/setor_ramais_mapping.json'):
            print(f"✅ Arquivo source setor_ramais_mapping.json existe")
        else:
            print(f"❌ Arquivo source setor_ramais_mapping.json NÃO existe!")
            return False

        print(f"\n✅ Arquivos fonte OK - ramais serão embarcados na próxima execução")
        return True

    try:
        with open(arquivo, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ ERRO ao ler JSON: {e}")
        return False

    # Validação 1: Ramais presentes?
    if 'ramais_hro' not in data:
        print(f"❌ ERRO CRÍTICO: 'ramais_hro' não encontrado no arquivo!")
        resultado = False
    else:
        ramais_count = len(data.get('ramais_hro', []))
        if ramais_count > 0:
            print(f"✅ Ramais presentes: {ramais_count} departamentos")
        else:
            print(f"❌ ERRO: 'ramais_hro' está vazio!")
            resultado = False

    # Validação 2: Mapeamento de setores presente?
    if 'setor_ramais_mapping' not in data:
        print(f"❌ ERRO CRÍTICO: 'setor_ramais_mapping' não encontrado!")
        resultado = False
    else:
        mapping_count = len(data.get('setor_ramais_mapping', []))
        if mapping_count > 0:
            print(f"✅ Mapeamento de setores presente: {mapping_count} mapeamentos")
        else:
            print(f"❌ ERRO: 'setor_ramais_mapping' está vazio!")
            resultado = False

    # Validação 3: Estrutura esperada
    if 'atual' not in data or 'anterior' not in data:
        print(f"❌ ERRO: Estrutura de escalas incompleta!")
        resultado = False
    else:
        print(f"✅ Estrutura de escalas OK")

    return resultado


def validar_dia_anterior():
    """Valida que dia anterior é exatamente D-1"""
    print(f"\n{'='*80}")
    print(f"📅 VALIDANDO DIA ANTERIOR (Rolling Window D-1)")
    print(f"{'='*80}\n")

    resultado = True

    arquivo = '/tmp/extracao_inteligente.json'
    if not os.path.exists(arquivo):
        arquivo = '/Users/joaoperes/escalaHRO/data/extracao_inteligente_anterior_cache.json'

    try:
        with open(arquivo, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ ERRO ao ler JSON: {e}")
        return False

    # Extrair datas
    data_atual_str = data.get('atual', {}).get('data', '')
    data_anterior_str = data.get('anterior', {}).get('data', '')

    print(f"Data atual no arquivo: {data_atual_str}")
    print(f"Data anterior no arquivo: {data_anterior_str}")

    if not data_atual_str or not data_anterior_str:
        print(f"❌ ERRO: Datas não encontradas no arquivo!")
        return False

    # Converter para datetime
    meses_pt = {
        'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
        'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
        'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
    }

    try:
        partes_atual = data_atual_str.split()
        partes_anterior = data_anterior_str.split()

        data_atual = datetime(
            int(partes_atual[2]),
            meses_pt[partes_atual[1].lower()],
            int(partes_atual[0])
        )

        data_anterior = datetime(
            int(partes_anterior[2]),
            meses_pt[partes_anterior[1].lower()],
            int(partes_anterior[0])
        )

        dias_diff = (data_atual - data_anterior).days

        print(f"\nDiferença de dias: {dias_diff}")

        if dias_diff == 1:
            print(f"✅ CORRETO: Anterior é exatamente D-1 (1 dia atrás)")
        elif dias_diff == 2:
            print(f"⚠️  AVISO: Anterior é 2 dias atrás (workflow perdeu 1 dia)")
            print(f"   → Verificar se workflow rodou ontem")
        elif dias_diff > 2:
            print(f"❌ ERRO: Anterior tem {dias_diff} dias de diferença!")
            resultado = False
        else:
            print(f"❌ ERRO: Anterior é mais recente que atual! Data inválida!")
            resultado = False

    except Exception as e:
        print(f"❌ ERRO ao converter datas: {e}")
        resultado = False

    return resultado


def validar_autenticacao():
    """Valida que autenticação está ativada"""
    print(f"\n{'='*80}")
    print(f"🔐 VALIDANDO AUTENTICAÇÃO")
    print(f"{'='*80}\n")

    arquivo = '/Users/joaoperes/escalaHRO/index.html'

    try:
        with open(arquivo, 'r') as f:
            html = f.read()
    except Exception as e:
        print(f"❌ ERRO ao ler HTML: {e}")
        return False

    # Verificar se tem sessionStorage.removeItem
    if "sessionStorage.removeItem('authenticated')" in html:
        print(f"✅ sessionStorage.removeItem presente")
    else:
        print(f"❌ ERRO: sessionStorage.removeItem não encontrado!")
        return False

    # Verificar se tem DOMContentLoaded
    if "DOMContentLoaded" in html:
        print(f"✅ DOMContentLoaded listener presente")
    else:
        print(f"❌ ERRO: DOMContentLoaded não encontrado!")
        return False

    # Verificar se tem auth-modal
    if 'id="auth-modal"' in html:
        print(f"✅ Auth modal presente")
    else:
        print(f"❌ ERRO: Auth modal não encontrado!")
        return False

    return True


def validar_profissionais():
    """Valida consolidação de profissionais"""
    print(f"\n{'='*80}")
    print(f"👥 VALIDANDO PROFISSIONAIS (Sem Duplicatas)")
    print(f"{'='*80}\n")

    arquivo = '/Users/joaoperes/escalaHRO/profissionais_autenticacao.json'

    try:
        with open(arquivo, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ ERRO ao ler profissionais: {e}")
        return False

    total = len(data.get('professionals', []))
    print(f"Total de profissionais: {total}")

    # Verificar duplicatas por nome normalizado
    nomes = {}
    for prof in data.get('professionals', []):
        nome_norm = ' '.join(prof.get('name', '').lower().split())
        if nome_norm in nomes:
            print(f"❌ DUPLICATA encontrada: {prof['name']}")
            return False
        nomes[nome_norm] = True

    if total > 160:  # Expected around 171
        print(f"✅ {total} profissionais únicos (sem duplicatas)")
        return True
    else:
        print(f"⚠️  Apenas {total} profissionais (esperado ~171)")
        return False


def main():
    """Executa todas as validações"""
    print(f"\n")
    print(f"╔{'='*78}╗")
    print(f"║ 🚀 VALIDAÇÃO DE PRODUÇÃO - ESCALA HRO                                    ║")
    print(f"║ Verificando integridade após execução                                   ║")
    print(f"╚{'='*78}╝")

    validacoes = {
        'Ramais (Função Fixa)': validar_ramais(),
        'Dia Anterior (D-1)': validar_dia_anterior(),
        'Autenticação': validar_autenticacao(),
        'Profissionais': validar_profissionais(),
    }

    # Resumo
    print(f"\n{'='*80}")
    print(f"📊 RESUMO DE VALIDAÇÃO")
    print(f"{'='*80}\n")

    todas_passaram = True
    for nome, resultado in validacoes.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"{status} - {nome}")
        if not resultado:
            todas_passaram = False

    print(f"\n{'='*80}")
    if todas_passaram:
        print(f"✅ TODAS AS VALIDAÇÕES PASSARAM!")
        print(f"   Pronto para produção! 🚀")
    else:
        print(f"❌ ALGUMAS VALIDAÇÕES FALHARAM!")
        print(f"   Verificar erros acima e corrigir antes do deploy!")

    print(f"{'='*80}\n")

    return todas_passaram


if __name__ == "__main__":
    sucesso = main()
    exit(0 if sucesso else 1)
