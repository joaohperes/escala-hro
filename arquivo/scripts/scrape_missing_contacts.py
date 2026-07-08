#!/usr/bin/env python3
"""
Script para scraping de contatos de profissionais faltantes
Tenta múltiplas fontes para encontrar telefones
"""

import json
import re
import os
from pathlib import Path

# Lista de profissionais faltando contato
MISSING_PROFILES = [
    "Bianca Soder Wolschick",
    "Fabricio Praca Consalter",
    "Fernando Luiz de Melo Bernardi",
    "Graziela Fatima Battistel",
    "Jamile Rosset Mocellin",
    "Jessica Aparecida Battistel",
    "João Roberto Munhoz Zorzetto",
    "Marcelo Eduardo Heinig",
    "Marcia Akemi Nishino",
    "Matheus Toldo Kazerski",
    "Rodrigo Sponchiado Rocha",
    "Rovani Jose Rinaldi Camargo",
    "Vinicius Rubin",
    "Waleska Furini"
]

def procurar_no_arquivo_escalas(prof_name):
    """Tenta encontrar email ou telefone no arquivo de escalas"""
    try:
        with open('/Users/joaoperes/escalaHRO/escalas_multiplos_dias.json', 'r') as f:
            data = json.load(f)
        
        # Procura em 'atual' e 'anterior'
        for key in ['atual', 'anterior']:
            if key in data:
                for reg in data[key].get('registros', []):
                    if reg.get('profissional', '').lower() == prof_name.lower():
                        return {
                            'email': reg.get('email', ''),
                            'phone': reg.get('phone', '')
                        }
    except Exception as e:
        print(f"⚠️  Erro ao procurar em escalas_multiplos_dias.json: {e}")
    
    return None

def normalizar_nome(name):
    """Normaliza nomes para comparação"""
    return ' '.join(name.lower().split())

def main():
    print("🔍 Scraping de contatos faltantes...\n")
    
    # Carregar profissionais existentes
    with open('/Users/joaoperes/escalaHRO/profissionais_autenticacao.json', 'r') as f:
        data = json.load(f)
    
    professionals = data['professionals']
    prof_dict = {normalizar_nome(p['name']): p for p in professionals}
    
    # Procurar contatos para cada profissional faltante
    encontrados = []
    
    print(f"📞 Procurando contatos para {len(MISSING_PROFILES)} profissionais...\n")
    
    for prof_name in MISSING_PROFILES:
        print(f"🔎 Procurando: {prof_name}")
        
        # Tentar encontrar em escalas_multiplos_dias.json
        result = procurar_no_arquivo_escalas(prof_name)
        
        if result and (result['email'] or result['phone']):
            print(f"   ✅ Encontrado em escalas_multiplos_dias.json")
            if result['email']:
                print(f"      Email: {result['email']}")
            if result['phone']:
                print(f"      Telefone: {result['phone']}")
                
                # Extrair last4 do telefone
                phone_numbers = re.findall(r'\d{4,5}$', result['phone'].replace(' ', '').replace('-', ''))
                last4 = phone_numbers[0][-4:] if phone_numbers else ''
                
                new_prof = {
                    'name': prof_name,
                    'email': result['email'] if result['email'] else '',
                    'phone': result['phone'] if result['phone'] else '',
                    'last4': last4
                }
                
                encontrados.append(new_prof)
        else:
            print(f"   ⚠️  Não encontrado em nenhuma fonte")
        
        print()
    
    # Salvar novos contatos
    if encontrados:
        print(f"\n✅ {len(encontrados)} contato(s) encontrado(s)")
        print("\n📝 Novos profissionais a adicionar:")
        for prof in encontrados:
            print(f"  - {prof['name']}: {prof['phone']} ({prof['last4']})")
        
        # Adicionar aos profissionais existentes
        for new_prof in encontrados:
            # Verificar se já existe
            if not any(normalizar_nome(p['name']) == normalizar_nome(new_prof['name']) for p in professionals):
                professionals.append(new_prof)
                print(f"✅ Adicionado: {new_prof['name']}")
            else:
                print(f"⏭️  Pulado (já existe): {new_prof['name']}")
        
        # Salvar arquivo atualizado
        with open('/Users/joaoperes/escalaHRO/profissionais_autenticacao.json', 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Arquivo atualizado: profissionais_autenticacao.json")
    else:
        print(f"\n⚠️  Nenhum contato encontrado para adicionar")

if __name__ == "__main__":
    main()
