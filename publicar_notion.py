#!/usr/bin/env python3
"""
Publica os dados extraídos de escalaHRO no Notion
Com organização por setor e limpeza de registros antigos
"""

import json
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# Credentials Notion
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

print(f"\n{'='*100}")
print("📤 PUBLICANDO NO NOTION COM ORGANIZAÇÃO")
print(f"{'='*100}")

# Carregar dados extraídos
with open('/tmp/extracao_inteligente.json', 'r') as f:
    data = json.load(f)

registros = data['registros']
data_escala = data['data']

print(f"📊 Total de registros para publicar: {len(registros)}")
print(f"📅 Data da escala: {data_escala}\n")

# Headers Notion API
headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# === STEP 1: Limpar registros com mais de 2 dias ===
print("🗑️  LIMPANDO REGISTROS ANTIGOS (mantendo apenas últimos 2 dias)...\n")

query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
response = requests.post(query_url, headers=headers, json={"page_size": 100})

if response.status_code == 200:
    existing_records = response.json().get('results', [])

    # Datas válidas: hoje e ontem
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    # Extrair data de hoje da escala (formato: "31 outubro 2025")
    try:
        data_parts = data_escala.split()
        today_day = int(data_parts[0])
        today_month = data_parts[1]
        today_year = int(data_parts[2])

        # Converter nome do mês para número
        meses = {
            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
            'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
            'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
        }
        today_date = datetime(today_year, meses.get(today_month.lower(), 1), today_day)
        yesterday_date = today_date - timedelta(days=1)

        print(f"📅 Mantendo registros de: {today_date.strftime('%d/%m/%Y')} e {yesterday_date.strftime('%d/%m/%Y')}\n")

        # Arquivar registros antigos
        archived = 0
        for item in existing_records:
            props = item.get('properties', {})
            data_field = props.get('Data', {}).get('title', [])

            if data_field:
                data_str = data_field[0].get('text', {}).get('content', '')
                # Se a data não corresponder aos últimos 2 dias, arquivar
                try:
                    data_parts = data_str.split()
                    item_day = int(data_parts[0])
                    item_month = data_parts[1]
                    item_year = int(data_parts[2])
                    item_date = datetime(item_year, meses.get(item_month.lower(), 1), item_day)

                    if item_date not in [today_date, yesterday_date]:
                        page_id = item['id']
                        archive_response = requests.patch(
                            f"https://api.notion.com/v1/pages/{page_id}",
                            headers=headers,
                            json={"archived": True}
                        )
                        if archive_response.status_code == 200:
                            archived += 1
                except:
                    pass

        if archived > 0:
            print(f"✅ Arquivados {archived} registros antigos\n")
        else:
            print(f"✅ Nenhum registro antigo para arquivar\n")
    except Exception as e:
        print(f"⚠️  Erro ao processar datas: {str(e)}\n")

# === STEP 2: Publicar novos registros ===
print("📤 PUBLICANDO NOVOS REGISTROS...\n")

# URL para criar páginas
create_url = "https://api.notion.com/v1/pages"

sucesso = 0
erro = 0

# Função auxiliar para extrair categoria do setor
def get_category(setor):
    """Extrai categoria do setor para organização"""
    setor_lower = setor.lower()

    if any(x in setor_lower for x in ['uti', 'terapia intensiva', 'cuidados intensivos']):
        return 'UTI'
    elif any(x in setor_lower for x in ['gineco', 'obstet', 'parto']):
        return 'Obstetrícia'
    elif any(x in setor_lower for x in ['cirurgia', 'transplante', 'vascular']):
        return 'Cirurgia'
    elif any(x in setor_lower for x in ['clínica', 'comanejo', 'hospitalista']):
        return 'Clínica'
    elif any(x in setor_lower for x in ['emergência', 'pronto', 'urgência']):
        return 'Emergência'
    elif any(x in setor_lower for x in ['ambulatório', 'oncologia']):
        return 'Ambulatório'
    elif any(x in setor_lower for x in ['residência', 'residencia']):
        return 'Residência'
    else:
        return 'Especialidades'

for idx, registro in enumerate(registros, 1):
    try:
        # Extrair categoria do setor
        categoria = get_category(registro['setor'])

        # Preparar dados para Notion
        # Construir Observações de forma mais limpa (SEM EMOJIS)
        observacoes = registro['tipo_turno']
        if registro.get('email'):
            observacoes += f"\nEmail: {registro['email']}"
        if registro.get('phone'):
            observacoes += f"\nTel: {registro['phone']}"

        # Colocar apenas a data na coluna Data (formato: "31 outubro 2025")
        titulo = registro['data']

        page_data = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "Data": {
                    "title": [
                        {
                            "text": {
                                "content": titulo
                            }
                        }
                    ]
                },
                "Profissional": {
                    "rich_text": [
                        {
                            "text": {
                                "content": registro['profissional']
                            }
                        }
                    ]
                },
                "Setor": {
                    "rich_text": [
                        {
                            "text": {
                                "content": registro['setor']
                            }
                        }
                    ]
                },
                "Período": {
                    "rich_text": [
                        {
                            "text": {
                                "content": registro['horario']
                            }
                        }
                    ]
                },
                "Observações": {
                    "rich_text": [
                        {
                            "text": {
                                "content": observacoes
                            }
                        }
                    ]
                }
            }
        }

        # Fazer request para Notion
        response = requests.post(create_url, headers=headers, json=page_data)

        if response.status_code == 200:
            sucesso += 1
            if idx % 10 == 0:
                print(f"✓ {idx:3d}/{len(registros)} - {registro['profissional'][:30]}")
        else:
            erro += 1
            print(f"✗ {idx:3d} - Erro {response.status_code}: {registro['profissional']}")
            print(f"   Resposta: {response.text[:200]}")

    except Exception as e:
        erro += 1
        print(f"✗ {idx:3d} - Exception: {str(e)[:100]}")

print(f"\n{'='*100}")
print(f"✅ Publicação Concluída!")
print(f"   ✓ Sucesso: {sucesso}/{len(registros)}")
print(f"   ✗ Erros: {erro}/{len(registros)}")
print(f"{'='*100}\n")

if sucesso == len(registros):
    print("🎉 TODOS OS REGISTROS FORAM PUBLICADOS COM SUCESSO!")
else:
    print(f"⚠️  {erro} registros falharam. Verifique os erros acima.")
