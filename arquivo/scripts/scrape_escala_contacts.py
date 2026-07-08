#!/usr/bin/env python3
"""
Script para scraping de contatos do site escala.med.br
Extrai informações de profissionais diretamente da escala da semana
"""

import os
import json
import time
import re
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

ESCALA_USERNAME = os.getenv('ESCALA_USERNAME')
ESCALA_PASSWORD = os.getenv('ESCALA_PASSWORD')

# Profissionais que faltam contato
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

def normalizar_nome(name):
    return ' '.join(name.lower().split())

class ContatoScraper:
    def __init__(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except:
            self.driver = webdriver.Chrome(options=chrome_options)

    def login(self):
        """Faz login no site escala.med.br"""
        print(f"🔐 Fazendo login...")
        self.driver.get("https://escala.med.br/painel/#!/login")
        time.sleep(4)

        try:
            # Tentar encontrar campo de email/usuário
            username_input = None
            try:
                username_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='email']")
            except:
                try:
                    username_input = self.driver.find_element(By.XPATH, "//input[@placeholder*='usuário' or @placeholder*='email']")
                except:
                    username_input = self.driver.find_element(By.XPATH, "//input[@type='text']")

            username_input.send_keys(ESCALA_USERNAME)
            time.sleep(1)

            # Campo de senha
            password = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            password.send_keys(ESCALA_PASSWORD)
            time.sleep(1)

            # Encontrar e clicar botão de login (pode ter vários seletores)
            login_btn = None
            try:
                login_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            except:
                try:
                    login_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login') or contains(text(), 'Entrar')]")
                except:
                    login_btn = self.driver.find_element(By.XPATH, "//button[@ng-click or @onclick]")

            login_btn.click()
            time.sleep(5)

            print("✅ Login realizado com sucesso!")
            return True
        except Exception as e:
            print(f"❌ Erro no login: {e}")
            return False

    def extrair_contatos_da_escala(self):
        """Extrai contatos de profissionais do site"""
        print(f"\n🔍 Navegando para a escala médica...\n")

        contatos_encontrados = {}

        try:
            # Navegar para a escala
            self.driver.get("https://escala.med.br/painel/#!/")

            # Aguardar carregamento dos dados (página usa AngularJS)
            print("⏳ Aguardando carregamento de dados da escala...")
            time.sleep(10)

            # Obter todo o HTML da página
            page_html = self.driver.page_source

            print(f"📄 Página carregada, tamanho: {len(page_html)} caracteres\n")
            print(f"🔍 Procurando contatos de profissionais na escala...\n")

            # Procurar por cada profissional
            for missing_prof in MISSING_PROFILES:
                print(f"  🔎 Procurando: {missing_prof}")

                if missing_prof in page_html:
                    print(f"     ✅ Encontrado no HTML")

                    # Procurar padrão de telefone próximo ao nome
                    # Estratégia: encontrar contexto ao redor do nome
                    prof_index = page_html.find(missing_prof)

                    # Extrair contexto: 500 caracteres antes e depois
                    start = max(0, prof_index - 500)
                    end = min(len(page_html), prof_index + 500)
                    context = page_html[start:end]

                    # Procurar por padrões de telefone na área do contexto
                    phones = re.findall(r'\(\d{2}\)\s*\d{4,5}-\d{4}', context)

                    if phones:
                        phone = phones[0]
                        last4 = phone[-4:]

                        print(f"     📱 Telefone encontrado: {phone}")

                        contatos_encontrados[missing_prof] = {
                            'name': missing_prof,
                            'email': '',
                            'phone': phone,
                            'last4': last4
                        }
                    else:
                        # Tentar procurar elementos do Selenium como alternativa
                        try:
                            elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{missing_prof}')]")
                            if elements:
                                elemento = elements[0]
                                parent = elemento.find_element(By.XPATH, ".//ancestor::*[contains(@class, 'row') or contains(@class, 'cell')]")
                                parent_html = parent.get_attribute('innerHTML')
                                phones = re.findall(r'\(\d{2}\)\s*\d{4,5}-\d{4}', parent_html)

                                if phones:
                                    phone = phones[0]
                                    last4 = phone[-4:]
                                    print(f"     📱 Telefone encontrado (Selenium): {phone}")

                                    contatos_encontrados[missing_prof] = {
                                        'name': missing_prof,
                                        'email': '',
                                        'phone': phone,
                                        'last4': last4
                                    }
                                else:
                                    print(f"     ⚠️  Nome encontrado mas sem telefone visível")
                            else:
                                print(f"     ⚠️  Nome no HTML mas não encontrado com XPath")
                        except:
                            print(f"     ⚠️  Nome encontrado mas sem telefone no contexto")
                else:
                    print(f"     ❌ Não encontrado na página")

        except Exception as e:
            print(f"❌ Erro geral na extração: {e}")
            import traceback
            traceback.print_exc()

        return contatos_encontrados

    def close(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()

def salvar_contatos(contatos):
    """Salva contatos encontrados no arquivo de profissionais"""
    if not contatos:
        print(f"\n⚠️  Nenhum contato foi encontrado para adicionar")
        return False

    # Carregar profissionais existentes
    prof_file = 'profissionais_autenticacao.json'
    with open(prof_file, 'r') as f:
        data = json.load(f)

    professionals = data['professionals']

    # Adicionar novos contatos
    adicionados = 0
    atualizados = 0

    for nome, info in contatos.items():
        # Verificar se já existe
        encontrado_idx = None
        for idx, prof in enumerate(professionals):
            if normalizar_nome(prof['name']) == normalizar_nome(nome):
                encontrado_idx = idx
                break

        if encontrado_idx is not None:
            # Atualizar se estiver sem telefone
            if not professionals[encontrado_idx].get('phone'):
                professionals[encontrado_idx].update(info)
                atualizados += 1
                print(f"✅ Atualizado: {nome} - {info['phone']}")
        else:
            # Adicionar novo
            professionals.append(info)
            adicionados += 1
            print(f"✅ Adicionado: {nome} - {info['phone']}")

    # Salvar arquivo atualizado
    with open(prof_file, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n📊 Resumo:")
    print(f"  ✅ Adicionados: {adicionados}")
    print(f"  ✅ Atualizados: {atualizados}")
    print(f"  📁 Arquivo salvo: {prof_file}")

    return True

def main():
    print("="*80)
    print("📞 SCRAPER DE CONTATOS - ESCALA.MED.BR")
    print("="*80)

    scraper = None
    try:
        scraper = ContatoScraper(headless=True)

        # Fazer login
        if not scraper.login():
            print("❌ Falha no login. Aborting...")
            return 1

        # Extrair contatos
        contatos = scraper.extrair_contatos_da_escala()

        # Salvar contatos
        if contatos:
            print(f"\n{'='*80}")
            print(f"📝 Salvando {len(contatos)} contato(s) encontrado(s)...")
            print(f"{'='*80}\n")
            salvar_contatos(contatos)
        else:
            print(f"\n⚠️  Nenhum contato foi encontrado")

        print(f"\n{'='*80}")
        print(f"✅ Script finalizado com sucesso!")
        print(f"{'='*80}\n")

        return 0

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        if scraper:
            scraper.close()

if __name__ == "__main__":
    exit(main())
