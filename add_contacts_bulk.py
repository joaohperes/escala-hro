#!/usr/bin/env python3
"""
Script para adicionar/atualizar contatos em massa no arquivo de profissionais
"""

import json
import sys
from pathlib import Path

def normalizar_nome(name):
    """Normaliza nomes para comparação"""
    return ' '.join(name.lower().split())

def adicionar_contatos(arquivo_contatos='novos_contatos.json', arquivo_profissionais='profissionais_autenticacao.json'):
    """Adiciona contatos do arquivo JSON ao arquivo de profissionais"""

    # Carregar novos contatos
    try:
        with open(arquivo_contatos, 'r') as f:
            novos_contatos = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao ler {arquivo_contatos}: {e}")
        return False

    # Carregar profissionais existentes
    try:
        with open(arquivo_profissionais, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao ler {arquivo_profissionais}: {e}")
        return False

    professionals = data['professionals']

    # Mapear profissionais por nome normalizado
    prof_map = {}
    for idx, prof in enumerate(professionals):
        prof_map[normalizar_nome(prof['name'])] = idx

    # Adicionar ou atualizar contatos
    adicionados = 0
    atualizados = 0

    print(f"\n{'='*80}")
    print(f"📝 Processando {len(novos_contatos)} contato(s)...")
    print(f"{'='*80}\n")

    for novo in novos_contatos:
        nome_normalizado = normalizar_nome(novo['name'])

        if nome_normalizado in prof_map:
            # Atualizar profissional existente
            idx = prof_map[nome_normalizado]
            professionals[idx].update(novo)
            print(f"✅ Atualizado: {novo['name']}")
            if novo.get('phone'):
                print(f"   📱 {novo['phone']}")
            atualizados += 1
        else:
            # Adicionar novo profissional
            professionals.append(novo)
            print(f"✅ Adicionado: {novo['name']}")
            if novo.get('phone'):
                print(f"   📱 {novo['phone']}")
            adicionados += 1

    # Salvar arquivo atualizado
    try:
        with open(arquivo_profissionais, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n{'='*80}")
        print(f"✅ Resumo:")
        print(f"   ✅ Adicionados: {adicionados}")
        print(f"   ✅ Atualizados: {atualizados}")
        print(f"   📁 Arquivo salvo: {arquivo_profissionais}")
        print(f"{'='*80}\n")

        return True

    except Exception as e:
        print(f"❌ Erro ao salvar {arquivo_profissionais}: {e}")
        return False

def main():
    arquivo_contatos = 'novos_contatos.json'
    arquivo_profissionais = 'profissionais_autenticacao.json'

    if len(sys.argv) > 1:
        arquivo_contatos = sys.argv[1]

    if len(sys.argv) > 2:
        arquivo_profissionais = sys.argv[2]

    print(f"\n{'='*80}")
    print(f"🔧 ADICIONAR CONTATOS EM MASSA")
    print(f"{'='*80}")
    print(f"📄 Contatos: {arquivo_contatos}")
    print(f"📄 Profissionais: {arquivo_profissionais}")

    if not Path(arquivo_contatos).exists():
        print(f"❌ Arquivo não encontrado: {arquivo_contatos}")
        return 1

    if not Path(arquivo_profissionais).exists():
        print(f"❌ Arquivo não encontrado: {arquivo_profissionais}")
        return 1

    if adicionar_contatos(arquivo_contatos, arquivo_profissionais):
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
