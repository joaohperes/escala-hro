#!/usr/bin/env python3
"""
Converter: Adapta saída de extracao_inteligente.py para formato esperado
pela gerar_dashboard_executivo.py

Lê: /tmp/extracao_inteligente.json
Escreve: /tmp/escalas_multiplos_dias.json

HISTÓRICO: Mantém registros dos últimos 3 dias para consulta no dashboard
- Anterior: Dia anterior
- Atual: Dia de hoje
- Próxima: Próximo dia (quando disponível)
"""

import json
import os
from datetime import datetime, timedelta

def obter_dados_historico(data_obj):
    """Obtém dados históricos do arquivo anterior se existir"""
    try:
        with open('/tmp/escalas_multiplos_dias.json', 'r', encoding='utf-8') as f:
            historico = json.load(f)

        # Se o histórico existe, podemos usar o dia anterior dele como "anterior"
        # Isso mantém um histórico de até 3 dias
        return historico
    except FileNotFoundError:
        return None

def converter():
    """Converte formato de saída para formato esperado pelo dashboard"""

    try:
        # Lê dados da extração inteligente
        try:
            with open('/tmp/extracao_inteligente.json', 'r', encoding='utf-8') as f:
                dados_extraidos = json.load(f)
        except FileNotFoundError:
            print("❌ Arquivo /tmp/extracao_inteligente.json não encontrado")
            # Salvar status de falha
            resultado_falha = {
                'data_atualizacao': datetime.now().strftime('%d/%m/%Y'),
                'hora_atualizacao': datetime.now().strftime('%H:%M:%S'),
                'status_atualizacao': 'erro',
                'mensagem_erro': 'Arquivo de extração não encontrado',
                'anterior': {},
                'atual': {},
                'proxima': {}
            }
            try:
                with open('/tmp/escalas_multiplos_dias.json', 'w', encoding='utf-8') as f:
                    json.dump(resultado_falha, f, ensure_ascii=False, indent=2)
            except:
                pass
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

        # Obtém histórico anterior para manter registros dos últimos dias
        historico_anterior = obter_dados_historico(data_obj)

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

        # Manter histórico: se temos dados anteriores, reutilizamos
        # Isso permite que o dashboard sempre mostre os últimos 3 dias

        dados_anterior = {'registros': [], 'total': 0}

        # Se temos histórico, pegamos o dia anterior do histórico anterior
        if historico_anterior and 'anterior' in historico_anterior:
            dados_anterior = {
                'registros': historico_anterior['anterior'].get('registros', []),
                'total': historico_anterior['anterior'].get('total', 0)
            }

        resultado = {
            'data_atualizacao': formatar_data_simples(data_obj),
            'hora_atualizacao': datetime.now().strftime('%H:%M:%S'),
            'status_atualizacao': 'sucesso',
            'anterior': {
                'data': formatar_data_longa(data_anterior),
                'data_simples': formatar_data_simples(data_anterior),
                'registros': dados_anterior['registros'],
                'total': dados_anterior['total'],
                'nota': 'Dados do dia anterior para consulta histórica'
            },
            'atual': {
                'data': data_str,
                'data_simples': formatar_data_simples(data_obj),
                'registros': registros,
                'total': len(registros),
                'nota': 'Dados de hoje extraídos de escala.med.br'
            },
            'proxima': {
                'data': formatar_data_longa(data_proxima),
                'data_simples': formatar_data_simples(data_proxima),
                'registros': [],
                'total': 0,
                'nota': 'Próximo dia (dados indisponíveis no momento)'
            }
        }

        # Salvar no formato esperado
        try:
            with open('/tmp/escalas_multiplos_dias.json', 'w', encoding='utf-8') as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2)

            print(f"✅ Converter concluído com sucesso!")
            print(f"📍 Entrada: /tmp/extracao_inteligente.json")
            print(f"📍 Saída: /tmp/escalas_multiplos_dias.json")
            print(f"\n📊 HISTÓRICO DE ESCALAS (últimos 3 dias):")
            print(f"   📅 Anterior ({resultado['anterior']['data_simples']}): {resultado['anterior']['total']} registros")
            print(f"   📅 Atual ({resultado['atual']['data_simples']}): {resultado['atual']['total']} registros ⭐")
            print(f"   📅 Próxima ({resultado['proxima']['data_simples']}): {resultado['proxima']['total']} registros")
            print(f"\n💾 Dashboard manterá histórico dos últimos 3 dias para consulta")
            return True

        except Exception as e:
            print(f"❌ Erro ao salvar arquivo convertido: {e}")
            # Tentar salvar status de falha mesmo assim
            try:
                resultado_falha = {
                    'data_atualizacao': formatar_data_simples(data_obj),
                    'hora_atualizacao': datetime.now().strftime('%H:%M:%S'),
                    'status_atualizacao': 'erro',
                    'mensagem_erro': str(e),
                    'anterior': {},
                    'atual': {},
                    'proxima': {}
                }
                with open('/tmp/escalas_multiplos_dias.json', 'w', encoding='utf-8') as f:
                    json.dump(resultado_falha, f, ensure_ascii=False, indent=2)
            except:
                pass
            return False

    except Exception as e:
        print(f"❌ Erro geral no converter: {e}")
        try:
            resultado_falha = {
                'data_atualizacao': datetime.now().strftime('%d/%m/%Y'),
                'hora_atualizacao': datetime.now().strftime('%H:%M:%S'),
                'status_atualizacao': 'erro',
                'mensagem_erro': str(e),
                'anterior': {},
                'atual': {},
                'proxima': {}
            }
            with open('/tmp/escalas_multiplos_dias.json', 'w', encoding='utf-8') as f:
                json.dump(resultado_falha, f, ensure_ascii=False, indent=2)
        except:
            pass
        return False

if __name__ == '__main__':
    sucesso = converter()
    exit(0 if sucesso else 1)
