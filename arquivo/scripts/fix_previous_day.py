#!/usr/bin/env python3
"""
Script para corrigir o campo 'anterior' no dashboard
Usa dados do commit anterior (05/11) como dia anterior
"""

import json
import re
import subprocess

def extract_escalas_from_html(html_content):
    """Extrai o objeto escalas do HTML"""
    pattern = r'const escalas = ({.*?});'
    match = re.search(pattern, html_content, re.DOTALL)
    if match:
        escalas_str = match.group(1)
        return json.loads(escalas_str)
    return None

def main():
    print("🔧 Corrigindo dados do 'Dia Anterior'...")

    # 1. Ler index.html atual
    print("📖 Lendo index.html atual...")
    with open('index.html', 'r', encoding='utf-8') as f:
        html_atual = f.read()

    escalas_atual = extract_escalas_from_html(html_atual)
    if not escalas_atual:
        print("❌ Erro ao extrair dados do index.html atual")
        return 1

    print(f"✅ Dados atuais: {escalas_atual['atual']['data']} ({escalas_atual['atual']['total']} registros)")

    # 2. Extrair dados do commit anterior (05/11)
    print("📖 Extraindo dados do commit de ontem (9055118)...")
    try:
        result = subprocess.run(
            ['git', 'show', '9055118:index.html'],
            capture_output=True,
            text=True,
            check=True
        )
        html_anterior = result.stdout
    except Exception as e:
        print(f"❌ Erro ao extrair dados do git: {e}")
        return 1

    escalas_anterior = extract_escalas_from_html(html_anterior)
    if not escalas_anterior:
        print("❌ Erro ao extrair dados do commit anterior")
        return 1

    print(f"✅ Dados anteriores: {escalas_anterior['atual']['data']} ({escalas_anterior['atual']['total']} registros)")

    # 3. Atualizar objeto escalas atual com dados do dia anterior
    escalas_atual['anterior'] = escalas_anterior['atual']

    print(f"\n✅ Atualização:")
    print(f"   - Atual: {escalas_atual['atual']['data']} ({escalas_atual['atual']['total']} registros)")
    print(f"   - Anterior: {escalas_atual['anterior']['data']} ({escalas_atual['anterior']['total']} registros)")

    # 4. Atualizar index.html
    print("\n📝 Atualizando index.html...")
    escalas_json = json.dumps(escalas_atual, ensure_ascii=False)

    # Substituir no HTML
    pattern = r'const escalas = {.*?};'
    replacement = f'const escalas = {escalas_json};'
    html_atualizado = re.sub(pattern, replacement, html_atual, count=1, flags=re.DOTALL)

    # Salvar
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_atualizado)

    print("✅ index.html atualizado com sucesso!")

    # 5. Criar arquivo de backup para o próximo update
    print("\n📦 Criando arquivo de backup para rolling window...")
    backup_data = {
        'atual': escalas_atual['atual'],
        'anterior': escalas_atual['anterior'],
        'data_backup': escalas_atual['data_atualizacao'],
        'hora_backup': escalas_atual['hora_atualizacao']
    }

    with open('/tmp/extracao_inteligente_anterior.json', 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)

    print("✅ Backup criado: /tmp/extracao_inteligente_anterior.json")

    print("\n🎉 Pronto! O 'Dia Anterior' agora deve funcionar corretamente.")
    return 0

if __name__ == '__main__':
    exit(main())
