#!/usr/bin/env python3
"""
Extração INTELIGENTE baseada em POSIÇÃO VISUAL das colunas (coordenada X)
Com suporte a Rolling Window para Dia Anterior
"""

import os
import json
import time
import shutil
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

def carregar_ramais_data():
    """Carrega dados de ramais e mapeamento de setores para persistência"""
    ramais_data = None
    mapping_data = None

    # Tentar carregar ramais_hro.json
    ramais_paths = [
        'ramais_hro.json',
        os.path.expanduser('~/escalaHRO/ramais_hro.json'),
        '/Users/joaoperes/escalaHRO/ramais_hro.json',
    ]

    for path in ramais_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    ramais_data = json.load(f)
                print(f"✅ Ramais carregados de: {path}")
                break
            except Exception as e:
                print(f"⚠️  Erro ao ler {path}: {e}")

    # Tentar carregar setor_ramais_mapping.json
    mapping_paths = [
        'setor_ramais_mapping.json',
        os.path.expanduser('~/escalaHRO/setor_ramais_mapping.json'),
        '/Users/joaoperes/escalaHRO/setor_ramais_mapping.json',
    ]

    for path in mapping_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    mapping_data = json.load(f)
                print(f"✅ Mapeamento de setores carregado de: {path}")
                break
            except Exception as e:
                print(f"⚠️  Erro ao ler {path}: {e}")

    return ramais_data, mapping_data

class ExtractorInteligente:
    def __init__(self, headless=True):
        # Backend de browser: 'chrome' (padrão, usado no GitHub Actions) ou 'safari'
        # (para rodar localmente em Macs sem Chrome). Toda a extração usa JS via
        # execute_script, então o motor é indiferente para os dados.
        browser = os.getenv('ESCALA_BROWSER', 'chrome').lower()
        if browser == 'safari':
            print("🧭 Usando Safari (safaridriver) como backend...")
            # safaridriver às vezes falha com "unexpectedly exited" quando uma
            # sessão anterior ficou presa. Tenta algumas vezes com pausa.
            ultima_excecao = None
            for tentativa in range(1, 4):
                try:
                    self.driver = webdriver.Safari()
                    self.driver.set_window_size(1600, 1000)
                    return
                except Exception as e:
                    ultima_excecao = e
                    print(f"   ⚠️  Tentativa {tentativa}/3 de iniciar Safari falhou; aguardando...")
                    time.sleep(5)
            raise ultima_excecao

        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')  # Necessário para GitHub Actions
        chrome_options.add_argument('--disable-dev-shm-usage')  # Evita problemas de memória
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

        # Tenta usar chromedriver já instalado, se não, baixa via webdriver-manager
        chrome_driver_path = None

        # Procura por chromedriver em locais comuns
        common_paths = [
            '/usr/bin/chromedriver',
            '/usr/local/bin/chromedriver',
            shutil.which('chromedriver'),
        ]

        for path in common_paths:
            if path and os.path.isfile(path) and os.access(path, os.X_OK):
                chrome_driver_path = path
                print(f"✅ ChromeDriver encontrado em: {path}")
                break

        # Se não encontrou, tenta baixar via webdriver-manager
        if not chrome_driver_path:
            print("⚠️  ChromeDriver não encontrado nos caminhos comuns, tentando webdriver-manager...")
            
            # Limpa cache do webdriver-manager
            wdm_cache = os.path.expanduser("~/.wdm")
            if os.path.exists(wdm_cache):
                print(f"🗑️  Limpando cache em {wdm_cache}...")
                shutil.rmtree(wdm_cache)
            
            try:
                wdm_result = ChromeDriverManager().install()
                print(f"⚠️  WebDriver-Manager retornou: {wdm_result}")
                
                # Procura o arquivo executável
                chrome_dir = os.path.dirname(wdm_result)
                print(f"🔍 Procurando chromedriver em: {chrome_dir}")
                for root, dirs, files in os.walk(chrome_dir):
                    for file in files:
                        if file == 'chromedriver' or file == 'chromedriver.exe':
                            full_path = os.path.join(root, file)
                            if os.access(full_path, os.X_OK):
                                chrome_driver_path = full_path
                                print(f"✅ Executável encontrado: {full_path}")
                                break
                    if chrome_driver_path:
                        break
            except Exception as e:
                print(f"⚠️  Erro com webdriver-manager: {e}")

        if chrome_driver_path:
            print(f"✅ ChromeDriver pronto: {chrome_driver_path}")
            service = Service(chrome_driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            print("⚠️  Usando ChromeDriver padrão do sistema...")
            self.driver = webdriver.Chrome(options=chrome_options)

    def login(self):
        print(f"[{datetime.now()}] 🔐 Fazendo login...")
        self.driver.get("https://escala.med.br/painel/#!/login")
        time.sleep(4)

        username = self.driver.find_element(By.CSS_SELECTOR, "input[type='email'], input[type='text'][placeholder*='usuário']")
        username.send_keys(ESCALA_USERNAME)
        time.sleep(1)

        password = self.driver.find_element(By.CSS_SELECTOR, "input[type='password']")
        password.send_keys(ESCALA_PASSWORD)
        time.sleep(1)

        self.driver.execute_script("var buttons = document.querySelectorAll('button'); for(var b of buttons) { if(b.textContent.toLowerCase().includes('entrar')) { b.click(); break; } }")
        time.sleep(5)

        print(f"[{datetime.now()}] ✅ Login realizado")

    def extrair_dia(self):
        """Extrai dados de um único dia (atual ou anterior) usando JavaScript"""
        # JavaScript que calcula setores por POSIÇÃO X
        js_inteligente = """
        return (function() {
            var registros = [];
            var data = "Hoje";

            // Extrai data
            var dateElements = document.querySelectorAll('[class*="brqgnP"]');
            if (dateElements.length > 0) {
                data = dateElements[0].textContent.trim();
            }

            // === ESTRATÉGIA: Mapear profissionais por POSIÇÃO VISUAL (X coordinate) ===
            // 1. Encontra TODOS os headers de setor com suas posições X
            var setorHeaders = document.querySelectorAll('[class*="sc-ifAKCX"]');
            var setoresComPosicao = [];

            console.log("Headers encontrados: " + setorHeaders.length);

            for (var h = 0; h < setorHeaders.length; h++) {
                var rect = setorHeaders[h].getBoundingClientRect();
                var nomeSetor = setorHeaders[h].textContent.trim();

                setoresComPosicao.push({
                    nome: nomeSetor,
                    left: Math.round(rect.left),
                    right: Math.round(rect.right),
                    width: Math.round(rect.width)
                });
            }

            console.log("Setores com posição X:");
            for (var sp = 0; sp < setoresComPosicao.length; sp++) {
                console.log("  " + sp + ": " + setoresComPosicao[sp].nome + " [" + setoresComPosicao[sp].left + "-" + setoresComPosicao[sp].right + "]");
            }

            // 2. Extrai profissionais com suas posições X
            // Tenta múltiplas estratégias de seleção para compatibilidade com atualizações do site
            var profissionais = document.querySelectorAll('[class*="fjdhpX"]');
            var turnos = document.querySelectorAll('[class*="jzJRlG"]');
            var horarios = document.querySelectorAll('[class*="cSHVUG"]');

            // Fallback 1: Se os seletores originais não funcionam, tenta procurar por estrutura
            if (profissionais.length === 0) {
                console.log("DEBUG: Seletores originais falharam, tentando fallback...");

                // Tenta encontrar elementos que contêm nomes profissionais (em qualquer lugar)
                var allElements = document.querySelectorAll('[class*="Name"], [class*="name"], [class*="professional"], [class*="Professional"]');

                if (allElements.length > 0) {
                    console.log("DEBUG: Encontrados " + allElements.length + " elementos com 'name' na classe");
                    profissionais = allElements;
                } else {
                    // Fallback 2: Procura por divs com conteúdo que parece nome
                    var divs = document.querySelectorAll('div');
                    var nomesEncontrados = [];

                    for (var d = 0; d < divs.length; d++) {
                        var text = (divs[d].textContent || "").trim();
                        // Procura por padrão de nome: 2-3 palavras, começa com maiúscula
                        if (text && text.match(/^[A-Z][a-z]+(\\s+[A-Z][a-z]+){1,3}$/) && text.length > 3 && text.length < 80) {
                            nomesEncontrados.push(divs[d]);
                        }
                    }

                    if (nomesEncontrados.length > 0) {
                        console.log("DEBUG: Encontrados " + nomesEncontrados.length + " elementos com padrão de nome");
                        profissionais = nomesEncontrados;
                    }
                }
            }

            // Fallback para turnos e horários
            if (turnos.length === 0) {
                turnos = document.querySelectorAll('[class*="shift"], [class*="turno"], [class*="Turno"], span:contains("Plantão")');
            }

            if (horarios.length === 0) {
                horarios = document.querySelectorAll('[class*="time"], [class*="hora"], [class*="horario"], [class*="Horario"]');
            }

            console.log("Profissionais encontrados: " + profissionais.length);
            console.log("DEBUG: turnos=" + turnos.length + ", horarios=" + horarios.length);

            for (var i = 0; i < Math.min(profissionais.length, turnos.length, horarios.length); i++) {
                var prof = profissionais[i].textContent.trim();
                var turno = turnos[i].textContent.trim();
                var horario = horarios[i].textContent.trim();

                if (prof.length < 3 || turno.length < 2) continue;

                // Encontra a posição X do profissional
                var profRect = profissionais[i].getBoundingClientRect();
                var profLeft = Math.round(profRect.left);
                var profCenter = Math.round(profRect.left + profRect.width / 2);

                var setor = "Plantão";

                // Procura qual setor (coluna) contém este profissional pela posição X
                for (var s = 0; s < setoresComPosicao.length; s++) {
                    // Verifica se o profissional está dentro da largura deste setor
                    if (profCenter >= setoresComPosicao[s].left && profCenter <= setoresComPosicao[s].right) {
                        setor = setoresComPosicao[s].nome;
                        break;
                    }
                }

                // FALLBACK: se não achou por posição, procura o setor mais próximo
                if (setor === "Plantão" && setoresComPosicao.length > 0) {
                    var menorDistancia = Infinity;
                    for (var s = 0; s < setoresComPosicao.length; s++) {
                        var distancia = Math.abs(profCenter - ((setoresComPosicao[s].left + setoresComPosicao[s].right) / 2));
                        if (distancia < menorDistancia) {
                            menorDistancia = distancia;
                            setor = setoresComPosicao[s].nome;
                        }
                    }
                }

                // Tenta extrair contato (email e phone)
                // NOTA: Contatos podem não estar visíveis na DOM normal do schedule
                // Podem aparecer em modal ou hover - será necessário clicar para extrair
                var email = "";
                var phone = "";

                try {
                    // Tenta buscar em vários contextos possíveis
                    var container = profissionais[i];

                    // Procura até 10 níveis de parent
                    for (var level = 0; level < 10; level++) {
                        if (!container) break;

                        var fullText = (container.innerText || container.textContent || "").trim();

                        // Se encontrou dados no texto completo
                        if (fullText) {
                            // Procura email - padrão: algo@algo.algo
                            var emailMatch = fullText.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/);
                            if (emailMatch && !email) {
                                email = emailMatch[0];
                            }

                            // Procura telefone - padrão brasileiro (XX) XXXXX-XXXX ou similar
                            var phoneMatch = fullText.match(/\\(\\d{1,3}\\)\\s?\\d{4,5}-?\\d{3,4}/);
                            if (phoneMatch && !phone) {
                                phone = phoneMatch[0];
                            }
                        }

                        // Se encontrou ambos, para a busca
                        if (email && phone) break;

                        container = container.parentElement;
                    }
                } catch (e) {
                    // Silently fail
                }

                registros.push({
                    profissional: prof,
                    setor: setor,
                    tipo_turno: turno,
                    horario: horario,
                    email: email,
                    phone: phone,
                    data: data,
                    pos_x: profLeft
                });
            }

            // Conta setores únicos
            var setoresUnicos = {};
            for (var j = 0; j < registros.length; j++) {
                setoresUnicos[registros[j].setor] = true;
            }
            var totalSetores = Object.keys(setoresUnicos).length;

            return {
                total: registros.length,
                data: data,
                setores_encontrados: totalSetores,
                registros: registros,
                headers_encontrados: setoresComPosicao.length,
                debug: {
                    profissionais_selecionados: profissionais.length,
                    turnos_selecionados: turnos.length,
                    horarios_selecionados: horarios.length,
                    setores_com_posicao: setoresComPosicao.length
                }
            };
        })();
        """

        resultado = self.driver.execute_script(js_inteligente)
        return resultado

    def ativar_filtro_contato(self):
        """Abre o painel de Filtros e marca 'Mostrar informações de contato do
        plantonista', sem o qual telefone/email não aparecem na grade.
        Idempotente: se já estiver marcado, não faz nada."""
        try:
            # Abre o painel de Filtros
            self.driver.execute_script(r"""
              for (var e of document.querySelectorAll('button,div,span,a')){
                if((e.textContent||'').trim()==='Filtros'){ e.click(); return true; }
              }
              return false;
            """)
            time.sleep(2)

            # Marca o checkbox de contato (por texto; fallback: 2º checkbox)
            marcado = self.driver.execute_script(r"""
              function rowText(c){
                var n=c;
                for(var i=0;i<6;i++){ if(!n) break;
                  var t=(n.textContent||'').trim();
                  if(t.length>3) return t.slice(0,70);
                  n=n.parentElement;
                }
                return '';
              }
              var cbs=Array.from(document.querySelectorAll("input[type='checkbox']"));
              for (var c of cbs){
                if(rowText(c).toLowerCase().includes('contato')){
                  if(!c.checked) c.click();
                  return rowText(c);
                }
              }
              if(cbs.length>1){ if(!cbs[1].checked) cbs[1].click(); return 'idx1'; }
              return null;
            """)
            time.sleep(3)
            print(f"[{datetime.now()}] 📞 Filtro de contato ativado: {marcado}")

            # Fecha o painel de Filtros para não cobrir a grade (clica de novo)
            self.driver.execute_script(r"""
              for (var e of document.querySelectorAll('button,div,span,a')){
                if((e.textContent||'').trim()==='Filtros'){ e.click(); return; }
              }
            """)
            time.sleep(2)
        except Exception as e:
            print(f"[{datetime.now()}] ⚠️  Não foi possível ativar filtro de contato: {e}")

    def navegar_proximo_dia(self):
        """Clica na seta '>' do cabeçalho de data para avançar 1 dia.
        Retorna (data_antes, data_depois); se forem iguais, a navegação falhou."""
        antes = self.driver.execute_script(r"""
          for(var e of document.querySelectorAll('*')){
            if(e.childElementCount===0){var t=(e.textContent||'').trim();
              if(/^\d{1,2}\s+[A-Za-zçÇ]+\s+\d{4}$/.test(t)) return t;}
          }
          return null;
        """)
        self.driver.execute_script(r"""
          var cands=[];
          for(var e of document.querySelectorAll('button,span,div,i,svg,a')){
            var t=(e.textContent||'').trim();
            var aria=(e.getAttribute('aria-label')||'');
            if(t==='>'||/next|forward|chevron.?right|arrow.?right|proxim/i.test(aria)){ cands.push(e); }
          }
          if(cands.length){ cands[cands.length-1].click(); }
        """)
        time.sleep(4)
        depois = self.driver.execute_script(r"""
          for(var e of document.querySelectorAll('*')){
            if(e.childElementCount===0){var t=(e.textContent||'').trim();
              if(/^\d{1,2}\s+[A-Za-zçÇ]+\s+\d{4}$/.test(t)) return t;}
          }
          return null;
        """)
        return antes, depois

    def extrair_inteligente(self):
        """Extrai dados do dia ATUAL e do dia SEGUINTE (via navegação).
        O dia ANTERIOR é preenchido pela lógica de rolling window (cache)."""
        print(f"[{datetime.now()}] 📊 Extraindo com análise de POSIÇÃO VISUAL (X coordinate)...")

        self.driver.get("https://escala.med.br/painel/#!/day_grid")
        time.sleep(5)

        # Switch iframe
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                self.driver.switch_to.frame(iframes[0])
        except:
            pass

        # ===== ATIVAR FILTRO "MOSTRAR INFORMAÇÕES DE CONTATO" =====
        # Sem este filtro o site não renderiza telefone/email nos cards.
        self.ativar_filtro_contato()

        # ===== EXTRAÇÃO DO DIA ATUAL =====
        print(f"[{datetime.now()}] 📅 Extraindo dados do dia ATUAL...")
        resultado_atual = self.extrair_dia()
        print(f"[{datetime.now()}] ✅ Dia atual extraído: {resultado_atual['total']} registros")

        # ===== EXTRAÇÃO DO DIA SEGUINTE (navega +1 dia) =====
        resultado_seguinte = None
        try:
            print(f"[{datetime.now()}] ➡️  Navegando para o dia SEGUINTE...")
            antes, depois = self.navegar_proximo_dia()
            if antes and depois and antes != depois:
                resultado_seguinte = self.extrair_dia()
                print(f"[{datetime.now()}] ✅ Dia seguinte extraído ({depois}): {resultado_seguinte['total']} registros")
            else:
                print(f"[{datetime.now()}] ⚠️  Navegação não avançou (antes={antes}, depois={depois}); dia seguinte ignorado")
        except Exception as e:
            print(f"[{datetime.now()}] ⚠️  Erro ao extrair dia seguinte: {e}")

        return {
            'atual': resultado_atual,
            'seguinte': resultado_seguinte,
            'anterior': None  # Será preenchido pela lógica de rolling window
        }

    def close(self):
        self.driver.quit()


def corrigir_portugues(texto):
    """Corrige erros comuns de ortografia em textos extraídos do website"""
    if not texto:
        return texto

    # Mapa de correções (errado → correto)
    correcoes = {
        'Residencia': 'Residência',
        'Clinica': 'Clínica',
        'Clinica Médica': 'Clínica Médica',
        'Obstetrícia': 'Obstetrícia',  # Já está certo, mas por segurança
    }

    resultado = texto
    for errado, correto in correcoes.items():
        resultado = resultado.replace(errado, correto)

    return resultado

def main():
    extractor = None
    try:
        extractor = ExtractorInteligente(headless=True)
        extractor.login()
        resultados = extractor.extrair_inteligente()

        # Extrai data simples (DD/MM/YYYY) a partir da data em português
        def extrair_data_simples(data_texto):
            try:
                # Tenta converter "03 novembro 2025" para "03/11/2025"
                partes = data_texto.split()
                if len(partes) >= 3:
                    dia = partes[0].zfill(2)
                    ano = partes[2]

                    meses = {
                        'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
                        'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
                        'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
                    }
                    mes = meses.get(partes[1].lower(), '01')
                    return f"{dia}/{mes}/{ano}"
            except:
                pass
            return "00/00/0000"

        # ===== PROCESSA RESULTADO ATUAL =====
        resultado_atual = resultados['atual']
        data_atual = resultado_atual['data']
        registros_atual = resultado_atual['registros']
        setores_count_atual = resultado_atual['setores_encontrados']
        headers_encontrados_atual = resultado_atual['headers_encontrados']

        # Corrige erros de português nos registros atuais
        for reg in registros_atual:
            reg['setor'] = corrigir_portugues(reg['setor'])

        # Debug info do JavaScript (atual)
        debug_info_atual = resultado_atual.get('debug', {})

        print(f"\n{'='*100}")
        print(f"📅 DIA ATUAL - DATA: {data_atual}")
        print(f"📊 TOTAL DE REGISTROS: {len(registros_atual)}")
        print(f"📂 SETORES DETECTADOS: {setores_count_atual}")
        print(f"🔍 HEADERS ENCONTRADOS: {headers_encontrados_atual}")
        print(f"{'='*100}")

        if debug_info_atual:
            print(f"\n🔧 DEBUG INFO (ATUAL):")
            print(f"   - Profissionais selecionados: {debug_info_atual.get('profissionais_selecionados', 'N/A')}")
            print(f"   - Turnos selecionados: {debug_info_atual.get('turnos_selecionados', 'N/A')}")
            print(f"   - Horários selecionados: {debug_info_atual.get('horarios_selecionados', 'N/A')}")
            print(f"   - Setores com posição: {debug_info_atual.get('setores_com_posicao', 'N/A')}")
            print(f"{'='*100}\n")
        else:
            print(f"{'='*100}\n")

        # Conta setores (atual)
        setores_dict_atual = {}
        for reg in registros_atual:
            s = reg['setor']
            setores_dict_atual[s] = setores_dict_atual.get(s, 0) + 1

        print("📊 DISTRIBUIÇÃO POR SETOR (ATUAL):")
        for setor, count in sorted(setores_dict_atual.items()):
            print(f"   {count:2d}x - {setor}")

        print(f"\n{'='*160}")
        print(f" #  | {'PROFISSIONAL':<30} | {'SETOR':<35} | {'TURNO':<25} | {'HORÁRIO':<12}")
        print("-"*160)

        for idx, reg in enumerate(registros_atual, 1):
            prof = reg['profissional'][:30].ljust(30)
            setor = reg['setor'][:35].ljust(35)
            turno = reg['tipo_turno'][:25].ljust(25)
            horario = reg['horario'][:12].ljust(12)
            print(f"{idx:3d} | {prof} | {setor} | {turno} | {horario}")

        print(f"\n{'='*100}")
        print(f"✅ Extração salva em: /tmp/extracao_inteligente.json")
        print(f"{'='*100}\n")

        # ===== IMPLEMENTAR ROLLING WINDOW =====
        print(f"\n{'='*100}")
        print(f"🔄 CARREGANDO DADOS DO DIA ANTERIOR (ROLLING WINDOW)...")
        print(f"{'='*100}")

        resultado_anterior_salvo = None
        # FIX: Remover /tmp como source primário de anterior data
        # /tmp é ephemeral e pode conter dados antigos entre execuções
        # PRIORIZAR: data/ (persistente) > fallback > nenhum
        arquivo_anterior_persistente = 'data/extracao_inteligente_anterior_cache.json'

        # APENAS carrega do arquivo persistente (data/)
        # NÃO carrega de /tmp para evitar acumular dados antigos
        if os.path.exists(arquivo_anterior_persistente):
            arquivo_para_carregar = arquivo_anterior_persistente
            try:
                with open(arquivo_para_carregar, 'r') as f:
                    anterior_completa = json.load(f)
                    # A anterior salva tem a estrutura: { 'atual': {...}, 'anterior': {...} }
                    # Se o arquivo é de ONTEM:
                    # - O 'atual' desse arquivo é de ONTEM (quando foi salvo como backup)
                    # - Esse 'atual' deve ser nosso 'anterior' HOJE
                    # Se o arquivo é de HOJE (dias_diff == 0):
                    # - Significa que o 'atual' é de hoje
                    # - Então devemos usar o 'anterior' do arquivo como o anterior de hoje
                    # Por enquanto, vamos tentar usar 'atual' primeiro
                    resultado_anterior_salvo = anterior_completa.get('atual')

                    if resultado_anterior_salvo:
                        data_anterior_str = resultado_anterior_salvo.get('data', 'N/A')

                        # Validar que o arquivo anterior é realmente do dia anterior
                        # Se tiver mais de 1 dia de diferença, ignorar (workflow não rodou)
                        try:
                            # Exemplo de data: "09 novembro 2025"
                            meses_pt = {
                                'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
                                'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
                                'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
                            }

                            partes = data_anterior_str.split()
                            if len(partes) >= 3:
                                dia_ant = int(partes[0])
                                mes_ant = meses_pt.get(partes[1].lower(), 0)
                                ano_ant = int(partes[2])

                                data_obj_anterior = datetime(ano_ant, mes_ant, dia_ant)
                                data_obj_hoje = datetime.now()

                                dias_diff = (data_obj_hoje - data_obj_anterior).days

                                if dias_diff == 1:
                                    # Dados de exatamente 1 dia atrás - PERFEITO!
                                    print(f"✅ Dados do dia anterior carregados: {data_anterior_str}")
                                    print(f"   Total de registros: {len(resultado_anterior_salvo.get('registros', []))}")
                                elif dias_diff == 0:
                                    # Cache contém dados de HOJE (foi atualizado hoje)
                                    # Neste caso, o 'atual' do cache é de hoje
                                    # Devemos usar o 'anterior' do cache em vez do 'atual'
                                    print(f"⚠️  Cache foi atualizado hoje. Usando campo 'anterior' do cache...")
                                    resultado_anterior_salvo = anterior_completa.get('anterior')
                                    if resultado_anterior_salvo:
                                        data_anterior_str = resultado_anterior_salvo.get('data', 'N/A')
                                        print(f"✅ Usando anterior do cache: {data_anterior_str}")
                                        print(f"   Total de registros: {len(resultado_anterior_salvo.get('registros', []))}")
                                    else:
                                        print(f"⚠️  Campo 'anterior' do cache vazio. Tentando fallback...")
                                        resultado_anterior_salvo = None

                                        # Tentar carregar arquivo fallback
                                        fallback_paths = [
                                            'data/extracao_inteligente_anterior_fallback.json',
                                            os.path.expanduser('~/escalaHRO/data/extracao_inteligente_anterior_fallback.json'),
                                        ]
                                        for fallback_path in fallback_paths:
                                            if os.path.exists(fallback_path):
                                                try:
                                                    with open(fallback_path, 'r') as fb:
                                                        fallback_data = json.load(fb)
                                                        resultado_anterior_salvo = fallback_data.get('atual')
                                                        if resultado_anterior_salvo:
                                                            print(f"✅ Fallback anterior carregado: {resultado_anterior_salvo.get('data', 'N/A')}")
                                                            break
                                                except Exception as fb_err:
                                                    print(f"⚠️  Erro ao carregar fallback: {fb_err}")
                                elif dias_diff > 2:
                                    # Arquivo anterior é muito antigo (mais de 2 dias), rejeitar e usar fallback
                                    # Isso previne reutilizar dados muito antigos que podem estar desatualizados
                                    print(f"⚠️  REJEITAR: Arquivo anterior muito antigo ({dias_diff} dias). Carregando fallback...")
                                    resultado_anterior_salvo = None

                                    # Tentar carregar arquivo fallback
                                    fallback_paths = [
                                        'data/extracao_inteligente_anterior_fallback.json',
                                        os.path.expanduser('~/escalaHRO/data/extracao_inteligente_anterior_fallback.json'),
                                    ]
                                    for fallback_path in fallback_paths:
                                        if os.path.exists(fallback_path):
                                            try:
                                                with open(fallback_path, 'r') as fb:
                                                    fallback_data = json.load(fb)
                                                    resultado_anterior_salvo = fallback_data.get('atual')
                                                    if resultado_anterior_salvo:
                                                        print(f"✅ Fallback anterior carregado: {resultado_anterior_salvo.get('data', 'N/A')}")
                                                        break
                                            except Exception as fb_err:
                                                print(f"⚠️  Erro ao carregar fallback: {fb_err}")
                                else:
                                    # Dias diff é 2 ou algo entre 0-2 (mas não 0 ou 1)
                                    print(f"⚠️  Dados do anterior com diferença de {dias_diff} dia(s): {data_anterior_str}")
                                    print(f"   Total de registros: {len(resultado_anterior_salvo.get('registros', []))}")
                        except Exception as date_err:
                            print(f"⚠️  Erro ao validar data anterior: {date_err}")
                            # Se não conseguir validar, mantém como está

            except Exception as e:
                print(f"⚠️  Erro ao carregar anterior: {e}")
        else:
            print(f"⚠️  Nenhuma extração anterior encontrada (primeira execução?)")

        # ===== CARREGAR RAMAIS PARA PERSISTÊNCIA =====
        print(f"\n{'='*100}")
        print(f"📞 CARREGANDO DADOS DE RAMAIS PARA PERSISTÊNCIA...")
        print(f"{'='*100}")
        ramais_data, mapping_data = carregar_ramais_data()
        if ramais_data is None:
            print(f"⚠️  Ramais não carregados")
        if mapping_data is None:
            print(f"⚠️  Mapeamento de setores não carregado")
        print(f"\n{'='*100}\n")

        # ===== CONSTRUIR OUTPUT COM ROLLING WINDOW =====
        data_simples_atual = extrair_data_simples(data_atual)

        output = {
            'atual': {
                'data': data_atual,
                'data_simples': data_simples_atual,
                'registros': registros_atual,
                'total': len(registros_atual)
            },
            'data_atualizacao': datetime.now().strftime('%d/%m/%Y'),
            'hora_atualizacao': datetime.now().strftime('%H:%M'),
            'status_atualizacao': 'sucesso'
        }

        # Adiciona dados de ramais ao output para persistência (garante que estarão disponíveis no workflow)
        if ramais_data:
            output['ramais_hro'] = ramais_data
        if mapping_data:
            output['setor_ramais_mapping'] = mapping_data

        # Adiciona dados do dia anterior (rolling window)
        if resultado_anterior_salvo:
            output['anterior'] = resultado_anterior_salvo
        else:
            # Primeira execução ou arquivo perdido
            output['anterior'] = {
                'data': 'N/A',
                'data_simples': '00/00/0000',
                'registros': [],
                'total': 0
            }

        # Adiciona dados do dia seguinte (extraído ao vivo navegando +1 dia)
        resultado_seguinte = resultados.get('seguinte')
        if resultado_seguinte and resultado_seguinte.get('registros'):
            for reg in resultado_seguinte['registros']:
                reg['setor'] = corrigir_portugues(reg['setor'])
            output['seguinte'] = {
                'data': resultado_seguinte['data'],
                'data_simples': extrair_data_simples(resultado_seguinte['data']),
                'registros': resultado_seguinte['registros'],
                'total': len(resultado_seguinte['registros'])
            }
        else:
            output['seguinte'] = {
                'data': 'N/A',
                'data_simples': '00/00/0000',
                'registros': [],
                'total': 0
            }

        # Salva o JSON principal
        with open('/tmp/extracao_inteligente.json', 'w') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\n✅ JSON principal salvo: /tmp/extracao_inteligente.json")

        # IMPORTANTE: Salvar a extração ATUAL para ser usada como ANTERIOR amanhã
        # Criar um backup da extração atual para amanhã usar como anterior
        backup_para_amanha = {
            'atual': output['atual'],
            'anterior': output['anterior'],  # Mantém a cadeia de histórico
            'data_backup': datetime.now().strftime('%d/%m/%Y'),
            'hora_backup': datetime.now().strftime('%H:%M')
        }

        # Salvar em /tmp (temporário) e no repositório (persistente)
        arquivo_anterior = '/tmp/extracao_inteligente_anterior.json'
        with open(arquivo_anterior, 'w') as f:
            json.dump(backup_para_amanha, f, ensure_ascii=False, indent=2)
        print(f"✅ Backup para amanhã: {arquivo_anterior}")

        # Salvar também no arquivo persistente (data/extracao_inteligente_anterior_cache.json)
        # para que o GitHub Actions possa usar no dia seguinte
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(arquivo_anterior_persistente), exist_ok=True)
            with open(arquivo_anterior_persistente, 'w') as f:
                json.dump(backup_para_amanha, f, ensure_ascii=False, indent=2)
            print(f"✅ Backup persistente: {arquivo_anterior_persistente}")
        except Exception as e:
            print(f"⚠️  Erro ao salvar backup persistente: {e}")

        # TAMBÉM salvar como fallback anterior para quando a extração falhar
        # Isso garante que "Dia Anterior" sempre tenha dados mais recentes
        arquivo_anterior_fallback = 'data/extracao_inteligente_anterior_fallback.json'
        try:
            os.makedirs(os.path.dirname(arquivo_anterior_fallback), exist_ok=True)
            with open(arquivo_anterior_fallback, 'w') as f:
                json.dump(backup_para_amanha, f, ensure_ascii=False, indent=2)
            print(f"✅ Fallback anterior atualizado: {arquivo_anterior_fallback}")
        except Exception as e:
            print(f"⚠️  Erro ao salvar fallback anterior: {e}")

        # ===== VALIDAÇÃO FINAL =====
        print(f"\n{'='*100}")
        print(f"🔍 VALIDAÇÃO FINAL DA EXTRAÇÃO")
        print(f"{'='*100}")

        try:
            # Validar que ramais foram embarcados
            if 'ramais_hro' not in output:
                raise ValueError("❌ ERRO CRÍTICO: 'ramais_hro' não encontrado no arquivo de saída!")
            if 'setor_ramais_mapping' not in output:
                raise ValueError("❌ ERRO CRÍTICO: 'setor_ramais_mapping' não encontrado no arquivo de saída!")

            if len(output.get('ramais_hro', [])) == 0:
                raise ValueError("❌ ERRO CRÍTICO: 'ramais_hro' está vazio!")
            if len(output.get('setor_ramais_mapping', [])) == 0:
                raise ValueError("❌ ERRO CRÍTICO: 'setor_ramais_mapping' está vazio!")

            print(f"✅ Ramais embarcados: {len(output['ramais_hro'])} departamentos")
            print(f"✅ Mapeamento de setores: {len(output['setor_ramais_mapping'])} mapeamentos")
            print(f"✅ Data atual: {output['atual']['data']}")
            print(f"✅ Data anterior: {output['anterior']['data']}")
            print(f"✅ Validação PASSOU!")
            print(f"{'='*100}\n")

        except ValueError as ve:
            print(f"{ve}")
            print(f"❌ VALIDAÇÃO FALHOU! Extração abortada.")
            raise

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if extractor:
            extractor.close()


if __name__ == "__main__":
    main()
