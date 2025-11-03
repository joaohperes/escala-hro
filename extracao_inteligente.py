#!/usr/bin/env python3
"""
Extração INTELIGENTE baseada em POSIÇÃO VISUAL das colunas (coordenada X)
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

class ExtractorInteligente:
    def __init__(self, headless=True):
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
            try:
                # Limpa cache corrompido do webdriver-manager
                cache_dir = os.path.expanduser('~/.wdm')
                if os.path.exists(cache_dir):
                    print(f"🗑️  Limpando cache em {cache_dir}...")
                    shutil.rmtree(cache_dir, ignore_errors=True)

                downloaded_path = ChromeDriverManager().install()
                print(f"⚠️  WebDriver-Manager retornou: {downloaded_path}")

                # webdriver-manager às vezes retorna o diretório em vez do executável
                # ou retorna o arquivo errado (THIRD_PARTY_NOTICES.chromedriver)
                # Procura pelo executável real
                search_dir = downloaded_path if os.path.isdir(downloaded_path) else os.path.dirname(downloaded_path)
                print(f"🔍 Procurando chromedriver em: {search_dir}")

                # Procura pelo executável no diretório
                # IMPORTANTE: Busca especificamente pelo arquivo 'chromedriver' sem extensão
                for root, dirs, files in os.walk(search_dir):
                    for file in files:
                        # Apenas o arquivo 'chromedriver' simples é o executável real
                        # Ignore THIRD_PARTY, LICENSE, .zip, .dmg, etc
                        if file == 'chromedriver' and not file.endswith(('.zip', '.dmg', '.exe')):
                            full_path = os.path.join(root, file)
                            # Garante que é executável
                            if not os.access(full_path, os.X_OK):
                                os.chmod(full_path, 0o755)
                            chrome_driver_path = full_path
                            print(f"✅ Executável encontrado: {chrome_driver_path}")
                            break
                    if chrome_driver_path:
                        break

                if not chrome_driver_path:
                    print(f"❌ Não conseguiu encontrar arquivo 'chromedriver' em {search_dir}")
                    raise FileNotFoundError("ChromeDriver executável não encontrado")

                print(f"✅ ChromeDriver pronto: {chrome_driver_path}")

            except Exception as e:
                print(f"❌ Erro ao usar webdriver-manager: {e}")
                raise

        self.driver = webdriver.Chrome(
            service=Service(chrome_driver_path),
            options=chrome_options
        )

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

    def extrair_inteligente(self):
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

    def close(self):
        self.driver.quit()


def main():
    extractor = None
    try:
        extractor = ExtractorInteligente(headless=True)
        extractor.login()
        resultado = extractor.extrair_inteligente()

        data = resultado['data']
        registros = resultado['registros']
        setores_count = resultado['setores_encontrados']
        headers_encontrados = resultado['headers_encontrados']

        # Debug info do JavaScript
        debug_info = resultado.get('debug', {})

        print(f"\n{'='*100}")
        print(f"📅 DATA: {data}")
        print(f"📊 TOTAL DE REGISTROS: {len(registros)}")
        print(f"📂 SETORES DETECTADOS: {setores_count}")
        print(f"🔍 HEADERS ENCONTRADOS: {headers_encontrados}")
        print(f"{'='*100}")

        if debug_info:
            print(f"\n🔧 DEBUG INFO:")
            print(f"   - Profissionais selecionados: {debug_info.get('profissionais_selecionados', 'N/A')}")
            print(f"   - Turnos selecionados: {debug_info.get('turnos_selecionados', 'N/A')}")
            print(f"   - Horários selecionados: {debug_info.get('horarios_selecionados', 'N/A')}")
            print(f"   - Setores com posição: {debug_info.get('setores_com_posicao', 'N/A')}")
            print(f"{'='*100}\n")
        else:
            print(f"{'='*100}\n")

        # Conta setores
        setores_dict = {}
        for reg in registros:
            s = reg['setor']
            setores_dict[s] = setores_dict.get(s, 0) + 1

        print("📊 DISTRIBUIÇÃO POR SETOR:")
        for setor, count in sorted(setores_dict.items()):
            print(f"   {count:2d}x - {setor}")

        print(f"\n{'='*160}")
        print(f" #  | {'PROFISSIONAL':<30} | {'SETOR':<35} | {'TURNO':<25} | {'HORÁRIO':<12}")
        print("-"*160)

        for idx, reg in enumerate(registros, 1):
            prof = reg['profissional'][:30].ljust(30)
            setor = reg['setor'][:35].ljust(35)
            turno = reg['tipo_turno'][:25].ljust(25)
            horario = reg['horario'][:12].ljust(12)
            print(f"{idx:3d} | {prof} | {setor} | {turno} | {horario}")

        print(f"\n{'='*100}")
        print(f"✅ Extração salva em: /tmp/extracao_inteligente.json")
        print(f"{'='*100}\n")

        # Salva JSON no formato esperado pelo dashboard (com chave 'atual')
        # O dashboard espera: { "anterior": {...}, "atual": {...}, "proximo": {...} }
        from datetime import datetime

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

        data_simples = extrair_data_simples(data)

        # Formata a resposta no formato esperado pelo dashboard
        # Formato: { "atual": {...}, "anterior": {...} } para dia atual e consulta histórica
        output = {
            'atual': {
                'data': data,
                'data_simples': data_simples,
                'registros': registros,
                'total': len(registros)
            },
            'anterior': {
                'data': 'N/A',
                'data_simples': '00/00/0000',
                'registros': [],
                'total': 0
            },
            'data_atualizacao': datetime.now().strftime('%d/%m/%Y'),
            'hora_atualizacao': datetime.now().strftime('%H:%M'),
            'status_atualizacao': 'sucesso'
        }

        with open('/tmp/extracao_inteligente.json', 'w') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if extractor:
            extractor.close()


if __name__ == "__main__":
    main()
