#!/usr/bin/env python3
"""
Dashboard Executivo - Visual Premium
Com banner ALVF e design sofisticado

MELHORIAS V2:
- Abas de navegação para 3 dias (anterior/atual/próxima)
- Badges coloridas para tipos de turno
- Indicadores visuais melhorados
- Melhor usabilidade e leitura
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

def gerar_dashboard():
    """Gera dashboard executivo com visual premium"""

    # Procurar pelos arquivos em múltiplos locais
    import os
    from pathlib import Path

    # Procurar arquivo de escalas
    escala_paths = [
        '/tmp/escalas_multiplos_dias.json',
        'escalas_multiplos_dias.json',
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

    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
            background: #0a2c4d;
            box-shadow: 0 4px 12px rgba(13, 59, 102, 0.2);
        }

        .auth-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            border-bottom: 2px solid #e8eef7;
        }

        .auth-tab-btn {
            background: none;
            border: none;
            padding: 12px 20px;
            font-size: 1em;
            font-weight: 600;
            color: #999;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
            margin-bottom: -2px;
        }

        .auth-tab-btn.active {
            color: #0d3b66;
            border-bottom-color: #0d3b66;
        }

        .auth-tab-btn:hover {
            color: #0d3b66;
        }

        .auth-tab-content {
            display: none;
        }

        .auth-tab-content.active {
            display: block;
        }

        .auth-error {
            color: #e63946;
            margin-top: 15px;
            font-size: 0.9em;
            display: none;
        }

        .auth-error.show {
            display: block;
        }

        /* Header com banner */
        .header-banner {
            background: linear-gradient(135deg, #0d3b66 0%, #1a5f8f 100%);
            padding: 30px 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            transition: box-shadow 1.8s ease-out, background 2s ease-out;
        }

        .header-banner:hover {
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
            background: linear-gradient(135deg, #1a5f8f 0%, #0d3b66 100%);
        }

        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 40px;
            flex-wrap: wrap;
            padding: 0 20px;
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 16px;
            flex: 1;
            min-width: 250px;
        }

        .header-right {
            display: flex;
            align-items: center;
            gap: 16px;
            text-align: right;
            flex: 1;
            min-width: 250px;
            justify-content: flex-end;
        }

        .header-logo {
            font-family: 'Merriweather', serif;
            color: white;
            font-size: 2em;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        .header-separator {
            color: white;
            font-size: 1.8em;
            opacity: 0.6;
            margin: 0 12px;
        }

        .header-title {
            font-family: 'Merriweather', serif;
            color: white;
            font-size: 1.5em;
            font-weight: 700;
            margin: 0;
            letter-spacing: 0.5px;
        }

        .header-description {
            color: white;
            font-size: 0.85em;
            opacity: 0.95;
            text-align: right;
        }

        .header-description p {
            margin: 0;
            line-height: 1.3;
            letter-spacing: 0.3px;
        }

        /* Container Principal */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        /* Controles */
        .controls-bar {
            background: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            display: flex;
            gap: 20px;
            align-items: center;
            flex-wrap: wrap;
        }

        .date-selector {
            display: flex;
            gap: 12px;
            align-items: center;
        }

        .date-btn {
            padding: 10px 20px;
            border: 2px solid #e0e0e0;
            background: white;
            color: #0d3b66;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.95em;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .date-btn:hover {
            border-color: #0d3b66;
            background: #f0f5fa;
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
            padding: 12px 18px;
            border: 2px solid #e0e0e0;
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
            font-weight: 600;
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
        }

        .btn-primary {
            background: #0d3b66;
            color: white;
        }

        .btn-primary:hover {
            background: #0a2c4d;
            box-shadow: 0 4px 12px rgba(13, 59, 102, 0.2);
        }

        .btn-secondary {
            background: #e8eef7;
            color: #0d3b66;
        }

        .btn-secondary:hover {
            background: #d8e2f0;
        }

        .btn-contacts {
            background: #1a5f8f;
            color: white;
        }

        .btn-contacts:hover {
            background: #0d3b66;
        }

        .btn-print {
            background: #1a5f8f;
            color: white;
        }

        .btn-print:hover {
            background: #0d3b66;
        }

        .btn-toggle-sections {
            background: #f0f5fa;
            color: #0d3b66;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }

        .btn-toggle-sections:hover {
            background: #e0e8f5;
        }

        .btn-toggle-sections.collapsed {
            background: #e0e8f5;
        }

        /* Triângulo dinâmico nos botões - usando mesmo do categoria-toggle */
        .btn-toggle-sections::before {
            content: '';
            color: #0d3b66;
            font-size: 1.2em;
            transition: transform 0.3s ease;
            display: inline-block;
            width: 0;
            height: 0;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-bottom: 10px solid #0d3b66;
            margin-right: 8px;
        }

        .btn-toggle-sections.collapsed::before {
            transform: rotate(180deg);
        }

        .date-btn {
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        /* Triângulo para botão anterior (apontando para esquerda) */
        .date-btn[data-dia="anterior"]::before {
            content: '';
            color: #0d3b66;
            font-size: 1.2em;
            transition: transform 0.3s ease;
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
            transition: border-color 0.3s ease;
        }

        .contacts-search:focus {
            outline: none;
            border-color: #0d3b66;
        }

        .contacts-warning {
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 6px;
            padding: 12px 15px;
            margin-bottom: 15px;
            font-size: 0.95em;
            color: #856404;
        }

        .contacts-warning p {
            margin: 0;
            line-height: 1.5;
        }

        .contacts-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .contact-item {
            background: #f8f9fb;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #0d3b66;
            transition: all 0.3s ease;
        }

        .contact-item:hover {
            background: #e8eef7;
            transform: translateX(4px);
        }

        .contact-name {
            font-weight: 700;
            color: #1a1a1a;
            font-size: 0.95em;
            margin-bottom: 8px;
        }

        .contact-info {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 0.85em;
            color: #666;
            margin-top: 6px;
        }

        .contact-email {
            color: #666;
        }

        .contact-separator {
            color: #ccc;
            font-weight: 300;
        }

        .contact-phone {
            color: #0d3b66;
            text-decoration: none;
            font-weight: 600;
            cursor: pointer;
            transition: color 0.2s ease;
        }

        .contact-phone:hover {
            color: #1a5f8f;
        }

        /* Estatísticas */
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
            opacity: 0.85;
        }

        .stat-card {
            background: white;
            padding: 18px;
            border-radius: 12px;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
            border-left: 3px solid #0d3b66;
            text-align: center;
        }

        .stat-number {
            font-size: 2.2em;
            font-weight: 700;
            color: #0d3b66;
            margin-bottom: 6px;
        }

        .stat-label {
            font-size: 0.9em;
            color: #666;
            font-weight: 500;
            letter-spacing: 0.5px;
        }

        /* Data Display */
        .date-display {
            text-align: center;
            font-size: 1.2em;
            color: #0d3b66;
            font-weight: 600;
            margin-bottom: 25px;
            letter-spacing: 0.5px;
        }

        /* Última atualização */
        .last-update {
            text-align: right;
            font-size: 0.85em;
            color: #999;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 8px;
            font-style: italic;
        }

        .update-status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            min-width: 12px;
            min-height: 12px;
            border-radius: 50%;
            margin-left: 8px;
            cursor: pointer;
            transition: transform 0.2s ease;
            vertical-align: middle;
            background: #ccc;
            box-shadow: 0 0 4px rgba(0,0,0,0.2);
        }

        .update-status-indicator:hover {
            transform: scale(1.3);
        }

        .update-status-indicator.sucesso {
            background: #4caf50 !important;
            box-shadow: 0 0 8px rgba(76, 175, 80, 0.6) !important;
        }

        .update-status-indicator.erro {
            background: #f44336 !important;
            box-shadow: 0 0 8px rgba(244, 67, 54, 0.6) !important;
            animation: pulse-error 1.5s infinite;
        }

        .update-status-indicator.aviso {
            background: #ff9800 !important;
            box-shadow: 0 0 8px rgba(255, 152, 0, 0.6) !important;
        }

        @keyframes pulse-error {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }

        /* Descrição do Dashboard */
        .dashboard-description {
            background: #f0f5fa;
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 25px;
            font-size: 0.95em;
            color: #333;
            line-height: 1.6;
        }

        .dashboard-description p {
            margin: 0;
            color: #333;
        }

        .dashboard-description strong {
            color: #0d3b66;
            font-weight: 700;
        }

        /* Categoria */
        .category {
            background: white;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .category:hover {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        }

        .categoria-header {
            padding: 20px 25px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
            user-select: none;
            border-left: 4px solid #0d3b66;
            background: linear-gradient(90deg, #f8fbff 0%, white 100%);
            transition: all 0.3s ease;
        }

        .categoria-header:hover {
            background: linear-gradient(90deg, #f0f5fa 0%, #f8fbff 100%);
        }

        .categoria-header.expanded {
            background: linear-gradient(90deg, #e8eef7 0%, #f0f5fa 100%);
        }

        .categoria-header-text {
            display: flex;
            flex-direction: column;
            text-align: left;
        }

        .categoria-nome {
            color: #0d3b66;
            font-size: 1.1em;
            margin-bottom: 3px;
        }

        .categoria-count {
            color: #999;
            font-size: 0.85em;
            font-weight: 500;
        }

        .categoria-toggle {
            color: #0d3b66;
            font-size: 1.2em;
            transition: transform 0.3s ease;
            display: inline-block;
            transform: rotate(180deg);
        }

        .categoria-header.expanded .categoria-toggle {
            transform: rotate(0deg);
        }

        .categoria-content {
            padding: 20px;
            transition: max-height 0.3s ease;
        }

        .categoria-content.collapsed {
            display: none;
        }

        /* Layout de colunas para turnos */
        .turnos-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 20px;
        }

        .turno-coluna {
            background: #ffffff;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
        }

        .turno-coluna:hover {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
            transform: translateX(4px);
        }

        .turno-title {
            font-weight: 700;
            color: #0d3b66;
            margin-bottom: 10px;
            font-size: 0.95em;
            letter-spacing: 0.3px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .turno-title::before {
            content: attr(data-count);
            font-size: 0.85em;
            background: #e8eef7;
            color: #0d3b66;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: 600;
        }

        .profissionais-list {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .profissional {
            background: white;
            padding: 14px;
            border-radius: 8px;
            border-left: 3px solid #0d3b66;
            transition: all 0.3s ease;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            position: relative;
        }

        .profissional:hover {
            transform: translateX(3px);
            box-shadow: 0 4px 10px rgba(13, 59, 102, 0.1);
        }

        .profissional-nome {
            font-weight: 700;
            margin-bottom: 6px;
            color: #1a1a1a;
            font-size: 0.95em;
            display: inline-block;
            position: relative;
        }

        .profissional-nome-wrapper {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .profissional-nome-text {
            cursor: pointer;
        }

        .whatsapp-icon {
            display: none;
        }

        .profissional-nome:hover .whatsapp-icon {
            display: block;
        }

        .telefone-tooltip {
            position: absolute;
            background: #0d3b66;
            color: white;
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 0.8em;
            font-weight: 600;
            white-space: nowrap;
            pointer-events: auto;
            cursor: pointer;
            z-index: 1000;
            bottom: 100%;
            left: 0;
            margin-bottom: 0;
            padding-bottom: 15px;
            opacity: 0;
            transition: opacity 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 2px 8px rgba(13, 59, 102, 0.2);
            user-select: none;
            text-decoration: none;
        }

        .telefone-tooltip:hover {
            transform: scale(1.05);
            box-shadow: 0 0 12px rgba(13, 59, 102, 0.5), 0 2px 8px rgba(13, 59, 102, 0.2);
            filter: drop-shadow(0 0 6px rgba(13, 59, 102, 0.4));
        }

        .profissional-nome:hover .telefone-tooltip,
        .telefone-tooltip:hover {
            opacity: 1;
        }

        .telefone-tooltip::after {
            content: '';
            position: absolute;
            bottom: -5px;
            left: 14px;
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #0d3b66;
        }

        .telefone-icon {
            display: inline-block;
            width: 16px;
            height: 16px;
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>') no-repeat center / contain;
        }

        .profissional-info {
            font-size: 0.85em;
            color: #666;
            line-height: 1.6;
        }

        .info-label {
            font-weight: 600;
            color: #0d3b66;
            display: inline;
        }

        /* ===== BADGES DE TURNO ===== */
        .turno-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.75em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            margin-left: 6px;
            vertical-align: middle;
        }

        .turno-badge.matutino {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .turno-badge.vespertino {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }

        .turno-badge.noturno {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }

        .turno-badge.plantao {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .turno-badge.outro {
            background: #e2e3e5;
            color: #383d41;
            border: 1px solid #d6d8db;
        }

        .turno-badge.badge-24h {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            font-weight: 800;
        }

        .turno-badge.diurno {
            background: linear-gradient(135deg, #ffe0b2 0%, #ffd699 100%);
            color: #e65100;
            border: 1px solid #ffb74d;
            font-weight: 600;
        }

        .turno-badge.sobreaviso {
            background: linear-gradient(135deg, #ff8fab 0%, #ff6b7a 100%);
            color: #ffffff;
            border: 1px solid #f72585;
            font-weight: 600;
        }

        .turno-badge.rotina {
            background: linear-gradient(135deg, #b5a7f5 0%, #8e7cc3 100%);
            color: #ffffff;
            border: 1px solid #6c5bb0;
        }

        /* ===== ABAS DE DATA ===== */
        .data-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            border-bottom: 2px solid #e0e0e0;
            overflow-x: auto;
            padding-bottom: 0;
        }

        .data-tab {
            padding: 14px 20px;
            border: none;
            background: none;
            cursor: pointer;
            font-weight: 600;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
            font-size: 0.95em;
            white-space: nowrap;
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
            .contacts-modal {
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

            <!-- Aba Profissional -->
            <div id="auth-tab-profissional" class="auth-tab-content active">
                <p>Digite seu email ou os últimos 4 dígitos do seu telefone:</p>
                <input type="text" id="auth-input-prof" placeholder="Email ou últimos 4 dígitos" class="auth-input" onkeypress="if(event.key === 'Enter') autenticarProfissional()">
                <button onclick="autenticarProfissional()" class="auth-btn">Acessar</button>
                <p id="auth-error-prof" class="auth-error"></p>
            </div>

            <!-- Aba Outro Usuário -->
            <div id="auth-tab-outro" class="auth-tab-content">
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

    <!-- Main content wrapper for blur effect -->
    <div id="main-content">
    <!-- Header com Banner -->
    <div class="header-banner">
        <div class="header-content">
            <div class="header-left">
                <div class="header-logo">HRO</div>
                <div class="header-separator">|</div>
                <h2 class="header-title">Escala Médica</h2>
            </div>
            <div class="header-right">
                <div class="header-logo">ALVF</div>
                <div class="header-description">
                    <p>Associação Hospitalar<br>Lenoir Vargas Ferreira</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Container Principal -->
    <div class="container">
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
            </div>
        </div>

        <!-- Data selecionada -->
        <div class="date-display" id="data-selecionada"></div>

        <!-- Última atualização -->
        <div class="last-update">
            <div id="ultima-atualizacao"></div>
            <div class="update-status-indicator" id="status-indicator" title="Status da última atualização automática"></div>
        </div>

        <!-- Descrição do Dashboard -->
        <div class="dashboard-description">
            <p><strong>Dashboard para visualização da escala médica do HRO.</strong> Atualizações diárias com manutenção do registro do dia anterior para consultas. Use as ferramentas de busca, filtros e expansão/colapso para navegar facilmente pelos profissionais e turnos. Passe o mouse sobre o nome de qualquer profissional para ver seu telefone e iniciar uma conversa via WhatsApp.</p>
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
            'ginecologia', 'obstet', 'hospitalista', 'pronto', 'urgência',
            'plantão', 'clínica', 'comanejo', 'ucin', 'cuidados', 'uti', 'residência'
        ];

        // Função para normalizar turnos
        function normalizarTurno(turnoText, horarioText = '') {
            if (!turnoText) return { ordem: 99, nome: 'Outro' };

            const turno = turnoText.toLowerCase().trim();
            const turnoOriginal = turnoText.trim();
            const horario = horarioText ? horarioText.toLowerCase() : '';

            // Se o turno for genérico (tipo "Res. Clínica Médica") e temos horário, detectar pelo horário
            if (turno.includes('res.') || turno.includes('residência') || turno.includes('residencia')) {
                if (horario && horario.includes('/')) {
                    try {
                        const [entrada, saida] = horario.split('/');
                        const entradaH = parseInt(entrada.split(':')[0]);
                        const saidaH = parseInt(saida.split(':')[0]);
                        // Detectar diurno (07:00-19:00) - entrada 07, saída 19
                        if (entradaH === 7 && saidaH === 19) {
                            return { ordem: 1, nome: 'Plantão Diurno' };
                        }
                        // Detectar por hora de entrada
                        if (entradaH >= 6 && entradaH < 12) return { ordem: 1, nome: 'Plantão Matutino' };
                        if (entradaH >= 12 && entradaH < 18) return { ordem: 2, nome: 'Plantão Vespertino' };
                        if (entradaH >= 18 || entradaH < 6) return { ordem: 3, nome: 'Plantão Noturno' };
                    } catch (e) {}
                }
                // Fallback: retorna como genérico
                return { ordem: 1, nome: turnoOriginal };
            }

            // HOSPITALISTA - COMANEJO vs URGÊNCIA
            if (turno.includes('hospitalista')) {
                if (turno.includes('comanejo')) {
                    if (turno.includes('matutino') || turno.includes('07:00')) return { ordem: 1, nome: 'Comanejo Matutino' };
                    if (turno.includes('vespertino') || turno.includes('tarde') || turno.includes('13:00')) return { ordem: 2, nome: 'Comanejo Vespertino' };
                    if (turno.includes('noturno') || turno.includes('19:00')) return { ordem: 3, nome: 'Comanejo Noturno' };
                } else if (turno.includes('urgência') || turno.includes('urgencia')) {
                    if (turno.includes('matutino') || turno.includes('07:00')) return { ordem: 1, nome: 'Urgência Matutino' };
                    if (turno.includes('vespertino') || turno.includes('tarde') || turno.includes('13:00')) return { ordem: 2, nome: 'Urgência Vespertino' };
                    if (turno.includes('noturno') || turno.includes('19:00')) return { ordem: 3, nome: 'Urgência Noturno' };
                }
            }

            // MATUTINO
            if (['matutino', 'matutina', 'manhã', 'madrugada'].some(x => turno.includes(x)) || ['07:00', '08:00', '06:00'].some(x => turno.includes(x))) {
                if (turno.includes('final')) return { ordem: 1, nome: 'Manhã - Final de Semana' };
                if (turno.includes('p1')) return { ordem: 1, nome: 'Plantão Matutino - P1' };
                if (turno.includes('p2')) return { ordem: 1, nome: 'Plantão Matutino - P2' };
                return { ordem: 1, nome: 'Plantão Matutino' };
            }

            // VESPERTINO
            if (['vespertino', 'vespertina', 'tarde'].some(x => turno.includes(x)) || ['13:00', '14:00'].some(x => turno.includes(x))) {
                if (turno.includes('final')) return { ordem: 2, nome: 'Tarde - Final de Semana' };
                if (turno.includes('p1')) return { ordem: 2, nome: 'Plantão Vespertino - P1' };
                if (turno.includes('p2')) return { ordem: 2, nome: 'Plantão Vespertino - P2' };
                return { ordem: 2, nome: 'Plantão Vespertino' };
            }

            // NOTURNO
            if (['noturno', 'noturna', 'noite'].some(x => turno.includes(x)) || turno.includes('19:00')) {
                if (turno.includes('p1')) return { ordem: 3, nome: 'Plantão Noturno - P1' };
                if (turno.includes('p2')) return { ordem: 3, nome: 'Plantão Noturno - P2' };
                return { ordem: 3, nome: 'Plantão Noturno' };
            }

            // DIURNO (07:00-19:00)
            if (turno === 'diurno') return { ordem: 1, nome: 'Plantão Diurno' };

            // DIA / NOITE (legacy)
            if (turno === 'dia') return { ordem: 1, nome: 'Plantão Diurno' };
            if (turno === 'noite') return { ordem: 3, nome: 'Período Noturno' };

            // P1, P2, P3, P4
            if (['p1', 'p2', 'p3', 'p4'].includes(turno)) return { ordem: 2, nome: 'Plantão ' + turno.toUpperCase() };

            // ROTINA
            if (['rotina', 'regular', 'alojamento'].some(x => turno.includes(x))) {
                if (turno.includes('matutino')) return { ordem: 1, nome: 'Rotina Matutino' };
                if (turno.includes('vespertino') || turno.includes('tarde')) return { ordem: 2, nome: 'Rotina Vespertino' };
                if (turno.includes('noturno') || turno.includes('noite')) return { ordem: 3, nome: 'Rotina Noturno' };
                if (turno.includes('final')) return { ordem: 4, nome: 'Rotina - Final de Semana' };
                return { ordem: 4, nome: 'Rotina' };
            }

            // SOBREAVISO
            if (turno.includes('sobreaviso')) {
                if (turno.includes('cardiologia')) return { ordem: 5, nome: 'Sobreaviso Cardiologia' };
                if (turno.includes('urologia')) return { ordem: 5, nome: 'Sobreaviso Urologia' };
                if (turno.includes('cirurgia')) {
                    if (turno.includes('equipe 1') || turno.includes(' 1')) return { ordem: 5, nome: 'Sobreaviso Cirurgia - Equipe 1' };
                    if (turno.includes('equipe 2') || turno.includes(' 2')) return { ordem: 5, nome: 'Sobreaviso Cirurgia - Equipe 2' };
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
                statusIndicator.title = 'Atualização bem-sucedida';
            } else {
                statusIndicator.classList.add('erro');
                const erro = escalas.mensagem_erro || 'Erro desconhecido';
                statusIndicator.title = `Erro na atualização: ${erro}`;
            }

            const porSetor = {};
            dados.registros.forEach(reg => {
                if (!porSetor[reg.setor]) porSetor[reg.setor] = [];
                porSetor[reg.setor].push(reg);
            });

            let html = '';
            Object.keys(porSetor).sort().forEach(setor => {
                const profissionais = porSetor[setor];

                if (temMultiplosTurnos(setor)) {
                    const porTurno = {};
                    const turnoOrdem = {};

                    profissionais.forEach(prof => {
                        const turnoOriginal = prof.tipo_turno || 'Outro';
                        const { ordem, nome } = normalizarTurno(turnoOriginal, prof.horario);

                        if (!porTurno[nome]) {
                            porTurno[nome] = [];
                            turnoOrdem[nome] = ordem;
                        }
                        porTurno[nome].push(prof);
                    });

                    const turnosOrdenados = Object.keys(porTurno).sort((a, b) => turnoOrdem[a] - turnoOrdem[b]);

                    html += `
                    <div class="category">
                        <div class="categoria-header expanded" onclick="toggleCategoria(this)">
                            <div class="categoria-header-text">
                                <div class="categoria-nome">${setor}</div>
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
                                                <div class="profissional" data-search="${prof.profissional.toLowerCase()} ${setor.toLowerCase()} ${turno.toLowerCase()} ${prof.tipo_turno.toLowerCase()} ${prof.horario.toLowerCase()}">
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
                                <div class="categoria-nome">${setor}</div>
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
                                    <div class="profissional" data-search="${prof.profissional.toLowerCase()} ${setor.toLowerCase()} ${prof.tipo_turno.toLowerCase()} ${prof.horario.toLowerCase()}">
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

        function filtrarProfissionais() {
            const searchText = document.getElementById('search').value.toLowerCase();
            const profissionais = document.querySelectorAll('.profissional');
            let totalVistos = 0;

            profissionais.forEach(prof => {
                const texto = prof.getAttribute('data-search');
                if (searchText === '' || texto.includes(searchText)) {
                    prof.style.display = 'block';
                    totalVistos++;
                } else {
                    prof.style.display = 'none';
                }
            });

            // Ocultar turno-coluna vazia (sem profissionais vistos)
            document.querySelectorAll('.turno-coluna').forEach(turnoColuna => {
                const vistosTurno = turnoColuna.querySelectorAll('.profissional[style*="display: block"]').length;
                if (searchText === '') {
                    turnoColuna.style.display = 'block';
                } else {
                    turnoColuna.style.display = vistosTurno > 0 ? 'block' : 'none';
                }
            });

            document.querySelectorAll('.category').forEach(category => {
                const content = category.querySelector('.categoria-content');
                const header = category.querySelector('.categoria-header');
                const colunas = content.querySelectorAll('.turno-coluna[style*="display: block"]').length;

                if (searchText === '') {
                    category.style.display = 'block';
                } else {
                    if (colunas > 0) {
                        category.style.display = 'block';
                        content.classList.remove('collapsed');
                        header.classList.add('expanded');
                    } else {
                        category.style.display = 'none';
                    }
                }
            });

            // Mostrar mensagem se não encontrar nada
            let emptyMessageDiv = document.getElementById('empty-search-message');
            if (!emptyMessageDiv) {
                emptyMessageDiv = document.createElement('div');
                emptyMessageDiv.id = 'empty-search-message';
                emptyMessageDiv.style.cssText = 'text-align: center; padding: 40px 20px; color: #999; font-size: 1em; margin-top: 20px;';
                document.getElementById('categorias').parentNode.insertBefore(emptyMessageDiv, document.getElementById('categorias'));
            }

            if (searchText !== '' && totalVistos === 0) {
                emptyMessageDiv.textContent = `Nenhum resultado encontrado para "${searchText}"`;
                emptyMessageDiv.style.display = 'block';
            } else {
                emptyMessageDiv.style.display = 'none';
            }
        }

        // Dados de autenticação
        const profissionaisData = PROFISSIONAIS_JSON;

        // Criar mapa de profissionais por nome para acessar telefones
        const mapaProfissionais = {};
        profissionaisData.professionals.forEach(prof => {
            mapaProfissionais[prof.name.toLowerCase()] = prof;
        });

        // Função de autenticação
        // Trocar entre abas
        function trocarAbaAuth(aba) {
          // Esconder todas as abas
          document.getElementById('auth-tab-profissional').classList.remove('active');
          document.getElementById('auth-tab-outro').classList.remove('active');

          // Remover classe active de todos os botões
          document.querySelectorAll('.auth-tab-btn').forEach(btn => {
            btn.classList.remove('active');
          });

          // Mostrar aba selecionada
          if (aba === 'profissional') {
            document.getElementById('auth-tab-profissional').classList.add('active');
            document.querySelectorAll('.auth-tab-btn')[0].classList.add('active');
          } else {
            document.getElementById('auth-tab-outro').classList.add('active');
            document.querySelectorAll('.auth-tab-btn')[1].classList.add('active');
          }
        }

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

if __name__ == '__main__':
    gerar_dashboard()
