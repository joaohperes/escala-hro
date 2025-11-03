#!/usr/bin/env python3
"""
Publica dados extraídos no Notion
"""

import json
import requests
import os
from datetime import datetime, timedelta

# Usar variáveis de ambiente (do GitHub Secrets)
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

print(f"\n{'='*100}")
print("📤 PUBLICANDO NO NOTION")
print(f"{'='*100}\n")

# Carregar dados extraídos
with open('/tmp/extracao_inteligente.json', 'r') as f:
    data = json.load(f)

registros = data['registros']
data_escala = data['data']

print(f"📊 Total de registros: {len(registros)}")
print(f"📅 Data da escala: {data_escala}\n")

# Headers da API Notion
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# URL base
query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
create_url = "https://api.notion.com/v1/pages"

# === STEP 1: Limpar registros com mais de 2 dias ===
print("🗑️  Limpando registros antigos...\n")

response = requests.post(query_url, headers=headers, json={"page_size": 100})

if response.status_code == 200:
    existing_records = response.json().get('results', [])

    today = datetime.now()
    yesterday = today - timedelta(days=1)

    try:
        data_parts = data_escala.split()
        today_day = int(data_parts[0])
        today_month = data_parts[1]
        today_year = int(data_parts[2])

        meses = {
            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
            'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
            'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
        }
        today_date = datetime(today_year, meses.get(today_month.lower(), 1), today_day)
        yesterday_date = today_date - timedelta(days=1)

        archived = 0
        for item in existing_records:
            props = item.get('properties', {})
            data_field = props.get('Data', {}).get('title', [])

            if data_field:
                data_str = data_field[0].get('text', {}).get('content', '')
                try:
                    data_parts = data_str.split()
                    item_day = int(data_parts[0])
                    item_month = data_parts[1]
                    item_year = int(data_parts[2])
                    item_date = datetime(item_year, meses.get(item_month.lower(), 1), item_day)

                    if item_date not in [today_date, yesterday_date]:
                        page_id = item['id']
                        requests.patch(
                            f"https://api.notion.com/v1/pages/{page_id}",
                            headers=headers,
                            json={"archived": True}
                        )
                        archived += 1
                except:
                    pass

        if archived > 0:
            print(f"✅ Arquivados {archived} registros antigos\n")
    except Exception as e:
        print(f"⚠️  Erro ao processar datas: {str(e)}\n")

# === STEP 2: Publicar novos registros ===
print("📤 Publicando novos registros...\n")

sucesso = 0
erro = 0

for idx, registro in enumerate(registros, 1):
    try:
        page_data = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "Data": {
                    "title": [{"text": {"content": registro['data']}}]
                },
                "Profissional": {
                    "rich_text": [{"text": {"content": registro['profissional']}}]
                },
                "Setor": {
                    "rich_text": [{"text": {"content": registro['setor']}}]
                },
                "Período": {
                    "rich_text": [{"text": {"content": registro['horario']}}]
                },
                "Observações": {
                    "rich_text": [{"text": {"content": registro['tipo_turno']}}]
                }
            }
        }

        response = requests.post(create_url, headers=headers, json=page_data)

        if response.status_code == 200:
            sucesso += 1
            if idx % 20 == 0:
                print(f"✓ {idx:3d}/{len(registros)} - {registro['profissional'][:30]}")
        else:
            erro += 1

    except Exception as e:
        erro += 1

print(f"\n{'='*100}")
print(f"✅ Publicação Concluída!")
print(f"   ✓ Sucesso: {sucesso}/{len(registros)}")
print(f"   ✗ Erros: {erro}/{len(registros)}")
print(f"{'='*100}\n")

if sucesso == len(registros):
    print("🎉 TODOS OS REGISTROS FORAM PUBLICADOS COM SUCESSO!")
