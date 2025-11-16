#!/usr/bin/env python3
"""
Script para remover duplicatas de profissionais em profissionais_autenticacao.json
Mantém apenas uma entrada por profissional (a com mais informações completas)
"""

import json
from pathlib import Path

def normalizar_nome(name):
    """Normaliza nomes para comparação"""
    return ' '.join(name.lower().split())

def remover_duplicatas():
    """Remove entradas duplicadas mantendo a mais completa"""

    arquivo = '/Users/joaoperes/escalaHRO/profissionais_autenticacao.json'

    # Carregar dados
    with open(arquivo, 'r') as f:
        data = json.load(f)

    professionals = data['professionals']

    print(f"\n{'='*80}")
    print(f"🔍 REMOVENDO DUPLICATAS DE PROFISSIONAIS")
    print(f"{'='*80}")
    print(f"📊 Total de entradas ANTES: {len(professionals)}\n")

    # Mapear profissionais por nome normalizado
    # Manter a entrada com mais campos preenchidos
    prof_map = {}

    for idx, prof in enumerate(professionals):
        nome_normalizado = normalizar_nome(prof['name'])

        # Contar campos preenchidos
        campos_preenchidos = sum([
            bool(prof.get('name')),
            bool(prof.get('email')),
            bool(prof.get('phone')),
            bool(prof.get('last4'))
        ])

        if nome_normalizado in prof_map:
            # Comparar com entrada existente
            idx_existente, prof_existente, campos_existente = prof_map[nome_normalizado]

            if campos_preenchidos > campos_existente:
                # Nova entrada é mais completa, substituir
                print(f"⚠️  Duplicata encontrada: {prof['name']}")
                print(f"   Substituindo entrada (tinha {campos_existente} campos, nova tem {campos_preenchidos})")
                prof_map[nome_normalizado] = (idx, prof, campos_preenchidos)
            else:
                print(f"⚠️  Duplicata encontrada: {prof['name']}")
                print(f"   Mantendo entrada anterior ({campos_existente} campos, nova tem {campos_preenchidos})")
        else:
            # Primeira ocorrência
            prof_map[nome_normalizado] = (idx, prof, campos_preenchidos)

    # Criar lista consolidada
    professionals_consolidados = [prof for _, prof, _ in prof_map.values()]
    professionals_consolidados.sort(key=lambda x: normalizar_nome(x['name']))

    # Atualizar data
    data['professionals'] = professionals_consolidados

    # Salvar
    with open(arquivo, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*80}")
    print(f"✅ RESULTADO:")
    print(f"   Total de entradas DEPOIS: {len(professionals_consolidados)}")
    print(f"   Duplicatas removidas: {len(professionals) - len(professionals_consolidados)}")
    print(f"   Arquivo salvo: {arquivo}")
    print(f"{'='*80}\n")

    return len(professionals) - len(professionals_consolidados)

if __name__ == "__main__":
    remover_duplicatas()
