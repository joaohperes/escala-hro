#!/usr/bin/env python3
"""
Dashboard Executivo - Visual Premium
Com banner ALVF e design sofisticado

MELHORIAS V3:
- Abas de navegação para 3 dias (anterior/atual/próxima)
- Badges coloridas para tipos de turno
- Indicadores visuais melhorados
- Melhor usabilidade e leitura
- Integração de ramais hospitalares nos setores
- Diretório telefônico com busca de ramais
"""

import json
from datetime import datetime

def obter_tipo_turno(turno_text, horario_text=""):
    """Identifica o tipo de turno para aplicar cor correta com detecção hierárquica

    Prioridade:
    1. Detecta NOTURNO por horário (19:00-00:00 ou 19:00+) - IMPORTANTE para residências
    2. Detecta 24H (Sobreaviso/On-call que dura o dia inteiro)
    3. Detecta SOBREAVISO explícito
    4. Detecta FINAL DE SEMANA
    5. Detecta turnos específicos por horário
    6. Detecta ROTINA com horários
    7. Retorna OUTRO como fallback
    """
    if not turno_text:
        return "outro"

    turno = turno_text.lower()
    horario = horario_text.lower() if horario_text else ""

    # PRIORIDADE 1: Detecta NOTURNO por horário ANTES de 24H
    # Importante porque 19:00/00:00 é noturno, não 24h
    if horario and "/" in horario:
        try:
            entrada, saida = horario.split("/")
            entrada_h = int(entrada.split(":")[0])
            saida_h = int(saida.split(":")[0])

            # Noturno: entrada >= 19 (19:00 até 06:00 ou 00:00)
            # Exemplos: 19:00/00:00, 19:00/07:00, 20:00/06:00, 18:30/07:30
            if entrada_h >= 18:
                return "noturno"
        except:
            pass

    # PRIORIDADE 2: Detecta 24H (entrada = saída ou diferença grande)
    # Exemplos: "24:00/08:00", "07:00/07:00", "13:00/13:00" (on-call que dura o dia inteiro)
    if horario and "/" in horario:
        try:
            entrada, saida = horario.split("/")
            entrada = entrada.strip()
            saida = saida.strip()

            # Se entrada == saída, é plantão de 24h
            if entrada == saida:
                return "badge-24h"

            # Se está explícito como sobreaviso, marca como 24h
            if 'sobreaviso' in turno or '24h' in turno:
                return "badge-24h"

            # Detecta Diurno (07:00-19:00) - típico de residência
            try:
                entrada_h = int(entrada.split(":")[0])
                saida_h = int(saida.split(":")[0])
                # Se é 07:00/19:00, é diurno
                if entrada_h == 7 and saida_h == 19:
                    return "diurno"
            except:
                pass
        except:
            pass

    # PRIORIDADE 3: Detecta SOBREAVISO + FIM DE SEMANA (se entrada != saída, é só sobreaviso, não 24h)
    # Exemplos: "Ultrassonografia - Sobreaviso Final de Semana" com horário real
    if 'sobreaviso' in turno or 'sobre aviso' in turno:
        # Se tem horário e entrada == saída, já foi detectado como 24h acima
        # Se não, é sobreaviso normal com fim de semana como contexto
        # Mas detectar o período se disponível
        if any(x in turno for x in ['matutino', 'manhã', '07:00', '08:00', '06:00']):
            return "matutino"
        elif any(x in turno for x in ['vespertino', 'vespertina', 'tarde', '13:00', '14:00']):
            return "vespertino"
        elif any(x in turno for x in ['noturno', 'noturna', 'noite', '19:00']):
            return "noturno"
        # Sobreaviso sem período específico
        if horario and "/" in horario:
            try:
                entrada, saida = horario.split("/")
                entrada_h = int(entrada.split(":")[0])
                if entrada_h >= 6 and entrada_h < 12:
                    return "matutino"
                elif entrada_h >= 12 and entrada_h < 18:
                    return "vespertino"
                elif entrada_h >= 18 or entrada_h < 6:
                    return "noturno"
            except:
                pass
        return "sobreaviso"

    # PRIORIDADE 4: Detecta FINAL DE SEMANA (sem sobreaviso)
    # "Rotina Vespertino - Final de Semana" → vespertino (não cria badge própria)
    if 'final' in turno or 'finais' in turno or 'fim de semana' in turno or 'fds' in turno:
        # Se for final de semana, retorna o período específico
        if any(x in turno for x in ['matutino', 'manhã', '07:00', '08:00', '06:00']):
            return "matutino"
        elif any(x in turno for x in ['vespertino', 'vespertina', 'tarde', '13:00', '14:00']):
            return "vespertino"
        elif any(x in turno for x in ['noturno', 'noturna', 'noite', '19:00']):
            return "noturno"

        # Se não tem período explícito, detecta pelo horário
        if horario and "/" in horario:
            try:
                entrada, saida = horario.split("/")
                entrada_h = int(entrada.split(":")[0])
                # Matutino (6:00-13:00)
                if entrada_h >= 6 and entrada_h < 12:
                    return "matutino"
                # Vespertino (13:00-19:00)
                elif entrada_h >= 12 and entrada_h < 18:
                    return "vespertino"
                # Noturno (19:00-06:00)
                elif entrada_h >= 18 or entrada_h < 6:
                    return "noturno"
            except:
                pass

        # Se é rotina sem período específico
        if 'rotina' in turno:
            return "rotina"
        # Fallback
        return "outro"

    # PRIORIDADE 5: Detecta turnos específicos por horário/nome
    # Detecta por abreviações (P1, P2, P3, P4, DIA, NOITE) + horário
    if turno in ['p1', 'p2', 'p3', 'p4', 'dia', 'noite'] or (len(turno) <= 3 and turno.isalnum()):
        # P1, P2, P3 geralmente são matutino/vespertino, P4 é noturno
        if horario and "/" in horario:
            try:
                entrada, saida = horario.split("/")
                entrada_h = int(entrada.split(":")[0])
                saida_h = int(saida.split(":")[0])

                # Matutino (6:00-13:00)
                if entrada_h >= 6 and entrada_h < 12:
                    return "matutino"
                # Vespertino (13:00-19:00)
                elif entrada_h >= 12 and entrada_h < 18:
                    return "vespertino"
                # Noturno (19:00-06:00)
                elif entrada_h >= 18 or entrada_h < 6:
                    return "noturno"
            except:
                pass

    # Matutino (Verde)
    if any(x in turno for x in ['matutino', 'matutina', 'manhã', 'madrugada', '07:00', '08:00', '06:00']):
        return "matutino"

    # Vespertino (Laranja)
    if any(x in turno for x in ['vespertino', 'vespertina', 'tarde', '13:00', '14:00']):
        return "vespertino"

    # Noturno (Azul Escuro)
    if any(x in turno for x in ['noturno', 'noturna', 'noite', '19:00']):
        return "noturno"

    # Plantão (Coral)
    if 'plantão' in turno or 'plantao' in turno:
        if 'noturno' in turno or 'noite' in turno or '19:00' in turno:
            return "noturno"
        elif 'vespertino' in turno or 'tarde' in turno or '13:00' in turno:
            return "vespertino"
        elif 'matutino' in turno or 'manhã' in turno or '07:00' in turno:
            return "matutino"
        return "plantao"

    # PRIORIDADE 6: Detecta ROTINA com horário específico
    if 'rotina' in turno:
        if horario and "/" in horario:
            try:
                entrada, saida = horario.split("/")
                entrada_h = int(entrada.split(":")[0])
                saida_h = int(saida.split(":")[0])

                # Matutino (6:00-13:00)
                if entrada_h >= 6 and entrada_h < 12:
                    return "matutino"
                # Vespertino (13:00-19:00)
                elif entrada_h >= 12 and entrada_h < 18:
                    return "vespertino"
                # Noturno (19:00-06:00)
                elif entrada_h >= 18 or entrada_h < 6:
                    return "noturno"
            except:
                pass
        return "rotina"

    # FALLBACK: Detecta por horário como último recurso antes de retornar "outro"
    # Importante para turnos que não têm palavras-chave específicas (ex: Ambulatório, etc)
    if horario and "/" in horario:
        try:
            entrada, saida = horario.split("/")
            entrada_h = int(entrada.split(":")[0])
            saida_h = int(saida.split(":")[0])

            # Matutino (6:00-13:00)
            if entrada_h >= 6 and entrada_h < 12:
                return "matutino"
            # Vespertino (13:00-19:00)
            elif entrada_h >= 12 and entrada_h < 18:
                return "vespertino"
            # Noturno (19:00-06:00)
            elif entrada_h >= 18 or entrada_h < 6:
                return "noturno"
        except:
            pass

    return "outro"

def normalizar_turno(turno_text):
    """Normaliza nomes de turnos para ordem cronológica padrão"""
    if not turno_text:
        return (99, "Outro")

    turno = turno_text.lower().strip()
    turno_original = turno_text.strip()

    # HOSPITALISTA - COMANEJO vs URGÊNCIA (especial)
    if 'hospitalista' in turno:
        if 'comanejo' in turno:
            if 'matutino' in turno or '07:00' in turno:
                return (1, "Comanejo Matutino")
            elif 'vespertino' in turno or 'tarde' in turno or '13:00' in turno:
                return (2, "Comanejo Vespertino")
            elif 'noturno' in turno or '19:00' in turno:
                return (3, "Comanejo Noturno")
        elif 'urgência' in turno or 'urgencia' in turno:
            if 'matutino' in turno or '07:00' in turno:
                return (1, "Urgência Matutino")
            elif 'vespertino' in turno or 'tarde' in turno or '13:00' in turno:
                return (2, "Urgência Vespertino")
            elif 'noturno' in turno or '19:00' in turno:
                return (3, "Urgência Noturno")

    # MATUTINO (Ordem 1)
    if any(x in turno for x in ['matutino', 'matutina', 'manhã', 'madrugada', '07:00', '08:00', '06:00']):
        if 'final' in turno:
            return (1, "Manhã - Final de Semana")
        if 'p1' in turno:
            return (1, "Plantão Matutino - P1")
        elif 'p2' in turno:
            return (1, "Plantão Matutino - P2")
        return (1, "Plantão Matutino")

    # VESPERTINO (Ordem 2)
    if any(x in turno for x in ['vespertino', 'vespertina', 'tarde', '13:00', '14:00']):
        if 'final' in turno:
            return (2, "Tarde - Final de Semana")
        if 'p1' in turno:
            return (2, "Plantão Vespertino - P1")
        elif 'p2' in turno:
            return (2, "Plantão Vespertino - P2")
        return (2, "Plantão Vespertino")

    # NOTURNO (Ordem 3)
    if any(x in turno for x in ['noturno', 'noturna', 'noite', '19:00']):
        if 'p1' in turno:
            return (3, "Plantão Noturno - P1")
        elif 'p2' in turno:
            return (3, "Plantão Noturno - P2")
        return (3, "Plantão Noturno")

    # DIURNO (07:00-19:00) - Residência
    if turno == 'diurno':
        return (1, "Plantão Diurno")

    # DIA / NOITE (Residência - legacy)
    if turno == 'dia':
        return (1, "Plantão Diurno")
    elif turno == 'noite':
        return (3, "Período Noturno")

    # P1, P2, P3, P4 (Plantões standalone)
    if turno in ['p1', 'p2', 'p3', 'p4']:
        return (2, f"Plantão {turno.upper()}")

    # ROTINA (Ordem 4)
    if any(x in turno for x in ['rotina', 'regular', 'alojamento']):
        if 'matutino' in turno:
            return (1, "Rotina Matutino")
        elif 'vespertino' in turno or 'tarde' in turno:
            return (2, "Rotina Vespertino")
        elif 'noturno' in turno or 'noite' in turno:
            return (3, "Rotina Noturno")
        elif 'final' in turno:
            return (4, "Rotina - Final de Semana")
        return (4, "Rotina")

    # SOBREAVISO (Ordem 5)
    if 'sobreaviso' in turno:
        if 'cardiologia' in turno:
            return (5, "Sobreaviso Cardiologia")
        elif 'urologia' in turno:
            return (5, "Sobreaviso Urologia")
        elif 'cirurgia' in turno:
            if 'equipe 1' in turno or ' 1' in turno:
                return (5, "Sobreaviso Cirurgia - Equipe 1")
            elif 'equipe 2' in turno or ' 2' in turno:
                return (5, "Sobreaviso Cirurgia - Equipe 2")
            return (5, "Sobreaviso Cirurgia")
        elif 'oftalmologia' in turno:
            return (5, "Sobreaviso Oftalmologia")
        elif 'oncologia' in turno:
            return (5, "Sobreaviso Oncologia")
        elif 'endoscopia' in turno:
            return (5, "Sobreaviso Endoscopia")
        elif 'pediátrica' in turno or 'pediatrica' in turno:
            return (5, "Sobreaviso Cirurgia Pediátrica")
        elif 'vascular' in turno:
            return (5, "Sobreaviso Cirurgia Vascular")
        elif 'neurologia' in turno:
            return (5, "Sobreaviso Neurologia")
        elif 'neurocirurgia' in turno:
            return (5, "Sobreaviso Neurocirurgia")
        return (5, "Sobreaviso")

    # Plantão Diurno
    if 'plantão diurno' in turno:
        return (1, "Plantão Diurno")

    # Manter o original para casos não identificados
    return (99, turno_original)

def carregar_ramais_data():
    """Carrega dados de ramais e mapeamento de setores"""
    import os
    from pathlib import Path

    # Tentar carregar ramais_hro.json
    ramais_paths = [
        'ramais_hro.json',
        os.path.expanduser('~/escalaHRO/ramais_hro.json'),
        '/Users/joaoperes/escalaHRO/ramais_hro.json',
    ]

    ramais_data = None
    for path in ramais_paths:
        if Path(path).exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    ramais_data = json.load(f)
                print(f"✅ Ramais carregados de: {path}")
                break
            except Exception as e:
                print(f"⚠️  Erro ao ler {path}: {e}")
                continue

    # Tentar carregar setor_ramais_mapping.json
    mapping_paths = [
        'setor_ramais_mapping.json',
        os.path.expanduser('~/escalaHRO/setor_ramais_mapping.json'),
        '/Users/joaoperes/escalaHRO/setor_ramais_mapping.json',
    ]

    mapping_data = None
    for path in mapping_paths:
        if Path(path).exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    mapping_data = json.load(f)
                print(f"✅ Mapeamento de setores carregado de: {path}")
                break
            except Exception as e:
                print(f"⚠️  Erro ao ler {path}: {e}")
                continue

    return ramais_data, mapping_data

def obter_ramais_setor(setor_nome, ramais_data, mapping_data):
    """Obtém os ramais de um setor baseado no mapeamento"""
    if not ramais_data or not mapping_data:
        return []

    # Procurar o setor no mapeamento
    for mapping in mapping_data.get('sector_mappings', []):
        if mapping['dashboard_sector'] == setor_nome:
            # Encontrou o mapeamento, buscar os ramais
            extensions = []
            for dept_name in mapping['ramais_departments']:
                # Procurar o departamento nos ramais
                for dept in ramais_data.get('departments', []):
                    if dept['name'] == dept_name:
                        extensions.extend(dept['extensions'])
            return extensions

    return []

def formatar_ramais_display(extensions):
    """Formata ramais para exibição no cabeçalho do setor"""
    if not extensions:
        return ""

    # Remover duplicatas mantendo ordem
    unique_exts = []
    seen = set()
    for ext in extensions:
        if ext not in seen:
            unique_exts.append(ext)
            seen.add(ext)

    # Limitar exibição a 5 ramais para não poluir o cabeçalho
    if len(unique_exts) > 5:
        exts_str = ", ".join(unique_exts[:5])
        return f' <span class="setor-ramais" title="{", ".join(unique_exts)}">({exts_str}...)</span>'
    else:
        exts_str = ", ".join(unique_exts)
        return f' <span class="setor-ramais">({exts_str})</span>'

def gerar_dashboard():
    """Gera dashboard executivo com visual premium"""

    # Procurar pelos arquivos em múltiplos locais
    import os
    from pathlib import Path

    # Procurar arquivo de escalas
    # Prioritize extracao_inteligente.json (direct output from extraction)
    # Fallback to escalas_multiplos_dias.json for backward compatibility
    escala_paths = [
        '/tmp/extracao_inteligente.json',  # Primary: fresh from extraction
        '/tmp/escalas_multiplos_dias.json',  # Fallback: legacy intermediate file
        'extracao_inteligente.json',
        'escalas_multiplos_dias.json',
        os.path.expanduser('~/escalaHRO/extracao_inteligente.json'),
        os.path.expanduser('~/escalaHRO/escalas_multiplos_dias.json'),
    ]

    escalas = None
    for path in escala_paths:
        if Path(path).exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    escalas = json.load(f)
                print(f"✅ Escalas carregadas de: {path}")
                break
            except Exception as e:
                print(f"⚠️  Erro ao ler {path}: {e}")
                continue

    if escalas is None:
        print("❌ Arquivo de escalas não encontrado em nenhum local.")
        return

    # Procurar arquivo de profissionais
    prof_paths = [
        'profissionais_autenticacao.json',
        os.path.expanduser('~/escalaHRO/profissionais_autenticacao.json'),
        '/Users/joaoperes/escalaHRO/profissionais_autenticacao.json',
    ]

    profissionais_data = None
    for path in prof_paths:
        if Path(path).exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    profissionais_data = json.load(f)
                print(f"✅ Profissionais carregados de: {path}")
                break
            except Exception as e:
                print(f"⚠️  Erro ao ler {path}: {e}")
                continue

    if profissionais_data is None:
        print("❌ Arquivo de profissionais não encontrado em nenhum local.")
        return

    # Carregar dados de ramais
    ramais_data, mapping_data = carregar_ramais_data()

    if ramais_data is None:
        print("⚠️  Ramais não carregados - funcionalidade de extensões desabilitada")
    if mapping_data is None:
        print("⚠️  Mapeamento de setores não carregado - funcionalidade de extensões desabilitada")

    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="version" content="{datetime.now().strftime('%Y%m%d_%H%M%S')}">
    <title>Escala - ALVF</title>
    <link href="https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html, body {
            height: 100%;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #f8f9fb;
            color: #1a1a1a;
            line-height: 1.6;
        }

        #main-content {
            transition: filter 0.3s ease;
        }

        #main-content.blurred {
            filter: blur(8px);
            pointer-events: none;
        }

        /* Modal de Autenticação */
        .auth-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        }

        .auth-modal.hidden {
            display: none;
        }

        .auth-modal-content {
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            max-width: 400px;
            width: 90%;
            text-align: center;
        }

        .auth-modal-content h2 {
            color: #0d3b66;
            margin-bottom: 15px;
            font-size: 1.5em;
        }

        .auth-modal-content p {
            color: #666;
            margin-bottom: 20px;
            font-size: 0.95em;
        }

        .auth-input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
            margin-bottom: 15px;
            box-sizing: border-box;
            transition: border-color 0.3s ease;
        }

        .auth-input:focus {
            outline: none;
            border-color: #0d3b66;
            box-shadow: 0 0 0 3px rgba(13, 59, 102, 0.1);
        }

        .auth-btn {
            width: 100%;
            padding: 12px;
            background: #0d3b66;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .auth-btn:hover {
            background: #0a2f52;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(13, 59, 102, 0.2);
        }

        .auth-btn:active {
            transform: translateY(0);
        }

        .auth-error {
            color: #d9534f;
            font-size: 0.9em;
            margin-top: 10px;
            display: none;
        }

        .auth-error.show {
            display: block;
        }

        .auth-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e8eef7;
        }

        .auth-tab-btn {
            flex: 1;
            padding: 10px;
            background: none;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-size: 1em;
            color: #666;
            transition: all 0.3s ease;
        }

        .auth-tab-btn.active {
            color: #0d3b66;
            border-bottom-color: #0d3b66;
            font-weight: 600;
        }

        .auth-tab-btn:hover {
            color: #0d3b66;
        }

        .auth-tab-content {
            display: none;
        }

        .auth-tab-content.active {
            display: block;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: linear-gradient(135deg, #0d3b66 0%, #1a5490 100%);
            padding: 25px 30px;
            border-radius: 16px;
            margin-bottom: 25px;
            box-shadow: 0 8px 24px rgba(13, 59, 102, 0.2);
            position: relative;
            overflow: hidden;
        }

        .header::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -5%;
            width: 400px;
            height: 400px;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            position: relative;
            z-index: 1;
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 20px;
            flex: 1;
            min-width: 0;
        }

        .header-logo {
            font-family: 'Merriweather', serif;
            font-size: 2em;
            font-weight: 700;
            color: white;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            white-space: nowrap;
        }

        .header-separator {
            width: 2px;
            height: 60px;
            background: rgba(255, 255, 255, 0.3);
            border-radius: 2px;
        }

        .header-info {
            flex: 1;
            min-width: 0;
        }

        .header-info h2 {
            color: white;
            font-size: 1.4em;
            font-weight: 600;
            margin: 0 0 5px 0;
            text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
        }

        .header-description {
            color: rgba(255, 255, 255, 0.95);
            font-size: 0.95em;
            line-height: 1.4;
        }

        .header-description p {
            margin: 2px 0;
        }

        .header-right {
            text-align: right;
            color: rgba(255, 255, 255, 0.95);
            font-size: 0.9em;
            flex-shrink: 0;
        }

        .header-date {
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 5px;
        }

        .controls-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            gap: 15px;
            flex-wrap: wrap;
        }

        .date-selector {
            display: flex;
            gap: 10px;
        }

        .date-btn {
            padding: 10px 18px;
            background: white;
            border: 2px solid #e8eef7;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.95em;
            font-weight: 500;
            color: #666;
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
        }

        .date-btn:hover {
            border-color: #0d3b66;
            color: #0d3b66;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(13, 59, 102, 0.1);
        }

        .date-btn.active {
            background: #0d3b66;
            color: white;
            border-color: #0d3b66;
            box-shadow: 0 4px 12px rgba(13, 59, 102, 0.2);
        }

        .search-section {
            flex: 1;
            min-width: 250px;
        }

        .search-input {
            width: 100%;
            padding: 12px 20px;
            border: 2px solid #e8eef7;
            border-radius: 8px;
            font-size: 0.95em;
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
        }

        .search-input:focus {
            outline: none;
            border-color: #0d3b66;
            background: #f8fbff;
            box-shadow: 0 0 0 3px rgba(13, 59, 102, 0.1);
        }

        .action-buttons {
            display: flex;
            gap: 10px;
        }

        .btn {
            padding: 10px 18px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 500;
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
        }

        .btn-toggle-sections {
            background: white;
            color: #0d3b66;
            border: 2px solid #0d3b66;
        }

        .btn-toggle-sections:hover {
            background: #0d3b66;
            color: white;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(13, 59, 102, 0.15);
        }

        .btn-toggle-sections.collapsed {
            background: #0d3b66;
            color: white;
        }

        .btn-contacts {
            background: #0d3b66;
            color: white;
        }

        .btn-contacts:hover {
            background: #0a2947;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(13, 59, 102, 0.3);
        }

        .btn-ramais {
            background: #0d3b66;
            color: white;
        }

        .btn-ramais:hover {
            background: #0a2947;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(13, 59, 102, 0.3);
        }

        .btn-print {
            background: #6c757d;
            color: white;
        }

        .btn-print:hover {
            background: #5a6268;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(108, 117, 125, 0.3);
        }

        .btn-print::before {
            content: '';
            display: inline-block;
            width: 0;
            height: 0;
            border-top: 6px solid transparent;
            border-bottom: 6px solid transparent;
            border-right: 10px solid #0d3b66;
            margin-right: 8px;
        }

        /* Modal de Contatos */
        .contacts-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 5000;
            display: none;
        }

        .contacts-modal.active {
            display: flex;
        }

        .contacts-modal-content {
            background: white;
            border-radius: 12px;
            padding: 30px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        }

        .contacts-modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 2px solid #e8eef7;
            padding-bottom: 15px;
        }

        .contacts-modal-header h2 {
            color: #0d3b66;
            font-size: 1.5em;
            margin: 0;
        }

        .contacts-modal-close {
            background: none;
            border: none;
            font-size: 1.5em;
            color: #666;
            cursor: pointer;
            padding: 0;
        }

        .contacts-modal-close:hover {
            color: #0d3b66;
        }

        .contacts-search {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 1em;
        }

        .contacts-warning {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 20px;
            font-size: 0.9em;
        }

        .contact-item {
            padding: 12px 15px;
            border-bottom: 1px solid #f0f0f0;
            transition: background 0.2s ease;
        }

        .contact-item:hover {
            background: #f8f9fa;
        }

        .contact-name {
            font-weight: 600;
            color: #0d3b66;
            margin-bottom: 5px;
        }

        .contact-info {
            color: #666;
            font-size: 0.95em;
        }

        .contact-phone {
            color: #28a745;
            text-decoration: none;
        }

        .contact-phone:hover {
            text-decoration: underline;
        }

        /* Modal de Ramais */
        .ramais-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 5000;
            display: none;
        }

        .ramais-modal.active {
            display: flex;
        }

        .ramais-modal-content {
            background: white;
            border-radius: 12px;
            padding: 30px;
            max-width: 800px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        }

        .ramais-modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-bottom: 2px solid #e8eef7;
            padding-bottom: 15px;
        }

        .ramais-modal-header h2 {
            color: #0d3b66;
            font-size: 1.5em;
            margin: 0;
        }

        .ramais-modal-close {
            background: none;
            border: none;
            font-size: 1.5em;
            color: #666;
            cursor: pointer;
            padding: 0;
            line-height: 1;
        }

        .ramais-modal-close:hover {
            color: #0d3b66;
        }

        .ramais-search {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 1em;
        }

        .ramais-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 12px;
        }

        .ramal-item {
            padding: 12px 15px;
            border: 1px solid #e8eef7;
            border-radius: 8px;
            transition: all 0.2s ease;
            background: white;
        }

        .ramal-item:hover {
            background: #f8fbff;
            border-color: #0d3b66;
            box-shadow: 0 2px 8px rgba(13, 59, 102, 0.1);
        }

        .ramal-dept {
            font-weight: 600;
            color: #0d3b66;
            margin-bottom: 5px;
            font-size: 0.95em;
        }

        .ramal-exts {
            color: #28a745;
            font-size: 0.9em;
            font-weight: 500;
        }

        .ramal-exts-label {
            color: #666;
            font-size: 0.85em;
            margin-right: 5px;
        }

        /* Estilo dos ramais no cabeçalho do setor */
        .setor-ramais {
            color: #6610f2;
            font-weight: 500;
            font-size: 0.9em;
            margin-left: 8px;
        }

        .date-display {
            text-align: center;
            font-size: 1.2em;
            font-weight: 600;
            color: #0d3b66;
            margin-bottom: 15px;
            padding: 12px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(13, 59, 102, 0.1);
        }

        .last-update {
            text-align: center;
            font-size: 0.9em;
            color: #666;
            margin-bottom: 20px;
            padding: 10px;
            background: white;
            border-radius: 8px;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
        }

        .update-status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }

        .update-status-indicator.sucesso {
            background: #28a745;
            box-shadow: 0 0 8px rgba(40, 167, 69, 0.4);
        }

        .update-status-indicator.pendente {
            background: #ffc107;
            box-shadow: 0 0 8px rgba(255, 193, 7, 0.4);
        }

        .update-status-indicator.erro {
            background: #dc3545;
            box-shadow: 0 0 8px rgba(220, 53, 69, 0.4);
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
            border-left: 4px solid #0d3b66;
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        }

        .stat-number {
            font-size: 2em;
            font-weight: 700;
            color: #0d3b66;
            margin-bottom: 5px;
        }

        .stat-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .category {
            background: white;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .category:hover {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        }

        .categoria-header {
            background: linear-gradient(135deg, #f8fbff 0%, #e8eef7 100%);
            padding: 18px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-left: 4px solid #0d3b66;
            transition: all 0.3s ease;
        }

        .categoria-header:hover {
            background: linear-gradient(135deg, #e8eef7 0%, #d8dfe7 100%);
        }

        .categoria-header-text {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex: 1;
        }

        .categoria-nome {
            font-size: 1.15em;
            font-weight: 600;
            color: #0d3b66;
        }

        .categoria-count {
            color: #666;
            font-size: 0.9em;
            font-weight: 500;
        }

        .categoria-toggle {
            color: #0d3b66;
            font-size: 1.2em;
            transition: transform 0.3s ease;
        }

        .categoria-header:not(.expanded) .categoria-toggle {
            transform: rotate(180deg);
        }

        .categoria-content {
            padding: 20px;
            transition: all 0.3s ease;
            max-height: 10000px;
            overflow: hidden;
        }

        .categoria-content.collapsed {
            max-height: 0;
            padding: 0 20px;
        }

        .turnos-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 15px;
        }

        .turno-coluna {
            background: #f8fbff;
            border-radius: 8px;
            padding: 15px;
            border: 2px solid #e8eef7;
            transition: all 0.3s ease;
        }

        .turno-coluna:hover {
            border-color: #0d3b66;
            box-shadow: 0 2px 8px rgba(13, 59, 102, 0.1);
        }

        .turno-title {
            font-weight: 600;
            color: #0d3b66;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e8eef7;
            font-size: 1em;
        }

        .turno-title::after {
            content: ' (' attr(data-count) ')';
            color: #666;
            font-size: 0.9em;
            font-weight: 500;
        }

        .profissionais-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .profissional {
            padding: 12px;
            background: white;
            border-radius: 6px;
            border: 1px solid #e8eef7;
            transition: all 0.2s ease;
        }

        .profissional:hover {
            border-color: #0d3b66;
            box-shadow: 0 2px 8px rgba(13, 59, 102, 0.1);
            transform: translateX(2px);
        }

        .profissional-nome {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;
        }

        .profissional-nome-wrapper {
            flex: 1;
        }

        .profissional-nome-text {
            font-weight: 600;
            color: #1a1a1a;
            font-size: 0.95em;
        }

        .profissional-info {
            font-size: 0.85em;
            color: #666;
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }

        .info-label {
            font-weight: 500;
            color: #999;
        }

        .turno-badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.75em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }

        .turno-badge.matutino {
            background: #d4edda;
            color: #155724;
        }

        .turno-badge.vespertino {
            background: #fff3cd;
            color: #856404;
        }

        .turno-badge.noturno {
            background: #d1ecf1;
            color: #0c5460;
        }

        .turno-badge.badge-24h {
            background: #f8d7da;
            color: #721c24;
        }

        .turno-badge.sobreaviso {
            background: #e7e7ff;
            color: #4a4a8a;
        }

        .turno-badge.rotina {
            background: #e2e3e5;
            color: #383d41;
        }

        .turno-badge.plantao {
            background: #ffdab9;
            color: #8b4513;
        }

        .turno-badge.diurno {
            background: #d4edda;
            color: #155724;
        }

        .turno-badge.outro {
            background: #e2e3e5;
            color: #6c757d;
        }

        .telefone-tooltip {
            color: #28a745;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            transition: all 0.2s ease;
        }

        .telefone-tooltip:hover {
            color: #218838;
            text-decoration: underline;
        }

        .telefone-icon {
            width: 16px;
            height: 16px;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%2328a745"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>') center/contain no-repeat;
        }

        .data-tabs {
            display: flex;
            gap: 5px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e8eef7;
            padding-bottom: 5px;
        }

        .data-tab {
            flex: 1;
            padding: 12px;
            text-align: center;
            background: white;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-size: 1em;
            font-weight: 500;
            color: #666;
            transition: all 0.3s ease;
            border-radius: 8px 8px 0 0;
            position: relative;
            bottom: -2px;
        }

        .data-tab:hover {
            color: #0d3b66;
        }

        .data-tab.active {
            color: #0d3b66;
            border-bottom-color: #0d3b66;
        }

        .data-tab.inactive {
            opacity: 0.6;
        }

        .data-content {
            display: none;
        }

        .data-content.ativo {
            display: block;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }

        /* Responsivo */
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                text-align: center;
                gap: 10px;
                padding: 0 10px;
            }

            .header-left {
                flex: none;
                min-width: auto;
                width: 100%;
                justify-content: center;
                gap: 8px;
            }

            .header-right {
                flex: none;
                min-width: auto;
                width: 100%;
                justify-content: center;
                text-align: center;
                gap: 8px;
            }

            .header-logo {
                font-size: 1.5em;
            }

            .header-separator {
                display: none;
            }

            .header-info {
                text-align: center;
            }

            .header-info h2 {
                font-size: 1.2em;
            }

            .header-description p {
                font-size: 0.85em;
                line-height: 1.2;
            }

            .controls-bar {
                flex-direction: column;
                align-items: stretch;
                gap: 10px;
            }

            .search-section {
                min-width: auto;
                width: 100%;
            }

            .action-buttons {
                width: 100%;
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                justify-content: center;
            }

            .action-buttons .btn {
                flex: 1;
                min-width: 120px;
                font-size: 0.95em;
                padding: 10px 8px;
            }

            .turnos-container {
                grid-template-columns: 1fr;
            }

            .stats {
                grid-template-columns: 1fr;
            }

            .date-btn {
                padding: 8px 12px;
                font-size: 0.9em;
            }
        }

        /* Estilos para Impressão - 1 página A4 máxima compactação */
        @media print {
            @page {
                size: A4;
                margin: 1mm;
            }

            * {
                box-shadow: none !important;
                margin: 0 !important;
                padding: 0 !important;
            }

            html, body {
                height: 100%;
                background: white;
                font-family: Arial, sans-serif;
                font-size: 5pt;
                line-height: 1;
            }

            .container {
                max-width: 100%;
                width: 100%;
                padding: 1mm !important;
            }

            /* Ocultar tudo exceto conteúdo */
            .controls-bar,
            .header,
            .dashboard-description,
            .contacts-modal,
            .ramais-modal,
            .date-display,
            .categoria-toggle,
            .stats,
            .categoria-header-text,
            .categoria-count {
                display: none !important;
            }

            /* Mostrar apenas conteúdo das categorias */
            .category {
                display: block !important;
                margin: 0 !important;
                padding: 0 !important;
                page-break-inside: avoid;
                break-inside: avoid;
            }

            .categoria-header {
                background: transparent !important;
                border-left: none !important;
                padding: 0.3mm !important;
                margin: 0.3mm 0 !important;
                font-size: 4.5pt !important;
                font-weight: bold !important;
                display: block !important;
            }

            .categoria-content {
                display: block !important;
                max-height: none !important;
                padding: 0 !important;
                margin: 0 !important;
            }

            .turnos-container {
                display: grid !important;
                grid-template-columns: 1fr 1fr 1fr !important;
                gap: 0.5mm !important;
                padding: 0 !important;
            }

            /* Colunas de turno extremamente compactas */
            .turno-coluna {
                page-break-inside: avoid;
                break-inside: avoid;
                margin: 0 !important;
                padding: 0.3mm !important;
                border: 0.5pt solid #e0e0e0;
                background: white;
                display: block !important;
            }

            .turno-title {
                font-weight: bold;
                font-size: 4.5pt;
                margin: 0 0 0.2mm 0 !important;
                padding: 0 !important;
                color: #0d3b66;
                page-break-inside: avoid;
                break-inside: avoid;
                border-bottom: 0.5pt solid #e0e0e0;
            }

            .profissionais-list {
                display: block !important;
            }

            /* Profissionais extremamente compactos */
            .profissional {
                page-break-inside: avoid;
                break-inside: avoid;
                margin: 0.1mm 0 !important;
                padding: 0.1mm 0 !important;
                border: none !important;
                font-size: 4pt;
                line-height: 1;
                display: block;
            }

            .profissional-nome {
                font-weight: bold;
                margin: 0 !important;
                padding: 0 !important;
                font-size: 4pt;
                display: inline;
            }

            .profissional-nome-wrapper {
                display: inline !important;
            }

            .profissional-nome-text {
                color: #000;
                margin: 0 !important;
            }

            .profissional-info {
                font-size: 3.5pt;
                color: #333;
                margin: 0 !important;
                padding: 0 !important;
                display: inline;
            }

            .telefone-tooltip,
            .telefone-icon,
            a.telefone-tooltip {
                display: none !important;
            }

            .turno-badge {
                font-size: 3pt !important;
                padding: 0.1pt 1pt !important;
                margin: 0 0.5pt !important;
                display: inline-block;
                border-radius: 1pt;
            }

            /* Remover todos os espaçamentos extras */
            .info-label {
                display: none;
            }

            /* Mostrar apenas o essencial: nome e horário */
            .profissional-info::before {
                content: ' ';
                margin: 0;
            }

            /* Ocultar elementos flutuantes */
            .contacts-modal-overlay,
            .contacts-modal,
            .ramais-modal {
                display: none !important;
            }

            /* Ocultar ramais no print */
            .setor-ramais {
                display: none !important;
            }
        }
    </style>
</head>
<body>
    <!-- Modal de Autenticação -->
    <div id="auth-modal" class="auth-modal">
        <div class="auth-modal-content">
            <h2>Acesso Restrito</h2>

            <!-- Abas de Autenticação -->
            <div class="auth-tabs">
                <button class="auth-tab-btn active" onclick="trocarAbaAuth('profissional')">Profissional</button>
                <button class="auth-tab-btn" onclick="trocarAbaAuth('outro')">Outro Usuário</button>
            </div>

            <!-- Conteúdo: Profissional -->
            <div id="auth-content-profissional" class="auth-tab-content active">
                <p>Entre com seu email ou últimos 4 dígitos do telefone cadastrado no app.</p>
                <input type="text" id="auth-input-prof" placeholder="Email ou últimos 4 dígitos do telefone" class="auth-input" onkeypress="if(event.key === 'Enter') autenticarProfissional()">
                <button onclick="autenticarProfissional()" class="auth-btn">Acessar</button>
                <p id="auth-error-prof" class="auth-error"></p>
            </div>

            <!-- Conteúdo: Outro Usuário -->
            <div id="auth-content-outro" class="auth-tab-content">
                <p>Acesso para administrativo, enfermagem e outros usuários.</p>
                <p style="color: #666; font-size: 0.9em; margin: 15px 0;">Se você não possui acesso, entre em contato conosco para solicitar a senha.</p>
                <input type="password" id="auth-input-outro" placeholder="Digite a senha" class="auth-input" onkeypress="if(event.key === 'Enter') autenticarOutro()">
                <button onclick="autenticarOutro()" class="auth-btn">Acessar</button>
                <p id="auth-error-outro" class="auth-error"></p>
            </div>
        </div>
    </div>

    <!-- Modal de Contatos -->
    <div id="contacts-modal" class="contacts-modal">
        <div class="contacts-modal-content">
            <div class="contacts-modal-header">
                <h2>Lista de Contatos</h2>
                <button class="contacts-modal-close" onclick="fecharListaContatos()">✕</button>
            </div>
            <input type="text" class="contacts-search" id="contacts-search" placeholder="Buscar por nome ou telefone..." onkeyup="filtrarContatos()">
            <div class="contacts-warning">
                <p>⚠️ <strong>Aviso:</strong> Os números de telefone são obtidos do cadastro do app Escalas e podem estar desatualizados. Recomenda-se fazer uma verificação antes de contatar.</p>
            </div>
            <div class="contacts-list" id="contacts-list"></div>
        </div>
    </div>

    <!-- Modal de Ramais -->
    <div id="ramais-modal" class="ramais-modal">
        <div class="ramais-modal-content">
            <div class="ramais-modal-header">
                <h2>📞 Diretório Telefônico HRO</h2>
                <button class="ramais-modal-close" onclick="fecharDiretorioRamais()">✕</button>
            </div>
            <input type="text" class="ramais-search" id="ramais-search" placeholder="Buscar por departamento ou ramal..." onkeyup="filtrarRamais()">
            <div class="ramais-list" id="ramais-list"></div>
        </div>
    </div>

    <!-- Main content wrapper for blur effect -->
    <div id="main-content" class="blurred">
    <div class="container">
        <!-- Header Banner -->
        <div class="header">
            <div class="header-content">
                <div class="header-left">
                    <div class="header-logo">ALVF</div>
                    <div class="header-separator"></div>
                    <div class="header-info">
                        <h2>Hospital Regional do Oeste (HRO)</h2>
                        <div class="header-description">
                            <p>Escala Médica</p>
                        </div>
                    </div>
                </div>
                <div class="header-right">
                    <div class="header-date" id="data-atual-header"></div>
                    <div>Atualização em tempo real</div>
                </div>
            </div>
        </div>

        <!-- Controles -->
        <div class="controls-bar">
            <div class="date-selector">
                <button class="date-btn" data-dia="anterior" onclick="selecionarDia('anterior')">Dia Anterior</button>
                <button class="date-btn active" data-dia="atual" onclick="selecionarDia('atual')">📅 Hoje</button>
            </div>
            <div class="search-section">
                <input type="text" class="search-input" id="search" placeholder="Busque por nome, setor, turno..." onkeyup="filtrarProfissionais()">
            </div>
            <div class="action-buttons">
                <button class="btn btn-toggle-sections" id="toggle-btn" onclick="alternarSeccoes()">Minimizar</button>
                <button class="btn btn-contacts" onclick="abrirListaContatos()">📋 Contatos</button>
                <button class="btn btn-ramais" onclick="abrirDiretorioRamais()">📞 Ramais</button>
            </div>
        </div>

        <!-- Data selecionada -->
        <div class="date-display" id="data-selecionada"></div>

        <!-- Última atualização -->
        <div class="last-update">
            <span class="update-status-indicator" id="status-indicator"></span>
            <span id="ultima-atualizacao">Carregando...</span>
        </div>

        <!-- Estatísticas -->
        <div class="stats" id="stats"></div>

        <!-- Categorias -->
        <div id="categorias"></div>
    </div>

    <script>
        // Dados das escalas
        const escalas = """ + json.dumps(escalas, ensure_ascii=False) + """;

        let diaSelecionado = 'atual';

        // Especialidades que devem ser divididas por turno
        const especialidadesComTurno = [
            'plantão', 'sobreaviso', 'residência', 'uti', 'pronto', 'urgência',
            'emergência', 'on-call', 'clinica', 'cirurgia', 'pediatria'
        ];

        // Dados de ramais e mapeamento
        const ramaisData = """ + json.dumps(ramais_data if ramais_data else {}, ensure_ascii=False) + """;
        const setorRamaisMapping = """ + json.dumps(mapping_data if mapping_data else {}, ensure_ascii=False) + """;

        // Função para obter ramais de um setor
        function obterRamaisSetor(setorNome) {
            if (!ramaisData.departments || !setorRamaisMapping.sector_mappings) {
                return [];
            }

            // Procurar o setor no mapeamento
            const mapping = setorRamaisMapping.sector_mappings.find(m => m.dashboard_sector === setorNome);
            if (!mapping) {
                return [];
            }

            // Coletar todos os ramais dos departamentos mapeados
            const extensions = [];
            mapping.ramais_departments.forEach(deptName => {
                const dept = ramaisData.departments.find(d => d.name === deptName);
                if (dept) {
                    extensions.push(...dept.extensions);
                }
            });

            return extensions;
        }

        // Função para formatar ramais para exibição
        function formatarRamaisDisplay(extensions) {
            if (!extensions || extensions.length === 0) {
                return '';
            }

            // Remover duplicatas
            const uniqueExts = [...new Set(extensions)];

            // Limitar exibição a 5 ramais
            if (uniqueExts.length > 5) {
                const extsStr = uniqueExts.slice(0, 5).join(', ');
                const allExtsStr = uniqueExts.join(', ');
                return ` <span class="setor-ramais" title="${allExtsStr}">(${extsStr}...)</span>`;
            } else {
                const extsStr = uniqueExts.join(', ');
                return ` <span class="setor-ramais">(${extsStr})</span>`;
            }
        }

        // Funções para o modal de ramais
        function abrirDiretorioRamais() {
            const modal = document.getElementById('ramais-modal');
            modal.classList.add('active');
            renderizarDiretorioRamais();
        }

        function fecharDiretorioRamais() {
            const modal = document.getElementById('ramais-modal');
            modal.classList.remove('active');
        }

        function renderizarDiretorioRamais() {
            const ramaisList = document.getElementById('ramais-list');

            if (!ramaisData.departments) {
                ramaisList.innerHTML = '<p style="text-align: center; color: #666;">Dados de ramais não disponíveis.</p>';
                return;
            }

            const departamentos = [...ramaisData.departments].sort((a, b) =>
                a.name.localeCompare(b.name, 'pt-BR')
            );

            ramaisList.innerHTML = departamentos.map(dept => {
                const extsStr = dept.extensions.join(', ');
                return `
                    <div class="ramal-item" data-search="${dept.name.toLowerCase()} ${extsStr}">
                        <div class="ramal-dept">${dept.name}</div>
                        <div class="ramal-exts">
                            <span class="ramal-exts-label">Ramais:</span>
                            ${extsStr}
                        </div>
                    </div>
                `;
            }).join('');
        }

        function filtrarRamais() {
            const searchText = document.getElementById('ramais-search').value.toLowerCase();
            const ramalItems = document.querySelectorAll('.ramal-item');

            ramalItems.forEach(item => {
                const searchData = item.getAttribute('data-search');
                if (searchData.includes(searchText)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        }

        // Fechar modal de ramais ao clicar fora
        document.getElementById('ramais-modal').addEventListener('click', function(e) {
            if (e.target === this) {
                fecharDiretorioRamais();
            }
        });

        function trocarAbaAuth(aba) {
            // Trocar aba ativa
            document.querySelectorAll('.auth-tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.auth-tab-content').forEach(content => content.classList.remove('active'));

            if (aba === 'profissional') {
                document.querySelector('.auth-tab-btn:first-child').classList.add('active');
                document.getElementById('auth-content-profissional').classList.add('active');
            } else {
                document.querySelector('.auth-tab-btn:last-child').classList.add('active');
                document.getElementById('auth-content-outro').classList.add('active');
            }

            // Limpar mensagens de erro
            document.querySelectorAll('.auth-error').forEach(err => err.classList.remove('show'));
        }

        function filtrarProfissionais() {
            const search = document.getElementById('search').value.toLowerCase().trim();
            const profissionais = document.querySelectorAll('.profissional');

            if (!search) {
                profissionais.forEach(prof => prof.style.display = 'block');
                return;
            }

            let visibleCount = 0;
            profissionais.forEach(prof => {
                const searchText = prof.getAttribute('data-search') || '';
                if (searchText.includes(search)) {
                    prof.style.display = 'block';
                    visibleCount++;
                } else {
                    prof.style.display = 'none';
                }
            });

            console.log(`Busca: "${search}" - ${visibleCount} resultados`);
        }

        function normalizarTurno(turnoText) {
            if (!turnoText) return { ordem: 99, nome: 'Outro' };

            const turno = turnoText.toLowerCase().trim();
            const turnoOriginal = turnoText.trim();

            // HOSPITALISTA - COMANEJO vs URGÊNCIA (especial)
            if (turno.includes('hospitalista')) {
                if (turno.includes('comanejo')) {
                    if (turno.includes('matutino') || turno.includes('07:00')) {
                        return { ordem: 1, nome: 'Comanejo Matutino' };
                    } else if (turno.includes('vespertino') || turno.includes('tarde') || turno.includes('13:00')) {
                        return { ordem: 2, nome: 'Comanejo Vespertino' };
                    } else if (turno.includes('noturno') || turno.includes('19:00')) {
                        return { ordem: 3, nome: 'Comanejo Noturno' };
                    }
                } else if (turno.includes('urgência') || turno.includes('urgencia')) {
                    if (turno.includes('matutino') || turno.includes('07:00')) {
                        return { ordem: 1, nome: 'Urgência Matutino' };
                    } else if (turno.includes('vespertino') || turno.includes('tarde') || turno.includes('13:00')) {
                        return { ordem: 2, nome: 'Urgência Vespertino' };
                    } else if (turno.includes('noturno') || turno.includes('19:00')) {
                        return { ordem: 3, nome: 'Urgência Noturno' };
                    }
                }
            }

            // MATUTINO (Ordem 1)
            if (['matutino', 'matutina', 'manhã', 'madrugada', '07:00', '08:00', '06:00'].some(x => turno.includes(x))) {
                if (turno.includes('final')) {
                    return { ordem: 1, nome: 'Manhã - Final de Semana' };
                }
                if (turno.includes('p1')) {
                    return { ordem: 1, nome: 'Plantão Matutino - P1' };
                } else if (turno.includes('p2')) {
                    return { ordem: 1, nome: 'Plantão Matutino - P2' };
                }
                return { ordem: 1, nome: 'Plantão Matutino' };
            }

            // VESPERTINO (Ordem 2)
            if (['vespertino', 'vespertina', 'tarde', '13:00', '14:00'].some(x => turno.includes(x))) {
                if (turno.includes('final')) {
                    return { ordem: 2, nome: 'Tarde - Final de Semana' };
                }
                if (turno.includes('p1')) {
                    return { ordem: 2, nome: 'Plantão Vespertino - P1' };
                } else if (turno.includes('p2')) {
                    return { ordem: 2, nome: 'Plantão Vespertino - P2' };
                }
                return { ordem: 2, nome: 'Plantão Vespertino' };
            }

            // NOTURNO (Ordem 3)
            if (['noturno', 'noturna', 'noite', '19:00'].some(x => turno.includes(x))) {
                if (turno.includes('p1')) {
                    return { ordem: 3, nome: 'Plantão Noturno - P1' };
                } else if (turno.includes('p2')) {
                    return { ordem: 3, nome: 'Plantão Noturno - P2' };
                }
                return { ordem: 3, nome: 'Plantão Noturno' };
            }

            // DIURNO (07:00-19:00) - Residência
            if (turno === 'diurno') {
                return { ordem: 1, nome: 'Plantão Diurno' };
            }

            // DIA / NOITE (Residência - legacy)
            if (turno === 'dia') {
                return { ordem: 1, nome: 'Plantão Diurno' };
            } else if (turno === 'noite') {
                return { ordem: 3, nome: 'Período Noturno' };
            }

            // P1, P2, P3, P4 (Plantões standalone)
            if (['p1', 'p2', 'p3', 'p4'].includes(turno)) {
                return { ordem: 2, nome: `Plantão ${turno.toUpperCase()}` };
            }

            // ROTINA (Ordem 4)
            if (['rotina', 'regular', 'alojamento'].some(x => turno.includes(x))) {
                if (turno.includes('matutino')) {
                    return { ordem: 1, nome: 'Rotina Matutino' };
                } else if (turno.includes('vespertino') || turno.includes('tarde')) {
                    return { ordem: 2, nome: 'Rotina Vespertino' };
                } else if (turno.includes('noturno') || turno.includes('noite')) {
                    return { ordem: 3, nome: 'Rotina Noturno' };
                } else if (turno.includes('final')) {
                    return { ordem: 4, nome: 'Rotina - Final de Semana' };
                }
                return { ordem: 4, nome: 'Rotina' };
            }

            // SOBREAVISO (Ordem 5)
            if (turno.includes('sobreaviso')) {
                if (turno.includes('cardiologia')) return { ordem: 5, nome: 'Sobreaviso Cardiologia' };
                if (turno.includes('urologia')) return { ordem: 5, nome: 'Sobreaviso Urologia' };
                if (turno.includes('cirurgia')) {
                    if (turno.includes('equipe 1') || turno.includes(' 1')) {
                        return { ordem: 5, nome: 'Sobreaviso Cirurgia - Equipe 1' };
                    } else if (turno.includes('equipe 2') || turno.includes(' 2')) {
                        return { ordem: 5, nome: 'Sobreaviso Cirurgia - Equipe 2' };
                    }
                    return { ordem: 5, nome: 'Sobreaviso Cirurgia' };
                }
                if (turno.includes('oftalmologia')) return { ordem: 5, nome: 'Sobreaviso Oftalmologia' };
                if (turno.includes('oncologia')) return { ordem: 5, nome: 'Sobreaviso Oncologia' };
                if (turno.includes('endoscopia')) return { ordem: 5, nome: 'Sobreaviso Endoscopia' };
                if (turno.includes('pediátrica') || turno.includes('pediatrica')) return { ordem: 5, nome: 'Sobreaviso Cirurgia Pediátrica' };
                if (turno.includes('vascular')) return { ordem: 5, nome: 'Sobreaviso Cirurgia Vascular' };
                if (turno.includes('neurologia')) return { ordem: 5, nome: 'Sobreaviso Neurologia' };
                if (turno.includes('neurocirurgia')) return { ordem: 5, nome: 'Sobreaviso Neurocirurgia' };
                return { ordem: 5, nome: 'Sobreaviso' };
            }

            // Plantão Diurno
            if (turno.includes('plantão diurno')) return { ordem: 1, nome: 'Plantão Diurno' };

            return { ordem: 99, nome: turnoOriginal };
        }

        function temMultiplosTurnos(setor) {
            const setorLower = setor.toLowerCase();
            return especialidadesComTurno.some(esp => setorLower.includes(esp));
        }

        function obterTipoTurno(turnoText, horarioText = '') {
            // Identifica o tipo de turno com detecção hierárquica
            // Prioridade: 24H → SOBREAVISO+FIM SEMANA → FIM SEMANA → Específico → ROTINA → OUTRO
            if (!turnoText) return 'outro';

            const turno = turnoText.toLowerCase();
            const horario = horarioText ? horarioText.toLowerCase() : '';

            // PRIORIDADE 1: Detecta 24H (entrada == saída)
            if (horario && horario.includes('/')) {
                try {
                    const [entrada, saida] = horario.split('/').map(x => x.trim());
                    if (entrada === saida) {
                        return 'badge-24h';
                    }
                    if (turno.includes('sobreaviso') || turno.includes('24h')) {
                        return 'badge-24h';
                    }
                    // Detecta Diurno (07:00-19:00) - típico de residência
                    try {
                        const entradaH = parseInt(entrada.split(':')[0]);
                        const saidaH = parseInt(saida.split(':')[0]);
                        if (entradaH === 7 && saidaH === 19) {
                            return 'diurno';
                        }
                    } catch (e) {}
                } catch (e) {}
            }

            // PRIORIDADE 2: Detecta SOBREAVISO (com ou sem fim de semana)
            if (turno.includes('sobreaviso') || turno.includes('sobre aviso')) {
                // Se tem período específico, retorna esse período
                if (['matutino', 'manhã', '07:00', '08:00', '06:00'].some(x => turno.includes(x))) return 'matutino';
                if (['vespertino', 'vespertina', 'tarde', '13:00', '14:00'].some(x => turno.includes(x))) return 'vespertino';
                if (['noturno', 'noturna', 'noite', '19:00'].some(x => turno.includes(x))) return 'noturno';
                // Se não tem período, detecta pelo horário
                if (horario && horario.includes('/')) {
                    try {
                        const [entrada] = horario.split('/')[0].split(':');
                        const entradaH = parseInt(entrada);
                        if (entradaH >= 6 && entradaH < 12) return 'matutino';
                        if (entradaH >= 12 && entradaH < 18) return 'vespertino';
                        if (entradaH >= 18 || entradaH < 6) return 'noturno';
                    } catch (e) {}
                }
                return 'sobreaviso';
            }

            // PRIORIDADE 3: Detecta FINAL DE SEMANA (sem sobreaviso)
            if (turno.includes('final') || turno.includes('finais') || turno.includes('fim de semana') || turno.includes('fds')) {
                if (['matutino', 'manhã', '07:00', '08:00', '06:00'].some(x => turno.includes(x))) return 'matutino';
                if (['vespertino', 'vespertina', 'tarde', '13:00', '14:00'].some(x => turno.includes(x))) return 'vespertino';
                if (['noturno', 'noturna', 'noite', '19:00'].some(x => turno.includes(x))) return 'noturno';

                // Se não tem período explícito, detecta pelo horário
                if (horario && horario.includes('/')) {
                    try {
                        const [entrada] = horario.split('/')[0].split(':');
                        const entradaH = parseInt(entrada);
                        if (entradaH >= 6 && entradaH < 12) return 'matutino';
                        if (entradaH >= 12 && entradaH < 18) return 'vespertino';
                        if (entradaH >= 18 || entradaH < 6) return 'noturno';
                    } catch (e) {}
                }

                if (turno.includes('rotina')) return 'rotina';
                return 'outro';
            }

            // PRIORIDADE 4: Detecta turnos específicos
            // Detecta por abreviações (P1, P2, P3, P4, DIA, NOITE) + horário
            if (['p1', 'p2', 'p3', 'p4', 'dia', 'noite'].includes(turno) || (turno.length <= 3 && /^[a-z0-9]+$/.test(turno))) {
                if (horario && horario.includes('/')) {
                    try {
                        const [entrada] = horario.split('/')[0].split(':');
                        const entradaH = parseInt(entrada);
                        if (entradaH >= 6 && entradaH < 12) return 'matutino';
                        if (entradaH >= 12 && entradaH < 18) return 'vespertino';
                        if (entradaH >= 18 || entradaH < 6) return 'noturno';
                    } catch (e) {}
                }
            }

            // Matutino (Verde)
            if (['matutino', 'matutina', 'manhã', 'madrugada', '07:00', '08:00', '06:00'].some(x => turno.includes(x))) {
                return 'matutino';
            }

            // Vespertino (Laranja)
            if (['vespertino', 'vespertina', 'tarde', '13:00', '14:00'].some(x => turno.includes(x))) {
                return 'vespertino';
            }

            // Noturno (Azul)
            if (['noturno', 'noturna', 'noite', '19:00'].some(x => turno.includes(x))) {
                return 'noturno';
            }

            // Plantão (Coral)
            if (turno.includes('plantão') || turno.includes('plantao')) {
                if (turno.includes('noturno') || turno.includes('noite') || turno.includes('19:00')) return 'noturno';
                if (turno.includes('vespertino') || turno.includes('tarde') || turno.includes('13:00')) return 'vespertino';
                if (turno.includes('matutino') || turno.includes('manhã') || turno.includes('07:00')) return 'matutino';
                return 'plantao';
            }

            // PRIORIDADE 5: Detecta ROTINA com horário
            if (turno.includes('rotina')) {
                if (horario && horario.includes('/')) {
                    try {
                        const [entrada] = horario.split('/')[0].split(':');
                        const entradaH = parseInt(entrada);
                        if (entradaH >= 6 && entradaH < 12) return 'matutino';
                        if (entradaH >= 12 && entradaH < 18) return 'vespertino';
                        if (entradaH >= 18 || entradaH < 6) return 'noturno';
                    } catch (e) {}
                }
                return 'rotina';
            }

            // FALLBACK: Detecta por horário como último recurso antes de retornar 'outro'
            // Importante para turnos que não têm palavras-chave específicas (ex: Ambulatório, etc)
            if (horario && horario.includes('/')) {
                try {
                    const [entrada] = horario.split('/')[0].split(':');
                    const entradaH = parseInt(entrada);
                    if (entradaH >= 6 && entradaH < 12) return 'matutino';
                    if (entradaH >= 12 && entradaH < 18) return 'vespertino';
                    if (entradaH >= 18 || entradaH < 6) return 'noturno';
                } catch (e) {}
            }

            return 'outro';
        }

        function formatarTipoBadge(tipoBadge) {
            // Converte o tipo de turno em texto legível para a badge
            const mapping = {
                'badge-24h': '24H',
                'matutino': 'MATUTINO',
                'vespertino': 'VESPERTINO',
                'noturno': 'NOTURNO',
                'sobreaviso': 'SOBREAVISO',
                'rotina': 'ROTINA',
                'plantao': 'PLANTÃO',
                'outro': 'OUTRO'
            };
            return mapping[tipoBadge] || tipoBadge.toUpperCase();
        }

        function pluralizarProfissional(count) {
            // Retorna singular ou plural corretamente
            return count === 1 ? `${count} profissional` : `${count} profissionais`;
        }

        function selecionarDia(dia) {
            diaSelecionado = dia;
            document.querySelectorAll('.date-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelector(`[data-dia="${dia}"]`).classList.add('active');
            renderizarEscala();
            document.getElementById('search').value = '';
        }

        function renderizarEscala() {
            console.log('🔄 Dashboard v3-ramais renderizado');
            const dados = escalas[diaSelecionado];
            document.getElementById('data-selecionada').textContent = dados.data;

            // Mostrar última atualização (da data em que os dados foram gerados)
            const dataAtualizacao = escalas.data_atualizacao;
            const horaAtualizacao = escalas.hora_atualizacao;
            const statusAtualizacao = escalas.status_atualizacao;

            document.getElementById('ultima-atualizacao').textContent = `Atualizado em ${dataAtualizacao} às ${horaAtualizacao}`;

            // Mostrar indicador de status (dot colorido)
            const statusIndicator = document.getElementById('status-indicator');
            statusIndicator.className = 'update-status-indicator';

            if (statusAtualizacao === 'sucesso') {
                statusIndicator.classList.add('sucesso');
            } else if (statusAtualizacao === 'pendente') {
                statusIndicator.classList.add('pendente');
            } else {
                statusIndicator.classList.add('erro');
            }

            const porSetor = {};
            dados.registros.forEach(prof => {
                if (!porSetor[prof.setor]) {
                    porSetor[prof.setor] = [];
                }
                porSetor[prof.setor].push(prof);
            });

            const setores = Object.keys(porSetor).sort();
            let html = '';

            setores.forEach(setor => {
                const profissionais = porSetor[setor];
                const ramaisSetor = obterRamaisSetor(setor);
                const ramaisDisplay = formatarRamaisDisplay(ramaisSetor);

                if (temMultiplosTurnos(setor)) {
                    const porTurno = {};
                    const turnoOrdem = {};

                    profissionais.forEach(prof => {
                        const { ordem, nome } = normalizarTurno(prof.tipo_turno);
                        turnoOrdem[nome] = ordem;
                        if (!porTurno[nome]) {
                            porTurno[nome] = [];
                        }
                        porTurno[nome].push(prof);
                    });

                    const turnosOrdenados = Object.keys(porTurno).sort((a, b) => turnoOrdem[a] - turnoOrdem[b]);

                    html += `
                    <div class="category">
                        <div class="categoria-header expanded" onclick="toggleCategoria(this)">
                            <div class="categoria-header-text">
                                <div class="categoria-nome">${setor}${ramaisDisplay}</div>
                                <div class="categoria-count">${pluralizarProfissional(profissionais.length)}</div>
                            </div>
                            <div class="categoria-toggle">▲</div>
                        </div>
                        <div class="categoria-content">
                            <div class="turnos-container">
                                ${turnosOrdenados.map(turno => {
                                    const profs = porTurno[turno];
                                    const tipoBadge = profs.length > 0 ? obterTipoTurno(profs[0].tipo_turno, profs[0].horario) : 'outro';
                                    return `
                                    <div class="turno-coluna" data-turno-tipo="${tipoBadge}">
                                        <div class="turno-title" data-count="${profs.length}">${turno}</div>
                                        <div class="profissionais-list">
                                            ${profs.map(prof => {
                                                const profData = mapaProfissionais[prof.profissional.toLowerCase()];
                                                const telefone = profData ? profData.phone : 'N/A';
                                                const telefoneLimpo = telefone.replace(/\D/g, '');
                                                const whatsappUrl = `https://wa.me/55${telefoneLimpo}`;
                                                return `
                                                <div class="profissional" data-prof="${prof.profissional}" data-setor="${setor}" data-turno="${turno}" data-tipo="${prof.tipo_turno}" data-hora="${prof.horario}" data-search="${prof.profissional.toLowerCase()} ${setor.toLowerCase()} ${turno.toLowerCase()}">
                                                    <div class="profissional-nome">
                                                        ${telefone !== 'N/A' ? `<a href="${whatsappUrl}" target="_blank" class="telefone-tooltip" title="Clique para enviar WhatsApp"><span class="telefone-icon"></span>${telefone}</a>` : ''}
                                                        <div class="profissional-nome-wrapper">
                                                            <span class="profissional-nome-text">${prof.profissional}</span>
                                                        </div>
                                                    </div>
                                                    <div class="profissional-info">
                                                        <span class="info-label">Horário:</span> ${prof.horario}
                                                        <span class="turno-badge ${obterTipoTurno(prof.tipo_turno, prof.horario)}" title="${prof.tipo_turno}">${formatarTipoBadge(obterTipoTurno(prof.tipo_turno, prof.horario))}</span>
                                                    </div>
                                                </div>
                                            `}).join('')}
                                        </div>
                                    </div>
                                    `;
                                }).join('')}
                            </div>
                        </div>
                    </div>
                    `;
                } else {
                    html += `
                    <div class="category">
                        <div class="categoria-header expanded" onclick="toggleCategoria(this)">
                            <div class="categoria-header-text">
                                <div class="categoria-nome">${setor}${ramaisDisplay}</div>
                                <div class="categoria-count">${pluralizarProfissional(profissionais.length)}</div>
                            </div>
                            <div class="categoria-toggle">▲</div>
                        </div>
                        <div class="categoria-content">
                            <div class="profissionais-list">
                                ${profissionais.map(prof => {
                                    const profData = mapaProfissionais[prof.profissional.toLowerCase()];
                                    const telefone = profData ? profData.phone : 'N/A';
                                    const telefoneLimpo = telefone.replace(/\D/g, '');
                                    const whatsappUrl = `https://wa.me/55${telefoneLimpo}`;
                                    return `
                                    <div class="profissional" data-prof="${prof.profissional}" data-setor="${setor}" data-turno="${prof.tipo_turno}" data-tipo="${prof.tipo_turno}" data-hora="${prof.horario}" data-search="${prof.profissional.toLowerCase()} ${setor.toLowerCase()}">
                                        <div class="profissional-nome">
                                            ${telefone !== 'N/A' ? `<a href="${whatsappUrl}" target="_blank" class="telefone-tooltip" title="Clique para enviar WhatsApp"><span class="telefone-icon"></span>${telefone}</a>` : ''}
                                            <div class="profissional-nome-wrapper">
                                                <span class="profissional-nome-text">${prof.profissional}</span>
                                            </div>
                                        </div>
                                        <div class="profissional-info">
                                            <span class="info-label">Turno:</span> ${prof.tipo_turno}
                                            <span class="turno-badge ${obterTipoTurno(prof.tipo_turno, prof.horario)}" title="${prof.tipo_turno}">${formatarTipoBadge(obterTipoTurno(prof.tipo_turno, prof.horario))}</span><br>
                                            <span class="info-label">Horário:</span> ${prof.horario}
                                        </div>
                                    </div>
                                `}).join('')}
                            </div>
                        </div>
                    </div>
                    `;
                }
            });

            document.getElementById('categorias').innerHTML = html;

            // Populate data-search attributes from individual data attributes
            // This ensures search works with rendered elements
            console.log('Populando data-search...');
            let attrCount = 0;
            document.querySelectorAll('.profissional').forEach(prof => {
                const prof_val = prof.getAttribute('data-prof') || '';
                const setor_val = prof.getAttribute('data-setor') || '';

                if (attrCount < 3) {
                    console.log(`Prof ${attrCount}: prof="${prof_val}" setor="${setor_val}"`);
                }

                const searchText = [prof_val, setor_val]
                    .join(' ').toLowerCase();
                prof.setAttribute('data-search', searchText);
                attrCount++;
            });
            console.log(`Total profissionais processados: ${attrCount}`);

            const totalSetores = Object.keys(porSetor).length;
            document.getElementById('stats').innerHTML = `
                <div class="stat-card">
                    <div class="stat-number">${dados.total}</div>
                    <div class="stat-label">Profissionais</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">${totalSetores}</div>
                    <div class="stat-label">Setores</div>
                </div>
            `;
        }

        function toggleCategoria(header) {
            header.classList.toggle('expanded');
            const content = header.nextElementSibling;
            content.classList.toggle('collapsed');
        }

        let seccoesExpandidas = true;

        function alternarSeccoes() {
            const btn = document.getElementById('toggle-btn');
            const categorias = document.querySelectorAll('.categoria-header');

            if (seccoesExpandidas) {
                // Colapsar todas
                categorias.forEach(h => {
                    h.classList.remove('expanded');
                    h.nextElementSibling.classList.add('collapsed');
                });
                btn.innerHTML = 'Expandir';
                btn.classList.add('collapsed');
                seccoesExpandidas = false;
            } else {
                // Expandir todas
                categorias.forEach(h => {
                    h.classList.add('expanded');
                    h.nextElementSibling.classList.remove('collapsed');
                });
                btn.innerHTML = 'Minimizar';
                btn.classList.remove('collapsed');
                seccoesExpandidas = true;
            }
        }

        // Mostrar data atual no header
        const hoje = new Date();
        const diasSemana = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];
        const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
        const dataFormatada = `${diasSemana[hoje.getDay()]}, ${hoje.getDate()} ${meses[hoje.getMonth()]} ${hoje.getFullYear()}`;
        document.getElementById('data-atual-header').textContent = dataFormatada;

        // Dados de autenticação
        const profissionaisData = PROFISSIONAIS_JSON;

        // Criar mapa de profissionais por nome para acessar telefones
        const mapaProfissionais = {};
        profissionaisData.professionals.forEach(prof => {
            mapaProfissionais[prof.name.toLowerCase()] = prof;
        });

        // Autenticar como Profissional
        function autenticarProfissional() {
          const input = document.getElementById('auth-input-prof').value.toLowerCase().trim();
          const errorMsg = document.getElementById('auth-error-prof');

          if (!input) {
            errorMsg.textContent = 'Digite seu email ou telefone';
            errorMsg.classList.add('show');
            return;
          }

          // Procura na lista de profissionais
          const encontrado = profissionaisData.professionals.some(prof => {
            return prof.email.toLowerCase() === input || prof.last4 === input;
          });

          if (encontrado) {
            // Salva autenticação na sessão
            sessionStorage.setItem('authenticated', 'true');
            // Esconde o modal e remove blur
            document.getElementById('auth-modal').classList.add('hidden');
            document.getElementById('main-content').classList.remove('blurred');
            errorMsg.classList.remove('show');
          } else {
            errorMsg.textContent = 'Email ou telefone não encontrado';
            errorMsg.classList.add('show');
            document.getElementById('auth-input-prof').value = '';
          }
        }

        // Autenticar como Outro Usuário
        function autenticarOutro() {
          const senha = document.getElementById('auth-input-outro').value.trim();
          const errorMsg = document.getElementById('auth-error-outro');
          const senhaCorreta = 'HRO-ALVF';

          if (!senha) {
            errorMsg.textContent = 'Digite a senha';
            errorMsg.classList.add('show');
            return;
          }

          if (senha === senhaCorreta) {
            // Salva autenticação na sessão
            sessionStorage.setItem('authenticated', 'true');
            // Esconde o modal e remove blur
            document.getElementById('auth-modal').classList.add('hidden');
            document.getElementById('main-content').classList.remove('blurred');
            errorMsg.classList.remove('show');
          } else {
            errorMsg.textContent = 'Senha incorreta';
            errorMsg.classList.add('show');
            document.getElementById('auth-input-outro').value = '';
          }
        }

        // Verifica autenticação ao carregar
        function verificarAutenticacao() {
          if (!sessionStorage.getItem('authenticated')) {
            document.getElementById('auth-modal').classList.remove('hidden');
            document.getElementById('main-content').classList.add('blurred');
          } else {
            document.getElementById('auth-modal').classList.add('hidden');
            document.getElementById('main-content').classList.remove('blurred');
          }
        }

        // Funções para o modal de contatos
        function abrirListaContatos() {
          const modal = document.getElementById('contacts-modal');
          modal.classList.add('active');
          renderizarContatos();
        }

        function fecharListaContatos() {
          const modal = document.getElementById('contacts-modal');
          modal.classList.remove('active');
        }

        function renderizarContatos() {
          const contactsList = document.getElementById('contacts-list');
          const profissionais = [...profissionaisData.professionals].sort((a, b) =>
            a.name.localeCompare(b.name, 'pt-BR')
          );

          contactsList.innerHTML = profissionais.map(prof => {
            const telefoneLimpo = prof.phone.replace(/\D/g, '');
            const whatsappUrl = `https://wa.me/55${telefoneLimpo}`;
            return `
              <div class="contact-item">
                <div class="contact-name">${prof.name}</div>
                <div class="contact-info">
                  <a href="${whatsappUrl}" target="_blank" class="contact-phone">
                    ${prof.phone}
                  </a>
                </div>
              </div>
            `;
          }).join('');
        }

        function filtrarContatos() {
          const searchText = document.getElementById('contacts-search').value.toLowerCase();
          const contactItems = document.querySelectorAll('.contact-item');

          contactItems.forEach(item => {
            const nome = item.querySelector('.contact-name').textContent.toLowerCase();
            const telefone = item.querySelector('.contact-info').textContent.toLowerCase();

            if (nome.includes(searchText) || telefone.includes(searchText)) {
              item.style.display = 'block';
            } else {
              item.style.display = 'none';
            }
          });
        }

        // Fechar modal ao clicar fora
        document.getElementById('contacts-modal').addEventListener('click', function(e) {
          if (e.target === this) {
            fecharListaContatos();
          }
        });

        // Verifica antes de renderizar
        verificarAutenticacao();
        renderizarEscala();
    </script>
    </div> <!-- Fecha main-content -->
</body>
</html>"""

    # Substituir placeholder de profissionais com dados reais
    profissionais_json_str = json.dumps(profissionais_data)
    html = html.replace('PROFISSIONAIS_JSON', profissionais_json_str)

    # Salvar arquivo
    output_file = '/tmp/dashboard_executivo.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Dashboard executivo criado!")
    print(f"📍 Arquivo: {output_file}")
    if ramais_data and mapping_data:
        print(f"📞 Funcionalidade de ramais integrada com sucesso!")

if __name__ == '__main__':
    gerar_dashboard()
