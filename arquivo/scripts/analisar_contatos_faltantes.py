#!/usr/bin/env python3
"""
Análise DINÂMICA de profissionais novos e contatos faltantes.

Compara a escala extraída (do scrape) com a base de cadastros
profissionais_autenticacao.json e descobre automaticamente:
  - Profissionais NOVOS: estão na escala mas não têm cadastro nenhum.
  - Contatos FALTANTES: estão cadastrados (ou na escala) mas sem telefone.

Não usa nenhuma lista hardcoded — a lista de faltantes é derivada dos dados.

Fontes da escala (usa a primeira que existir, nesta ordem):
  1. /tmp/extracao_inteligente.json            (extração fresca do dia)
  2. data/extracao_inteligente_anterior_cache.json  (cache persistente)
  3. escalas_multiplos_dias.json               (histórico)

Uso:
    python3 analisar_contatos_faltantes.py
"""

import json
import os
import unicodedata

BASE = os.path.dirname(os.path.abspath(__file__))
PROF_FILE = os.path.join(BASE, 'profissionais_autenticacao.json')

ESCALA_SOURCES = [
    '/tmp/extracao_inteligente.json',
    os.path.join(BASE, 'data', 'extracao_inteligente_anterior_cache.json'),
    os.path.join(BASE, 'escalas_multiplos_dias.json'),
]


def normalizar_nome(name):
    """Normaliza nome para comparação: minúsculo, sem acento, espaços colapsados."""
    if not name:
        return ''
    nfkd = unicodedata.normalize('NFKD', name)
    sem_acento = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return ' '.join(sem_acento.lower().split())


def carregar_escala():
    """Carrega registros da escala a partir da primeira fonte disponível."""
    for path in ESCALA_SOURCES:
        if not os.path.isfile(path):
            continue
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"⚠️  Erro ao ler {path}: {e}")
            continue

        registros = []
        if isinstance(data, dict) and 'registros' in data:
            registros = data['registros']
        elif isinstance(data, dict):
            # formato {atual: {registros: []}, anterior: {...}}
            for key in ('atual', 'anterior'):
                bloco = data.get(key)
                if isinstance(bloco, dict):
                    registros.extend(bloco.get('registros', []))
        elif isinstance(data, list):
            registros = data

        if registros:
            print(f"📂 Fonte da escala: {path}")
            print(f"   {len(registros)} registro(s) carregado(s)\n")
            return registros, path

    print("❌ Nenhuma fonte de escala encontrada. Rode a extração primeiro.")
    return [], None


def main():
    print("=" * 80)
    print("🔍 ANÁLISE DINÂMICA — NOVOS PROFISSIONAIS E CONTATOS FALTANTES")
    print("=" * 80 + "\n")

    registros, fonte = carregar_escala()
    if not registros:
        return 1

    with open(PROF_FILE, 'r', encoding='utf-8') as f:
        prof_data = json.load(f)
    professionals = prof_data['professionals']

    # Índice de cadastrados por nome normalizado
    cad_index = {normalizar_nome(p['name']): p for p in professionals}

    # Pessoas únicas na escala (com o último setor/telefone visto)
    escala = {}
    for reg in registros:
        nome = (reg.get('profissional') or '').strip()
        if not nome:
            continue
        chave = normalizar_nome(nome)
        if chave not in escala:
            escala[chave] = {
                'name': nome,
                'setor': reg.get('setor', ''),
                'phone': reg.get('phone', ''),
                'email': reg.get('email', ''),
            }
        else:
            # preenche telefone/email se aparecer em algum registro
            if not escala[chave]['phone'] and reg.get('phone'):
                escala[chave]['phone'] = reg['phone']
            if not escala[chave]['email'] and reg.get('email'):
                escala[chave]['email'] = reg['email']

    novos = []          # na escala, sem cadastro
    faltam_contato = []  # na escala, cadastrado, mas sem telefone

    for chave, info in sorted(escala.items(), key=lambda kv: kv[1]['name']):
        cad = cad_index.get(chave)
        if cad is None:
            novos.append(info)
        elif not cad.get('phone'):
            faltam_contato.append({**info, 'phone_escala': info.get('phone', '')})

    # Cadastrados sem telefone que NÃO estão na escala atual (info extra)
    cadastrados_sem_tel = [
        p['name'] for p in professionals
        if not p.get('phone') and normalizar_nome(p['name']) not in escala
    ]

    print(f"📊 RESUMO")
    print(f"   Profissionais na escala (únicos): {len(escala)}")
    print(f"   Cadastrados na base:              {len(professionals)}")
    print(f"   🆕 NOVOS (na escala, sem cadastro): {len(novos)}")
    print(f"   📞 Contatos faltantes (na escala): {len(faltam_contato)}")
    print(f"   📞 Cadastrados sem telefone (fora da escala atual): {len(cadastrados_sem_tel)}\n")

    if novos:
        print("=" * 80)
        print("🆕 NOVOS PROFISSIONAIS (precisam ser cadastrados)")
        print("=" * 80)
        for n in novos:
            tel = n['phone'] or '❌ sem telefone'
            print(f"  - {n['name']:<40} | {n['setor']:<35} | {tel}")
        print()

    if faltam_contato:
        print("=" * 80)
        print("📞 CONTATOS FALTANTES (cadastrados sem telefone, na escala atual)")
        print("=" * 80)
        for n in faltam_contato:
            print(f"  - {n['name']:<40} | {n['setor']}")
        print()

    if cadastrados_sem_tel:
        print("=" * 80)
        print("📞 CADASTRADOS SEM TELEFONE (não estão na escala atual)")
        print("=" * 80)
        for nome in sorted(cadastrados_sem_tel):
            print(f"  - {nome}")
        print()

    # Salva resultado para uso por outros scripts / commit
    out = {
        'fonte_escala': fonte,
        'novos_profissionais': novos,
        'contatos_faltantes': faltam_contato,
        'cadastrados_sem_telefone_fora_escala': cadastrados_sem_tel,
    }
    out_path = os.path.join(BASE, 'contatos_faltantes_dinamico.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"✅ Resultado salvo em: {out_path}")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
