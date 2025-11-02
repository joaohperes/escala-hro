#!/usr/bin/env python3
"""
Converter: Adapta saída de extracao_inteligente.py para formato esperado
pela gerar_dashboard_executivo.py

Lê: /tmp/extracao_inteligente.json
Escreve: /tmp/escalas_multiplos_dias.json
"""

import json
from datetime import datetime, timedelta

def converter():
    """Converte formato de saída para formato esperado pelo dashboard"""

    try:
        # Lê dados da extração inteligente
        with open('/tmp/extracao_inteligente.json', 'r', encoding='utf-8') as f:
            dados_extraidos = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo /tmp/extracao_inteligente.json não encontrado")
        return False

    registros = dados_extraidos.get('registros', [])
    data_str = dados_extraidos.get('data', 'Desconhecido')

    # Parse data para gerar datas anterior e próxima
    try:
        # Tentar diferentes formatos
        data_obj = None
        for fmt in ['%d %B %Y', '%d de %B de %Y', '%d novembro %Y', '%d de novembro de %Y']:
            try:
                # Substituir nomes de mês em português
                data_normalizada = data_str
                meses = {
                    'janeiro': 'January', 'fevereiro': 'February', 'março': 'March',
                    'abril': 'April', 'maio': 'May', 'junho': 'June',
                    'julho': 'July', 'agosto': 'August', 'setembro': 'September',
                    'outubro': 'October', 'novembro': 'November', 'dezembro': 'December'
                }
                for pt, en in meses.items():
                    data_normalizada = data_normalizada.replace(pt, en).replace(pt.capitalize(), en)

                data_obj = datetime.strptime(data_normalizada, '%d %B %Y')
                break
            except:
                continue

        if not data_obj:
            # Se não conseguir fazer parse, usar hoje
            data_obj = datetime.now()
            print(f"⚠️  Não conseguiu fazer parse de '{data_str}', usando data de hoje")

    except:
        data_obj = datetime.now()
        print(f"⚠️  Erro ao processar data, usando data de hoje")

    data_anterior = data_obj - timedelta(days=1)
    data_proxima = data_obj + timedelta(days=1)

    # Converter para formato string
    def formatar_data_simples(dt):
        return dt.strftime('%d/%m/%Y')

    def formatar_data_longa(dt):
        meses_pt = {
            'January': 'janeiro', 'February': 'fevereiro', 'March': 'março',
            'April': 'abril', 'May': 'maio', 'June': 'junho',
            'July': 'julho', 'August': 'agosto', 'September': 'setembro',
            'October': 'outubro', 'November': 'novembro', 'December': 'dezembro'
        }
        mes_en = dt.strftime('%B')
        mes_pt = meses_pt.get(mes_en, mes_en.lower())
        return dt.strftime(f'%d {mes_pt} %Y')

    # Separar registros por tipo de turno para gerar dados realistas das datas anteriores/próximas
    # Para hoje, usar dados reais. Para outras datas, usar dados simulados (cópia)

    resultado = {
        'anterior': {
            'data': formatar_data_longa(data_anterior),
            'data_simples': formatar_data_simples(data_anterior),
            'registros': [],  # Dados anteriores não estão disponíveis, deixar vazio
            'total': 0
        },
        'atual': {
            'data': data_str,
            'data_simples': formatar_data_simples(data_obj),
            'registros': registros,
            'total': len(registros)
        },
        'proxima': {
            'data': formatar_data_longa(data_proxima),
            'data_simples': formatar_data_simples(data_proxima),
            'registros': [],  # Dados futuros não estão disponíveis, deixar vazio
            'total': 0
        }
    }

    # Salvar no formato esperado
    try:
        with open('/tmp/escalas_multiplos_dias.json', 'w', encoding='utf-8') as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

        print(f"✅ Converter concluído!")
        print(f"📍 Entrada: /tmp/extracao_inteligente.json")
        print(f"📍 Saída: /tmp/escalas_multiplos_dias.json")
        print(f"📊 Registros de hoje ({resultado['atual']['data_simples']}): {resultado['atual']['total']}")
        return True

    except Exception as e:
        print(f"❌ Erro ao salvar arquivo convertido: {e}")
        return False

if __name__ == '__main__':
    sucesso = converter()
    exit(0 if sucesso else 1)
