#!/usr/bin/env python3
"""
Scraping de contatos para profissionais sem telefone cadastrado.
Tenta clicar em cada profissional na escala para capturar modal com contato.
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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

ESCALA_USERNAME = os.getenv('ESCALA_USERNAME')
ESCALA_PASSWORD = os.getenv('ESCALA_PASSWORD')
PROF_FILE = 'profissionais_autenticacao.json'


def normalizar(nome):
    import unicodedata
    nome = nome.lower().strip()
    nome = unicodedata.normalize('NFD', nome)
    return ''.join(c for c in nome if unicodedata.category(c) != 'Mn')


def carregar_sem_contato():
    with open(PROF_FILE, encoding='utf-8') as f:
        data = json.load(f)
    sem_contato = [p['name'] for p in data['professionals'] if not p.get('phone')]
    print(f"📋 Profissionais sem telefone: {len(sem_contato)}")
    for n in sem_contato:
        print(f"   - {n}")
    return sem_contato


def salvar_contatos(encontrados: dict):
    with open(PROF_FILE, encoding='utf-8') as f:
        data = json.load(f)

    atualizados = 0
    for prof in data['professionals']:
        nome_norm = normalizar(prof['name'])
        if nome_norm in encontrados:
            info = encontrados[nome_norm]
            if info.get('phone') and not prof.get('phone'):
                prof['phone'] = info['phone']
                prof['last4'] = info['phone'][-4:]
            if info.get('email') and not prof.get('email'):
                prof['email'] = info['email']
            atualizados += 1
            print(f"   ✅ {prof['name']} → {prof.get('phone', '')} / {prof.get('email', '')}")

    with open(PROF_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n💾 {atualizados} contato(s) salvo(s) em {PROF_FILE}")


class ContatoScraper:
    def __init__(self):
        opts = Options()
        opts.add_argument('--headless=new')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--window-size=1920,1080')
        opts.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
        self.driver = webdriver.Chrome(options=opts)
        self.wait = WebDriverWait(self.driver, 10)

    def login(self):
        print("🔐 Fazendo login...")
        self.driver.get("https://escala.med.br/painel/#!/login")
        time.sleep(4)

        try:
            user_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[type='text']")
            user_input.send_keys(ESCALA_USERNAME)
            pwd_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            pwd_input.send_keys(ESCALA_PASSWORD)
            btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button")
            btn.click()
            time.sleep(5)
            print("✅ Login OK")
            return True
        except Exception as e:
            print(f"❌ Erro no login: {e}")
            return False

    def extrair_texto_modal(self):
        """Captura texto de qualquer modal/popup visível na página."""
        textos = []

        # Seletores comuns de modal
        seletores_modal = [
            "[class*='modal']",
            "[class*='popup']",
            "[class*='tooltip']",
            "[class*='overlay']",
            "[role='dialog']",
            "[class*='card']",
            "[class*='detail']",
            "[class*='info']",
        ]

        for sel in seletores_modal:
            try:
                els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                for el in els:
                    if el.is_displayed():
                        texto = el.text.strip()
                        if texto and len(texto) > 10:
                            textos.append(texto)
            except Exception:
                pass

        return '\n'.join(textos)

    def extrair_contato_do_texto(self, texto):
        phone = ''
        email = ''
        phone_match = re.search(r'\(?\d{2}\)?\s?\d{4,5}[-\s]?\d{4}', texto)
        if phone_match:
            phone = re.sub(r'\s', '', phone_match.group())
            # Normalizar para formato (XX) XXXXX-XXXX
            digits = re.sub(r'\D', '', phone)
            if len(digits) == 11:
                phone = f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
            elif len(digits) == 10:
                phone = f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"

        email_match = re.search(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', texto)
        if email_match:
            email = email_match.group().lower()

        return phone, email

    def buscar_contatos(self, nomes_sem_contato: list) -> dict:
        print("\n🔍 Navegando para a escala...")
        self.driver.get("https://escala.med.br/painel/#!/")
        time.sleep(8)

        nomes_norm = {normalizar(n): n for n in nomes_sem_contato}
        encontrados = {}

        # --- Tentativa 1: buscar no HTML atual (contatos inline) ---
        print("\n📄 Tentativa 1: buscando contatos no HTML da página...")
        page_html = self.driver.page_source
        for norm, original in nomes_norm.items():
            # Procura pelo nome no HTML (pode estar em formato diferente)
            partes = norm.split()
            for parte in partes[:2]:  # primeiros dois tokens do nome
                idx = page_html.lower().find(parte)
                if idx >= 0:
                    trecho = page_html[max(0, idx-300):idx+500]
                    phone, email = self.extrair_contato_do_texto(trecho)
                    if phone or email:
                        encontrados[norm] = {'phone': phone, 'email': email}
                        print(f"   ✅ {original}: {phone} / {email}")
                        break

        # --- Tentativa 2: clicar em cada profissional visível ---
        print("\n🖱️  Tentativa 2: clicando em profissionais na escala...")
        try:
            # Seletores de elemento de profissional comuns em escalas
            seletores_prof = [
                "[class*='profissional']",
                "[class*='professional']",
                "[class*='medico']",
                "[class*='doctor']",
                "[class*='nome']",
                "td span",
                ".ng-binding",
            ]

            elementos_clicaveis = []
            for sel in seletores_prof:
                els = self.driver.find_elements(By.CSS_SELECTOR, sel)
                for el in els:
                    try:
                        texto = el.text.strip()
                        norm_texto = normalizar(texto)
                        if norm_texto in nomes_norm and norm_texto not in encontrados:
                            elementos_clicaveis.append((el, norm_texto, nomes_norm[norm_texto]))
                    except Exception:
                        pass

            print(f"   Encontrados {len(elementos_clicaveis)} elementos clicáveis para profissionais sem contato")

            for el, norm, original in elementos_clicaveis:
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", el)
                    time.sleep(0.5)
                    el.click()
                    time.sleep(2)

                    # Captura modal/popup
                    texto_modal = self.extrair_texto_modal()
                    if texto_modal:
                        phone, email = self.extrair_contato_do_texto(texto_modal)
                        if phone or email:
                            encontrados[norm] = {'phone': phone, 'email': email}
                            print(f"   ✅ {original}: {phone} / {email}")

                    # Fechar modal se aberto
                    try:
                        esc_btn = self.driver.find_element(
                            By.CSS_SELECTOR,
                            "[class*='close'], [aria-label='Close'], button[data-dismiss]"
                        )
                        esc_btn.click()
                        time.sleep(0.5)
                    except Exception:
                        self.driver.execute_script(
                            "document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape', keyCode: 27}));"
                        )
                        time.sleep(0.5)

                except Exception as e:
                    print(f"   ⚠️  Erro ao clicar em {original}: {e}")

        except Exception as e:
            print(f"   ⚠️  Erro na tentativa 2: {e}")

        # --- Tentativa 3: página de equipe/profissionais ---
        print("\n👥 Tentativa 3: buscando página de equipe...")
        equipe_urls = [
            "https://escala.med.br/painel/#!/equipe",
            "https://escala.med.br/painel/#!/profissionais",
            "https://escala.med.br/painel/#!/team",
            "https://escala.med.br/painel/#!/medicos",
        ]

        for url in equipe_urls:
            try:
                self.driver.get(url)
                time.sleep(4)
                html = self.driver.page_source
                if len(html) > 5000:  # página carregou algo
                    print(f"   Página encontrada: {url}")
                    for norm, original in nomes_norm.items():
                        if norm in encontrados:
                            continue
                        partes = original.split()[:2]
                        for parte in partes:
                            idx = html.lower().find(normalizar(parte))
                            if idx >= 0:
                                trecho = html[max(0, idx-300):idx+500]
                                phone, email = self.extrair_contato_do_texto(trecho)
                                if phone or email:
                                    encontrados[norm] = {'phone': phone, 'email': email}
                                    print(f"   ✅ {original}: {phone} / {email}")
                                    break
                    break
            except Exception:
                pass

        nao_encontrados = [nomes_norm[n] for n in nomes_norm if n not in encontrados]
        print(f"\n📊 Resultado:")
        print(f"   ✅ Encontrados: {len(encontrados)}")
        print(f"   ❌ Não encontrados: {len(nao_encontrados)}")
        if nao_encontrados:
            for n in nao_encontrados:
                print(f"      - {n}")

        return encontrados

    def close(self):
        self.driver.quit()


def main():
    print("=" * 60)
    print("📞 BUSCA DE CONTATOS FALTANTES - ESCALA HRO")
    print(f"   {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("=" * 60)

    sem_contato = carregar_sem_contato()
    if not sem_contato:
        print("\n✅ Todos os profissionais já têm telefone cadastrado!")
        return 0

    scraper = None
    try:
        scraper = ContatoScraper()
        if not scraper.login():
            return 1

        encontrados = scraper.buscar_contatos(sem_contato)

        if encontrados:
            print(f"\n💾 Salvando {len(encontrados)} contato(s)...")
            salvar_contatos(encontrados)
        else:
            print("\n⚠️  Nenhum contato encontrado nesta execução.")
            print("   Os contatos podem não estar visíveis na escala atual.")
            print("   Tente rodar novamente em outro dia quando esses profissionais estiverem escalados.")

        return 0

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    exit(main())
