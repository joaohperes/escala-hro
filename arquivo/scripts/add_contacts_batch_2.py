#!/usr/bin/env python3
"""
Script para adicionar novos contatos em lote
Adiciona 8 profissionais com informações completas
"""

import json
import os
from pathlib import Path

# Novos contatos a adicionar
NEW_CONTACTS = [
    {
        "name": "Emeline Moreira Cabral",
        "email": "emelinemoreira@hotmail.com",
        "phone": "(49) 99958-0101",
        "last4": "0101"
    },
    {
        "name": "Barbara Anahy Vinhas Bazzano",
        "email": "bbazzano@icloud.com",
        "phone": "(45) 99104-9074",
        "last4": "9074"
    },
    {
        "name": "Juliano Cesar Huf Farias",
        "email": "julianofarias@ymail.com",
        "phone": "(49) 99942-4165",
        "last4": "4165"
    },
    {
        "name": "Rodrigo Sponchiado Rocha",
        "email": "drrodrigosr121179@gmail.com",
        "phone": "(49) 99156-1330",
        "last4": "1330"
    },
    {
        "name": "Maria Del Pilar Telesca Valente",
        "email": "mtelesca@hotmail.com",
        "phone": "(49) 99158-8001",
        "last4": "8001"
    },
    {
        "name": "Giovani Santin",
        "email": "drgiovanisantin@hotmail.com",
        "phone": "(49) 99963-6866",
        "last4": "6866"
    },
    {
        "name": "Vicente Gregorio Restelli",
        "email": "vgrestelli@yahoo.com.br",
        "phone": "(49) 99123-4545",
        "last4": "4545"
    },
    {
        "name": "Fernando Luiz de Melo Bernardi",
        "email": "ferber08@gmail.com",
        "phone": "(49) 99825-0730",
        "last4": "0730"
    },
]

def add_contacts():
    """Adiciona novos contatos ao arquivo de profissionais"""
    arquivo = '/Users/joaoperes/escalaHRO/profissionais_autenticacao.json'

    print(f"\n{'='*80}")
    print(f"📝 ADICIONANDO NOVOS CONTATOS")
    print(f"{'='*80}\n")

    try:
        with open(arquivo, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ ERRO ao ler arquivo: {e}")
        return False

    # Normalizar nomes existentes para comparação
    existing_names = {
        ' '.join(prof['name'].lower().split()): prof['name']
        for prof in data['professionals']
    }

    added_count = 0
    skipped_count = 0

    print(f"Adicionando {len(NEW_CONTACTS)} novos contatos...\n")

    for contact in NEW_CONTACTS:
        name_normalized = ' '.join(contact['name'].lower().split())

        # Verificar se já existe
        if name_normalized in existing_names:
            print(f"⏭️  PULANDO: {contact['name']} (já existe)")
            skipped_count += 1
            continue

        # Adicionar novo contato
        data['professionals'].append(contact)
        print(f"✅ ADICIONADO: {contact['name']}")
        added_count += 1

    # Salvar arquivo atualizado
    try:
        with open(arquivo, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n{'='*80}")
        print(f"✅ SUCESSO!")
        print(f"   - Adicionados: {added_count} novos contatos")
        print(f"   - Pulados (duplicados): {skipped_count}")
        print(f"   - Total de profissionais: {len(data['professionals'])}")
        print(f"{'='*80}\n")
        return True
    except Exception as e:
        print(f"\n❌ ERRO ao salvar arquivo: {e}")
        return False

if __name__ == "__main__":
    sucesso = add_contacts()
    exit(0 if sucesso else 1)
