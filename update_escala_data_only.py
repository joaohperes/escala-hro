#!/usr/bin/env python3
"""
Script to UPDATE ONLY the escalas data in an existing HTML file
WITHOUT regenerating the entire template
This preserves all JavaScript improvements while keeping data fresh
"""

import json
import re
from pathlib import Path
from datetime import datetime

def extract_escalas_from_json(json_file):
    """Load escalas data from JSON file"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar escalas de {json_file}: {e}")
        return None

def update_html_escalas_data(html_file, escalas_data, output_files):
    """Update ONLY the escalas data in HTML file, preserving all other content"""
    try:
        # Read the current HTML
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Find and replace the escalas object
        escalas_json_str = json.dumps(escalas_data, ensure_ascii=False)

        # Pattern to find: const escalas = {...}
        # This is tricky because the JSON is on one line, so we look for the pattern
        pattern = r'const escalas = \{.*?\};'

        # Use re.DOTALL to match across newlines if needed
        replacement = f'const escalas = {escalas_json_str};'

        # Check if pattern exists
        if not re.search(pattern, html_content, re.DOTALL):
            print("❌ Padrão 'const escalas = ' não encontrado no HTML!")
            return False

        # Replace it
        new_html_content = re.sub(pattern, replacement, html_content, count=1, flags=re.DOTALL)

        # Verify replacement happened
        if new_html_content == html_content:
            print("❌ Falha ao substituir dados de escalas!")
            return False

        # Save to all output files
        for output_file in output_files:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(new_html_content)
                print(f"✅ Dados atualizados em: {output_file}")
            except Exception as e:
                print(f"⚠️  Erro ao salvar {output_file}: {e}")

        return True

    except Exception as e:
        print(f"❌ Erro ao atualizar HTML: {e}")
        return False

def main():
    print("🔄 Atualizando dados de escalas (apenas JSON, preservando JavaScript)...")

    # Data source
    json_file = '/tmp/extracao_inteligente.json'
    html_file = '/Users/joaoperes/escalaHRO/index.html'
    output_files = [
        '/Users/joaoperes/escalaHRO/index.html',
        '/Users/joaoperes/escalaHRO/docs/index.html'
    ]

    # Load escalas data
    escalas_data = extract_escalas_from_json(json_file)
    if not escalas_data:
        print(f"⚠️  Usando dados do HTML existente")
        return 1

    # Update HTML
    if update_html_escalas_data(html_file, escalas_data, output_files):
        print(f"✅ Escalas atualizadas com sucesso!")
        print(f"📊 Profissionais na data 'atual': {escalas_data.get('atual', {}).get('total', 0)}")
        return 0
    else:
        print("❌ Falha ao atualizar escalas")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
