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

from dashboard_logic import (
    obter_tipo_turno,
    normalizar_turno,
    carregar_ramais_data,
    obter_ramais_setor,
    formatar_ramais_display,
)

def gerar_dashboard():
    """Gera dashboard executivo com visual premium"""

    # Procurar pelos arquivos em múltiplos locais
    import os
    from pathlib import Path

    # Procurar arquivo de escalas
    # Prioritize extracao_inteligente.json (direct output from extraction)
    # Fallback to escalas_multiplos_dias.json for backward compatibility
    base_dir = Path(__file__).parent
    escala_paths = [
        '/tmp/extracao_inteligente.json',  # Primary: fresh from extraction
        '/tmp/escalas_multiplos_dias.json',  # Fallback: legacy intermediate file
        base_dir / 'extracao_inteligente.json',
        base_dir / 'escalas_multiplos_dias.json',
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

    # Fix common typos in the source data
    import json as json_lib
    escalas_str = json_lib.dumps(escalas)
    escalas_str = escalas_str.replace('Méidica', 'Médica')
    escalas = json_lib.loads(escalas_str)

    # Garante que 'anterior' e 'seguinte' existam (algumas fontes de fallback
    # só trazem 'atual'); evita erro no dashboard ao trocar de dia.
    for _dia in ('anterior', 'seguinte'):
        if not isinstance(escalas.get(_dia), dict) or 'registros' not in (escalas.get(_dia) or {}):
            escalas[_dia] = {'data': 'N/A', 'data_simples': '00/00/0000', 'registros': [], 'total': 0}

    # Procurar arquivo de profissionais
    prof_paths = [
        base_dir / 'profissionais_autenticacao.json',
        Path.cwd() / 'profissionais_autenticacao.json',
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

    # Carregar dados de ramais (prioriza dados embutidos no arquivo de extração)
    ramais_data, mapping_data = carregar_ramais_data(escalas)

    if ramais_data is None:
        print("⚠️  Ramais não carregados - funcionalidade de extensões desabilitada")
    else:
        print(f"✅ Ramais data loaded: {len(ramais_data.get('departments', []))} departments")

    if mapping_data is None:
        print("⚠️  Mapeamento de setores não carregado - funcionalidade de extensões desabilitada")
    else:
        print(f"✅ Mapping data loaded: {len(mapping_data.get('sector_mappings', []))} sector mappings")

    # ✅ CRITICAL FIX: SEMPRE adicionar ramais_hro e setor_ramais_mapping ao objeto escalas
    # Isso garante que os dados estejam disponíveis no JavaScript da dashboard
    # MESMO em caso de fallback ou quando escalas não tem ramais embutidos

    # Verificar se escalas já tem ramais (por exemplo, se veio do fallback que agora tem ramais)
    if 'ramais_hro' not in escalas or not escalas['ramais_hro']:
        if ramais_data:
            escalas['ramais_hro'] = ramais_data
            print(f"✅ Embedded ramais_hro into escalas object (from carregar_ramais_data)")
        else:
            # Fallback final: estrutura vazia mas válida
            escalas['ramais_hro'] = {'departments': []}
            print(f"⚠️  Usando ramais_hro vazio como fallback")
    else:
        print(f"✅ Ramais_hro já presente em escalas: {len(escalas['ramais_hro'].get('departments', []))} departments")

    if 'setor_ramais_mapping' not in escalas or not escalas['setor_ramais_mapping']:
        if mapping_data:
            escalas['setor_ramais_mapping'] = mapping_data
            print(f"✅ Embedded setor_ramais_mapping into escalas object (from carregar_ramais_data)")
        else:
            # Fallback final: estrutura vazia mas válida
            escalas['setor_ramais_mapping'] = {'sector_mappings': []}
            print(f"⚠️  Usando setor_ramais_mapping vazio como fallback")
    else:
        print(f"✅ Setor_ramais_mapping já presente em escalas: {len(escalas['setor_ramais_mapping'].get('sector_mappings', []))} mappings")

    html = """<!DOCTYPE html>
<!-- ============================================================
     ARQUIVO GERADO AUTOMATICAMENTE — NÃO EDITE MANUALMENTE
     Edite: gerar_dashboard_executivo.py
     Gerado por: update_dashboard.py via GitHub Actions (diariamente)
     Alterações diretas neste arquivo SERÃO PERDIDAS na próxima execução
     ============================================================ -->
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="version" content="VERSAO_GERACAO">
    <meta name="theme-color" content="#0d3b66">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="manifest" href="manifest.json">
    <link rel="apple-touch-icon" href="icon.svg">
    <title>Escala - ALVF</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📋</text></svg>">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
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

        /* CSS Variables para Temas */
        :root {
            /* Cores principais */
            --bg-primary: #f8f9fb;
            --bg-secondary: #ffffff;
            --bg-tertiary: #f8fbff;
            --bg-gradient-start: #f8fbff;
            --bg-gradient-end: #e8eef7;

            /* Textos */
            --text-primary: #1a1a1a;
            --text-secondary: #666666;
            --text-tertiary: #999999;

            /* Bordas */
            --border-color: #e8eef7;
            --border-color-hover: #ddd;

            /* Cores de destaque */
            --color-primary: #0d3b66;
            --color-primary-dark: #0a2f52;
            --color-primary-light: #1a5490;
            --color-success: #28a745;
            --color-success-dark: #218838;
            --color-warning: #ffc107;
            --color-danger: #dc3545;
            --color-info: #17a2b8;
            --color-purple: #6610f2;

            /* Shadows */
            --shadow-sm: 0 2px 8px rgba(13, 59, 102, 0.1);
            --shadow-md: 0 2px 12px rgba(0, 0, 0, 0.08);
            --shadow-lg: 0 4px 16px rgba(0, 0, 0, 0.12);
            --shadow-xl: 0 8px 24px rgba(13, 59, 102, 0.2);

            /* Badges - Turnos */
            --badge-matutino-bg: #d4edda;
            --badge-matutino-text: #155724;
            --badge-vespertino-bg: #fff3cd;
            --badge-vespertino-text: #856404;
            --badge-noturno-bg: #d1ecf1;
            --badge-noturno-text: #0c5460;
            --badge-24h-bg: #f8d7da;
            --badge-24h-text: #721c24;
            --badge-sobreaviso-bg: #e7e7ff;
            --badge-sobreaviso-text: #4a4a8a;
            --badge-rotina-bg: #e2e3e5;
            --badge-rotina-text: #383d41;
            --badge-plantao-bg: #ffdab9;
            --badge-plantao-text: #8b4513;
            --badge-diurno-bg: #d4edda;
            --badge-diurno-text: #155724;
            --badge-misto-bg: #e2d5f8;
            --badge-misto-text: #6610f2;
            --badge-outro-bg: #e2e3e5;
            --badge-outro-text: #6c757d;

            /* Modal */
            --modal-overlay: rgba(0, 0, 0, 0.7);
            --modal-overlay-light: rgba(0, 0, 0, 0.6);
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            transition: background-color 0.3s ease, color 0.3s ease;
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
            background: var(--modal-overlay);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
        }

        .auth-modal.hidden {
            display: none;
        }

        .auth-modal-content {
            background: var(--bg-secondary);
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            max-width: 400px;
            width: 90%;
            text-align: center;
        }

        .auth-modal-content h2 {
            color: var(--color-primary);
            margin-bottom: 15px;
            font-size: 1.5em;
        }

        .auth-modal-content p {
            color: var(--text-secondary);
            margin-bottom: 20px;
            font-size: 0.95em;
        }

        .auth-input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid var(--border-color-hover);
            border-radius: 8px;
            font-size: 1em;
            margin-bottom: 15px;
            box-sizing: border-box;
            transition: border-color 0.3s ease;
            background: var(--bg-secondary);
            color: var(--text-primary);
        }

        .auth-input:focus {
            outline: none;
            border-color: var(--color-primary);
            box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.1);
        }

        .auth-btn {
            width: 100%;
            padding: 12px;
            background: var(--color-primary);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .auth-btn:hover {
            background: var(--color-primary-dark);
            transform: translateY(-1px);
            box-shadow: var(--shadow-sm);
        }

        .auth-btn:active {
            transform: translateY(0);
        }

        .auth-error {
            color: var(--color-danger);
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
            border-bottom: 2px solid var(--border-color);
        }

        .auth-tab-btn {
            flex: 1;
            padding: 10px;
            background: none;
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-size: 1em;
            color: var(--text-secondary);
            transition: all 0.3s ease;
        }

        .auth-tab-btn.active {
            color: var(--color-primary);
            border-bottom-color: var(--color-primary);
            font-weight: 600;
        }

        .auth-tab-btn:hover {
            color: var(--color-primary);
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

        /* Seletor de dia como toggle segmentado (botões conectados) */
        .date-selector {
            display: inline-flex;
            border: 2px solid #e8eef7;
            border-radius: 8px;
            overflow: hidden;
            background: white;
        }

        .date-btn {
            padding: 10px 18px;
            background: white;
            border: none;
            border-left: 1px solid #e8eef7;
            cursor: pointer;
            font-size: 0.95em;
            font-weight: 500;
            color: #666;
            transition: background 0.2s ease, color 0.2s ease;
            font-family: 'Inter', sans-serif;
        }

        .date-btn:first-child {
            border-left: none;
        }

        .date-btn:hover {
            color: #0d3b66;
            background: #f2f6fc;
        }

        .date-btn.active {
            background: #0d3b66;
            color: white;
        }

        .search-section {
            flex: 1;
            min-width: 250px;
        }

        .search-input {
            width: 100%;
            padding: 12px 20px;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            font-size: 0.95em;
            transition: all 0.3s ease;
            font-family: 'Inter', sans-serif;
            background: var(--bg-secondary);
            color: var(--text-primary);
        }

        .search-input:focus {
            outline: none;
            border-color: var(--color-primary);
            background: var(--bg-tertiary);
            box-shadow: 0 0 0 3px rgba(74, 158, 255, 0.1);
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
            background: #0d3b66;
            color: white;
        }

        .btn-print:hover {
            background: #0a2947;
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(13, 59, 102, 0.3);
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

        .contacts-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 12px;
        }

        .contact-item {
            display: flex;
            flex-direction: column;
            gap: 5px;
            padding: 12px 15px;
            border: 1px solid #e8eef7;
            border-left: 4px solid #0d3b66;
            border-radius: 8px;
            background: white;
            transition: all 0.2s ease;
        }

        .contact-item:hover {
            background: #f8fbff;
            border-color: #0d3b66;
            box-shadow: 0 2px 8px rgba(13, 59, 102, 0.1);
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

        .contact-phone-vazio {
            color: #999;
            font-style: italic;
            font-size: 0.9em;
        }

        /* Modal de Ramais */
        .ramais-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: var(--modal-overlay-light);
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
            background: var(--bg-secondary);
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
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 15px;
        }

        .ramais-modal-header h2 {
            color: var(--color-primary);
            font-size: 1.5em;
            margin: 0;
        }

        .ramais-modal-close {
            background: none;
            border: none;
            font-size: 1.5em;
            color: var(--text-secondary);
            cursor: pointer;
            padding: 0;
            line-height: 1;
        }

        .ramais-modal-close:hover {
            color: var(--color-primary);
        }

        .ramais-search {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid var(--border-color-hover);
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 1em;
            background: var(--bg-secondary);
            color: var(--text-primary);
        }

        .ramais-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 12px;
        }

        .ramal-item {
            display: flex;
            flex-direction: column;
            gap: 5px;
            padding: 12px 15px;
            border: 1px solid #e8eef7;
            border-left: 4px solid #0d3b66;
            border-radius: 8px;
            background: white;
            transition: all 0.2s ease;
        }

        .ramal-item:hover {
            background: #f8fbff;
            border-color: #0d3b66;
            box-shadow: 0 2px 8px rgba(13, 59, 102, 0.1);
        }

        .ramal-dept-line {
            font-weight: 600;
            color: #0d3b66;
            font-size: 0.95em;
        }

        .ramal-exts-line {
            color: #28a745;
            font-size: 0.9em;
            font-weight: 500;
        }

        .ramal-dept {
            font-weight: 600;
            color: #0d3b66;
            font-size: 0.95em;
            flex: 1;
        }

        .ramal-separator {
            color: #ccc;
            font-size: 0.9em;
        }

        .ramal-exts-inline {
            color: #28a745;
            font-size: 0.9em;
            font-weight: 500;
            white-space: nowrap;
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
            color: var(--color-primary);
            margin-bottom: 15px;
            padding: 12px;
            background: var(--bg-secondary);
            border-radius: 8px;
            box-shadow: var(--shadow-sm);
        }

        .last-update {
            text-align: right;
            font-size: 0.9em;
            color: var(--text-secondary);
            margin-bottom: 20px;
            padding: 10px 20px;
            display: flex;
            justify-content: flex-end;
            align-items: center;
            gap: 8px;
        }

        .update-status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }

        .update-status-text {
            font-size: 0.85em;
            color: var(--text-secondary);
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
            background: var(--bg-secondary);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: var(--shadow-md);
            border-left: 4px solid var(--color-primary);
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }

        .stat-number {
            font-size: 2em;
            font-weight: 700;
            color: var(--color-primary);
            margin-bottom: 5px;
        }

        .stat-label {
            color: var(--text-secondary);
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Setores em grid de 2 colunas; os de turno ocupam a linha inteira.
           align-items:start evita que um card curto estique até a altura do vizinho. */
        #categorias {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            align-items: start;
        }

        .category-full {
            grid-column: 1 / -1;
        }

        .category {
            background: var(--bg-secondary);
            border-radius: 12px;
            box-shadow: var(--shadow-md);
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .category:hover {
            box-shadow: var(--shadow-lg);
        }

        .categoria-header {
            background: linear-gradient(135deg, var(--bg-gradient-start) 0%, var(--bg-gradient-end) 100%);
            padding: 18px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-left: 4px solid var(--color-primary);
            transition: all 0.3s ease;
        }

        .categoria-header:hover {
            background: linear-gradient(135deg, var(--bg-gradient-end) 0%, var(--border-color) 100%);
        }

        .categoria-header-text {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex: 1;
            gap: 15px;
        }

        .categoria-nome {
            font-size: 1.15em;
            font-weight: 600;
            color: var(--color-primary);
        }

        .setor-nome-curto { display: none; }

        .categoria-count {
            color: var(--text-secondary);
            font-size: 0.9em;
            font-weight: 500;
        }

        .categoria-toggle {
            color: #0d3b66;
            font-size: 1.4em;
            line-height: 1;
            margin-left: auto;
            padding-left: 20px;
            width: 1em;
            text-align: center;
        }

        /* Botões de preferência do setor */
        .setor-pref-btns {
            display: flex;
            gap: 4px;
            margin-left: 8px;
            opacity: 0.35;
            transition: opacity 0.2s;
        }
        .categoria-header:hover .setor-pref-btns {
            opacity: 1;
        }
        .btn-pref {
            background: none;
            border: 1px solid transparent;
            border-radius: 4px;
            cursor: pointer;
            padding: 2px 7px;
            font-size: 1em;
            line-height: 1.4;
            color: #888;
            transition: all 0.15s;
        }
        .btn-pref:hover { background: rgba(0,0,0,0.08); border-color: #ccc; }
        .btn-pref.favorito-ativo { color: #f59e0b; opacity: 1 !important; }

        /* Setor favoritado */
        .category.setor-favorito .categoria-header {
            border-left-color: #f59e0b;
            background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        }
        .category.setor-favorito .categoria-nome { color: #92400e; }

        /* Toast (aviso temporário) */
        .toast {
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%) translateY(20px);
            background: #0d3b66;
            color: #fff;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 0.9em;
            box-shadow: 0 4px 16px rgba(0,0,0,0.25);
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.25s ease, transform 0.25s ease;
            z-index: 9999;
            max-width: 90vw;
            text-align: center;
        }
        .toast.show {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }

        /* Barra de setores ocultos — ocupa a linha inteira do grid */
        .setores-ocultos-bar {
            grid-column: 1 / -1;
            margin-top: 12px;
            padding: 10px 16px;
            background: #f8f9fa;
            border-radius: 8px;
            border: 1px dashed #dee2e6;
            font-size: 0.88em;
            color: #6c757d;
        }
        .setores-ocultos-bar summary {
            cursor: pointer;
            user-select: none;
            font-weight: 500;
        }
        .setores-ocultos-lista {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        .setor-oculto-chip {
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 20px;
            padding: 4px 12px;
            font-size: 0.9em;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .setor-oculto-chip button {
            background: none;
            border: none;
            cursor: pointer;
            color: #28a745;
            font-size: 1em;
            padding: 0;
            line-height: 1;
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
            background: white;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #e8eef7;
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
            font-size: 1em;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .turno-title::before {
            content: attr(data-count);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
            background: var(--color-primary);
            color: white;
            border-radius: 50%;
            font-size: 0.85em;
            font-weight: 700;
            flex-shrink: 0;
        }

        .turno-title::after {
            content: '';
        }

        .profissionais-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .profissional {
            padding: 10px 12px;
            background: var(--bg-secondary);
            border-radius: 6px;
            border: 1px solid var(--border-color);
            transition: all 0.2s ease;
        }

        .profissional:hover {
            border-color: var(--color-primary);
            box-shadow: var(--shadow-sm);
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
            min-width: 0;
        }

        .profissional-nome-text {
            font-weight: 600;
            color: #1a1a1a;
            font-size: 0.95em;
        }

        .profissional-nome-curto {
            display: none;
        }

        /* Horário logo abaixo do nome, alinhado sob o nome (após o ícone). */
        .profissional-info {
            font-size: 0.85em;
            color: #666;
            display: flex;
            align-items: center;
            gap: 8px;
            padding-left: 28px;
        }

        .info-horario {
            color: #333;
            font-variant-numeric: tabular-nums;
            white-space: nowrap;
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
            background: var(--badge-matutino-bg);
            color: var(--badge-matutino-text);
        }

        .turno-badge.vespertino {
            background: var(--badge-vespertino-bg);
            color: var(--badge-vespertino-text);
        }

        .turno-badge.noturno {
            background: var(--badge-noturno-bg);
            color: var(--badge-noturno-text);
        }

        .turno-badge.badge-24h {
            background: var(--badge-24h-bg);
            color: var(--badge-24h-text);
        }

        .turno-badge.sobreaviso {
            background: var(--badge-sobreaviso-bg);
            color: var(--badge-sobreaviso-text);
        }

        .turno-badge.rotina {
            background: var(--badge-rotina-bg);
            color: var(--badge-rotina-text);
        }

        .turno-badge.plantao {
            background: var(--badge-plantao-bg);
            color: var(--badge-plantao-text);
        }

        .turno-badge.diurno {
            background: var(--badge-diurno-bg);
            color: var(--badge-diurno-text);
        }

        .turno-badge.misto {
            background: var(--badge-misto-bg);
            color: var(--badge-misto-text);
        }

        .turno-badge.outro {
            background: var(--badge-outro-bg);
            color: var(--badge-outro-text);
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

        .telefone-icon-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
            margin-right: 8px;
            background: transparent;
            border: none;
            cursor: pointer;
            border-radius: 50%;
            transition: all 0.3s ease;
            flex-shrink: 0;
            position: relative;
        }

        .telefone-icon-btn:hover {
            background: rgba(13, 59, 102, 0.1);
            transform: scale(1.1);
        }

        /* Tooltip now handled via JavaScript */
        .telefone-icon-btn:hover::before,
        .telefone-icon-btn:hover::after {
            content: none;
            display: none;
        }

        .telefone-icon {
            width: 20px;
            height: 20px;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%2328a745"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>') center/contain no-repeat;
        }

        /* JavaScript-based tooltip for WhatsApp phone numbers */
        .phone-tooltip {
            position: fixed;
            background: #0d3b66;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 0.85em;
            white-space: nowrap;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s ease;
        }

        .phone-tooltip.show {
            opacity: 1;
        }

        .phone-tooltip-arrow {
            position: fixed;
            width: 0;
            height: 0;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top: 6px solid #0d3b66;
            pointer-events: none;
            opacity: 0;
            z-index: 10001;
            transition: opacity 0.2s ease;
        }

        .phone-tooltip-arrow.show {
            opacity: 1;
        }

        .data-tabs {
            display: flex;
            gap: 5px;
            margin-bottom: 20px;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 5px;
        }

        .data-tab {
            flex: 1;
            padding: 12px;
            text-align: center;
            background: var(--bg-secondary);
            border: none;
            border-bottom: 3px solid transparent;
            cursor: pointer;
            font-size: 1em;
            font-weight: 500;
            color: var(--text-secondary);
            transition: all 0.3s ease;
            border-radius: 8px 8px 0 0;
            position: relative;
            bottom: -2px;
        }

        .data-tab:hover {
            color: var(--color-primary);
        }

        .data-tab.active {
            color: var(--color-primary);
            border-bottom-color: var(--color-primary);
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
                align-items: center;
                gap: 8px;
                flex-direction: column;
            }

            .header-right {
                flex: none;
                min-width: auto;
                width: 100%;
                justify-content: center;
                align-items: center;
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

            /* Mobile: setores em coluna única */
            #categorias {
                grid-template-columns: 1fr;
            }

            .stats {
                grid-template-columns: 1fr;
            }

            .date-selector {
                display: flex;
                width: 100%;
            }

            .date-btn {
                flex: 1;
                padding: 8px 12px;
                font-size: 0.9em;
            }

            /* Modal fixes for mobile */
            .contacts-modal-content {
                width: 95%;
                max-width: calc(100vw - 20px);
                max-height: 90vh;
                padding: 20px;
            }

            .contacts-modal-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 12px;
                margin-bottom: 15px;
            }

            .contacts-modal-header h2 {
                font-size: 1.2em;
                width: 100%;
            }

            .contacts-modal-close {
                position: absolute;
                top: 15px;
                right: 15px;
            }

            .contacts-list {
                grid-template-columns: 1fr;
                gap: 10px;
            }

            .contact-item {
                padding: 10px 12px;
            }

            /* Ramais modal fixes for mobile */
            .ramais-modal-content {
                width: 95%;
                max-width: calc(100vw - 20px);
                max-height: 90vh;
                padding: 20px;
            }

            .ramais-modal-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 12px;
                margin-bottom: 15px;
            }

            .ramais-modal-header h2 {
                font-size: 1.2em;
                width: 100%;
            }

            .ramais-modal-close {
                position: absolute;
                top: 15px;
                right: 15px;
            }

            .ramais-list {
                grid-template-columns: 1fr;
                gap: 10px;
            }

            .ramal-item {
                padding: 10px 12px;
            }

            .contacts-search,
            .ramais-search {
                padding: 10px 12px;
                font-size: 0.95em;
                margin-bottom: 15px;
            }

            .contacts-warning {
                font-size: 0.85em;
                padding: 10px;
                margin-bottom: 15px;
            }
        }

        /* Cabeçalho visível apenas na impressão */
        .print-header {
            display: none;
        }

        /* Estilos para Impressão — A4 retrato */
        @media print {
            @page {
                size: A4 landscape;
                margin: 5mm;
            }

            * { box-shadow: none !important; }

            html, body {
                background: white;
                font-family: Arial, Helvetica, sans-serif;
                font-size: 8pt;
                color: #000;
            }

            /* Ocultar elementos de interface */
            .controls-bar,
            .header,
            .dashboard-description,
            .contacts-modal,
            .ramais-modal,
            .auth-modal,
            .date-display,
            .last-update,
            .stats,
            .categoria-toggle,
            .setor-pref-btns,
            .setores-ocultos-bar,
            .app-footer,
            .telefone-icon-btn,
            .turno-badge,
            .setor-ramais {
                display: none !important;
            }

            .container {
                max-width: 100%;
                padding: 0 !important;
                margin: 0 !important;
            }

            /* Cabeçalho de impressão */
            .print-header {
                display: flex !important;
                justify-content: space-between;
                align-items: baseline;
                border-bottom: 1pt solid #1a4a7a;
                padding-bottom: 1mm;
                margin-bottom: 2mm;
            }
            .print-header-title {
                font-size: 11pt;
                font-weight: bold;
                color: #1a4a7a;
            }
            .print-header-sub {
                font-size: 9pt;
                font-weight: normal;
                color: #555;
            }
            .print-header-date {
                font-size: 11pt;
                font-weight: bold;
                color: #333;
            }

            /* 4 colunas estilo jornal — landscape, preenche espaço sem gaps */
            #categorias {
                display: block !important;
                columns: 4;
                column-gap: 2mm;
            }

            .category {
                break-inside: avoid;
                display: inline-block;
                width: 100%;
                border: 0.5pt solid #bbb;
                border-radius: 1pt;
                overflow: hidden;
                margin: 0 0 1.5mm 0 !important;
                padding: 0 !important;
            }

            .category.setor-favorito .categoria-header,
            .categoria-header {
                background: white !important;
                border-bottom: 1.5pt solid #1a4a7a !important;
                padding: 1mm 2mm !important;
                margin: 0 !important;
                display: flex !important;
                align-items: center;
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }

            .categoria-header-text { flex: 1 !important; }

            .categoria-nome {
                font-size: 12pt !important;
                font-weight: bold !important;
                color: #1a4a7a !important;
                line-height: 1.1 !important;
            }

            .setor-nome-full { display: none !important; }
            .setor-nome-curto { display: inline !important; }

            .categoria-content {
                display: block !important;
                max-height: none !important;
                padding: 1mm !important;
                margin: 0 !important;
            }

            /* Turnos em 2 sub-colunas dentro do setor */
            .turnos-container {
                display: grid !important;
                grid-template-columns: 1fr 1fr !important;
                gap: 1mm !important;
            }

            .turno-coluna {
                border: none !important;
                background: none !important;
                padding: 0 !important;
                margin: 0 !important;
            }

            .turno-title {
                font-size: 10pt !important;
                font-weight: bold !important;
                color: #1a4a7a !important;
                border-bottom: 0.3pt solid #ddd !important;
                padding-bottom: 0.2mm !important;
                margin-bottom: 0.5mm !important;
                line-height: 1.1 !important;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }

            .turno-title::before {
                display: none !important;
            }

            .profissionais-list {
                display: block !important;
                padding: 0 !important;
            }

            .profissional {
                display: block !important;
                border: none !important;
                padding: 0.3mm 0 !important;
                margin: 0 !important;
                border-bottom: 0.3pt solid #eee !important;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }

            .profissional:last-child { border-bottom: none !important; }

            .profissional-nome {
                display: block !important;
                font-size: 12pt !important;
                font-weight: bold !important;
                color: #000 !important;
                margin: 0 !important;
                padding: 0 !important;
                line-height: 1.2 !important;
            }

            .profissional-nome-wrapper { display: inline !important; }
            .profissional-nome-text { display: none !important; }
            .profissional-nome-curto { display: inline !important; color: #000 !important; }

            /* Horário abaixo do nome — sem overflow na margem direita */
            .profissional::after {
                content: attr(data-hora);
                display: block !important;
                font-size: 10pt !important;
                color: #555 !important;
                line-height: 1.2 !important;
            }

            /* Ocultar bloco de info (setor + horário duplicados) */
            .profissional-info { display: none !important; }

            /* Setores excluídos da impressão */
            .print-exclude { display: none !important; }
        }

        /* Footer Styles */
        .app-footer {
            background: var(--bg-secondary);
            border-top: 1px solid var(--border-color);
            margin-top: 60px;
            padding: 30px 20px;
            color: #999;
            text-align: center;
        }

        .footer-title {
            font-size: 0.9em;
            font-weight: 600;
            color: var(--color-primary);
            margin: 0 0 8px 0;
        }

        .footer-text {
            font-size: 0.8em;
            margin: 0;
            cursor: pointer;
            transition: color 0.3s ease;
            color: #aaa;
        }

        .footer-text:hover {
            color: var(--color-primary);
        }

        /* ============================================================
           MELHORIAS V4 — dark mode, filtros, "agora", mobile, a11y
           ============================================================ */

        /* ---- Tema escuro: redefinição de tokens ---- */
        html { color-scheme: light; }
        html[data-theme="dark"] {
            color-scheme: dark;
            --bg-primary: #0f1722;
            --bg-secondary: #16212f;
            --bg-tertiary: #1a2736;
            --bg-gradient-start: #1a2736;
            --bg-gradient-end: #14202e;
            --text-primary: #e6ecf3;
            --text-secondary: #9db0c3;
            --text-tertiary: #7b8fa0;
            --border-color: #24344a;
            --border-color-hover: #35496a;
            --color-primary: #6ea8dd;
            --color-primary-dark: #8dbde8;
            --color-primary-light: #4a86c2;
            --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.35);
            --shadow-md: 0 2px 12px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 4px 16px rgba(0, 0, 0, 0.5);
            --shadow-xl: 0 8px 24px rgba(0, 0, 0, 0.55);
            --badge-matutino-bg: #17402a;  --badge-matutino-text: #8fe0af;
            --badge-vespertino-bg: #4a3607; --badge-vespertino-text: #f3cd76;
            --badge-noturno-bg: #1c3050;   --badge-noturno-text: #a7c6f5;
            --badge-24h-bg: #4c1d24;       --badge-24h-text: #f1a3ae;
            --badge-sobreaviso-bg: #2b2b52; --badge-sobreaviso-text: #b9b9f0;
            --badge-rotina-bg: #2c3238;    --badge-rotina-text: #c3cad1;
            --badge-plantao-bg: #4a2e14;   --badge-plantao-text: #f0c295;
            --badge-diurno-bg: #17402a;    --badge-diurno-text: #8fe0af;
            --badge-misto-bg: #33254d;     --badge-misto-text: #cbb8f5;
            --badge-outro-bg: #2c3238;     --badge-outro-text: #aab3bb;
            --modal-overlay: rgba(0, 0, 0, 0.8);
            --modal-overlay-light: rgba(0, 0, 0, 0.75);
        }
        html[data-theme="dark"] .date-selector,
        html[data-theme="dark"] .date-btn { background: var(--bg-secondary); color: var(--text-secondary); border-color: var(--border-color); }
        html[data-theme="dark"] .date-btn.active { background: var(--color-primary); color: #0f1722; }
        html[data-theme="dark"] .date-btn:hover { color: var(--color-primary-dark); background: var(--bg-tertiary); }
        html[data-theme="dark"] .turno-coluna { background: var(--bg-secondary); border-color: var(--border-color); }
        html[data-theme="dark"] .btn-toggle-sections { background: var(--bg-secondary); color: var(--color-primary); border-color: var(--color-primary); }
        html[data-theme="dark"] .contacts-modal-content,
        html[data-theme="dark"] .ramais-modal-content { background: var(--bg-secondary); color: var(--text-primary); }
        html[data-theme="dark"] .contact-item { background: var(--bg-secondary); border-color: var(--border-color); }
        html[data-theme="dark"] .contact-item:hover { background: var(--bg-tertiary); }
        html[data-theme="dark"] .contact-name,
        html[data-theme="dark"] .contacts-modal-header h2 { color: var(--color-primary); }
        html[data-theme="dark"] .contacts-search { background: var(--bg-tertiary); color: var(--text-primary); border-color: var(--border-color); }
        html[data-theme="dark"] .contacts-warning { background: #3d3110; border-color: #6b5a1e; color: #e8d9a0; }
        html[data-theme="dark"] .setores-ocultos-bar { background: var(--bg-secondary); border-color: var(--border-color); color: var(--text-secondary); }
        html[data-theme="dark"] .setor-oculto-chip { background: var(--bg-tertiary); border-color: var(--border-color); }
        html[data-theme="dark"] .category.setor-favorito .categoria-header { background: linear-gradient(135deg, #3a2f10 0%, #2e2508 100%); }
        html[data-theme="dark"] .category.setor-favorito .categoria-nome { color: #f3cd76; }
        html[data-theme="dark"] .profissional-nome-text { color: var(--text-primary); }
        html[data-theme="dark"] .info-horario { color: var(--text-secondary); }
        html[data-theme="dark"] .contact-phone { color: #6fd398; }
        html[data-theme="dark"] .ramal-item { background: var(--bg-tertiary); border-color: var(--border-color); }
        html[data-theme="dark"] .ramal-item:hover { background: var(--bg-secondary); border-color: var(--color-primary); }
        html[data-theme="dark"] .ramal-dept-line { color: var(--color-primary); }
        html[data-theme="dark"] .ramais-search { background: var(--bg-tertiary); color: var(--text-primary); border-color: var(--border-color); }
        html[data-theme="dark"] .ramais-modal-header h2 { color: var(--color-primary); }
        html[data-theme="dark"] .ramal-exts-line a,
        html[data-theme="dark"] .ramal-tel-link { color: #6fd398; }

        .btn-theme {
            background: var(--bg-secondary);
            color: var(--color-primary);
            border: 2px solid var(--color-primary);
            min-width: 44px;
        }
        .btn-theme:hover { background: var(--color-primary); color: var(--bg-secondary); }

        /* ---- Faixa lateral colorida por turno ---- */
        .profissional { border-left: 4px solid transparent; }
        .profissional.stripe-matutino  { border-left-color: #2f9e5f; }
        .profissional.stripe-diurno    { border-left-color: #2f9e5f; }
        .profissional.stripe-vespertino{ border-left-color: #d99114; }
        .profissional.stripe-noturno   { border-left-color: #3f74c9; }
        .profissional.stripe-badge-24h { border-left-color: #c0392b; }
        .profissional.stripe-sobreaviso{ border-left-color: #8a7bd8; }
        .profissional.stripe-plantao   { border-left-color: #d97b4a; }
        .profissional.stripe-rotina    { border-left-color: #9aa5ae; }

        /* ---- Destaque "de plantão agora" / encerrados ---- */
        .profissional.plantao-agora {
            border-left-color: #1e7e46;
            box-shadow: 0 0 0 1px rgba(30, 126, 70, 0.35);
        }
        .profissional.plantao-encerrado { opacity: 0.5; }
        .agora-pill {
            display: inline-block;
            background: #1e7e46;
            color: #fff;
            font-size: 0.68em;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 999px;
            letter-spacing: 0.4px;
            text-transform: uppercase;
        }

        /* ---- Chips de filtro por período ---- */
        .filter-chips {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
            margin-bottom: 14px;
        }
        .filter-chip {
            border: 1px solid var(--border-color);
            background: var(--bg-secondary);
            color: var(--text-secondary);
            border-radius: 999px;
            padding: 7px 14px;
            font-size: 0.82em;
            font-weight: 600;
            cursor: pointer;
            font-family: inherit;
            transition: background 0.15s ease, color 0.15s ease;
            min-height: 34px;
        }
        .filter-chip:hover { border-color: var(--color-primary); color: var(--color-primary); }
        .filter-chip.active { background: var(--color-primary); border-color: var(--color-primary); color: var(--bg-secondary); }

        /* ---- Dropdown "Ir para setor" ---- */
        .setor-select {
            margin-left: auto;
            border: 1px solid var(--border-color);
            background: var(--bg-secondary);
            color: var(--text-secondary);
            border-radius: 999px;
            padding: 6px 12px;
            font-size: 0.82em;
            font-weight: 600;
            font-family: inherit;
            cursor: pointer;
            max-width: 220px;
            min-height: 34px;
        }
        .setor-select:hover, .setor-select:focus { border-color: var(--color-primary); color: var(--color-primary); }
        @media (max-width: 768px) {
            .setor-select { margin-left: 0; max-width: 100%; flex: 1 1 100%; }
        }

        /* ---- Selo de frescor + próxima troca ---- */
        .freshness-stamp {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.85em;
            font-weight: 500;
        }
        .freshness-stamp.fresco { background: var(--badge-matutino-bg); color: var(--badge-matutino-text); }
        .freshness-stamp.velho  { background: var(--badge-24h-bg); color: var(--badge-24h-text); font-weight: 700; }
        .proxima-troca-chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.85em;
            background: var(--bg-gradient-end);
            color: var(--color-primary);
            font-weight: 600;
            white-space: nowrap;
        }

        /* ---- Estado vazio da busca ---- */
        .empty-state {
            grid-column: 1 / -1;
            text-align: center;
            padding: 48px 20px;
            color: var(--text-secondary);
            background: var(--bg-secondary);
            border-radius: 12px;
            border: 1px dashed var(--border-color-hover);
        }
        .empty-state strong { color: var(--text-primary); }
        .empty-state button {
            margin-top: 14px;
            padding: 10px 18px;
            border: none;
            border-radius: 8px;
            background: var(--color-primary);
            color: var(--bg-secondary);
            font-family: inherit;
            font-weight: 600;
            cursor: pointer;
        }

        /* ---- Modo compacto ---- */
        body.compacto .profissional { padding: 4px 10px; }
        body.compacto .profissional-nome { margin-bottom: 0; }
        body.compacto .turno-badge { display: none; }
        body.compacto .categoria-content { padding: 12px; }
        body.compacto .turnos-container { gap: 8px; }
        body.compacto .turno-coluna { padding: 8px; }
        body.compacto .profissionais-list { gap: 4px; }
        body.compacto .stats { display: none; }

        /* ---- Barra inferior fixa (mobile) ---- */
        .bottom-bar { display: none; }
        @media (max-width: 768px) {
            .bottom-bar {
                display: flex;
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: var(--bg-secondary);
                border-top: 1px solid var(--border-color);
                box-shadow: 0 -2px 12px rgba(13, 59, 102, 0.15);
                z-index: 4000;
                padding-bottom: env(safe-area-inset-bottom);
            }
            .bottom-bar button {
                flex: 1;
                background: none;
                border: none;
                border-left: 1px solid var(--border-color);
                padding: 8px 4px 10px;
                font-family: inherit;
                font-size: 0.68em;
                font-weight: 600;
                color: var(--color-primary);
                cursor: pointer;
                min-height: 52px;
            }
            .bottom-bar button:first-child { border-left: none; }
            .bottom-bar .bb-icon { display: block; font-size: 1.5em; margin-bottom: 2px; }
            body { padding-bottom: 64px; }
            /* Busca sticky no mobile */
            .controls-bar { position: sticky; top: 0; z-index: 3000; background: var(--bg-primary); padding: 8px 0; margin-bottom: 12px; }
            .action-buttons { display: none; }
        }
        @media print {
            .bottom-bar,
            .filter-chips,
            .setor-select,
            .proxima-troca-chip,
            .freshness-stamp,
            .agora-pill,
            .empty-state,
            .btn-theme { display: none !important; }
            .profissional.plantao-encerrado { opacity: 1 !important; }
            .profissional { border-left-width: 0 !important; }
        }

        /* ---- Ícones SVG inline ---- */
        .ic { vertical-align: -3px; }
        .btn .ic { margin-right: 2px; }
        .bb-icon .ic { display: inline-block; vertical-align: middle; }
        .chip-dot {
            display: inline-block;
            width: 9px; height: 9px;
            border-radius: 50%;
            background: #1e7e46;
            margin-right: 6px;
            vertical-align: 0;
        }
        .filter-chip.active .chip-dot { background: #7ee2a8; }
        .proxima-troca-chip .ic { vertical-align: -2px; margin-right: 2px; }

        /* ---- Ramais clicáveis ---- */
        .ramal-tel-link {
            color: inherit;
            text-decoration: none;
            border-bottom: 1px dotted var(--color-primary);
            padding: 2px 1px;
        }
        .ramal-tel-link:hover { color: var(--color-primary); }

        /* ---- Acessibilidade ---- */
        .btn-pref { padding: 8px 12px; min-width: 40px; min-height: 40px; }
        .categoria-header:focus-visible,
        .filter-chip:focus-visible,
        .setor-index-chip:focus-visible,
        .btn:focus-visible,
        .btn-pref:focus-visible,
        .date-btn:focus-visible,
        .bottom-bar button:focus-visible {
            outline: 3px solid var(--color-primary);
            outline-offset: 2px;
        }
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
    </style>
</head>
<body>
    <!-- Modal de Autenticação -->
    <div id="auth-modal" class="auth-modal">
        <div class="auth-modal-content">
            <h2>Acesso Restrito</h2>

            <!-- Login único: aceita os 4 últimos dígitos do telefone OU a senha geral -->
            <div class="auth-tab-content active">
                <p>Digite os <strong>4 últimos dígitos do seu telefone</strong> (cadastrado no app Escalas) ou a senha de acesso.</p>
                <p style="color: #666; font-size: 0.9em; margin: 15px 0;">Se não conseguir acessar, entre em contato conosco.</p>
                <input type="password" id="auth-input-outro" placeholder="4 dígitos do telefone ou senha" class="auth-input" onkeypress="if(event.key === 'Enter') autenticarOutro()">
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
                <h2>Diretório Telefônico HRO</h2>
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
                        <h2>Hospital Regional do Oeste</h2>
                        <div class="header-description">
                            <p>Escala Médica</p>
                        </div>
                    </div>
                </div>
                <div class="header-right">
                    <div class="header-date" id="data-atual-header"></div>
                </div>
            </div>
        </div>

        <!-- Controles -->
        <div class="controls-bar">
            <div class="date-selector">
                <button class="date-btn" data-dia="anterior" onclick="selecionarDia('anterior')">Dia Anterior</button>
                <button class="date-btn active" data-dia="atual" onclick="selecionarDia('atual')">Hoje</button>
                <button class="date-btn" data-dia="seguinte" onclick="selecionarDia('seguinte')">Amanhã</button>
            </div>
            <div class="search-section">
                <input type="text" class="search-input" id="search" placeholder="Busque por nome, setor, turno..." onkeyup="filtrarProfissionais()">
            </div>
            <div class="action-buttons">
                <button class="btn btn-contacts" onclick="abrirListaContatos()">Contatos</button>
                <button class="btn btn-ramais" onclick="abrirDiretorioRamais()">Ramais</button>
                <button class="btn btn-print" onclick="window.print()"><svg class="ic" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg> Imprimir</button>
                <button class="btn btn-theme" id="btn-compacto" onclick="alternarCompacto()" title="Alternar modo compacto (mais setores por tela)" aria-label="Modo compacto"><svg class="ic" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg></button>
                <button class="btn btn-theme" id="btn-theme" onclick="alternarTema()" title="Alternar tema claro/escuro" aria-label="Alternar tema"><svg class="ic" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg></button>
            </div>
        </div>

        <!-- Filtros por período + ir para setor -->
        <div class="filter-chips" id="filter-row">
            <div id="filter-chips" role="group" aria-label="Filtrar por período" style="display:contents"></div>
            <select id="setor-index" class="setor-select" aria-label="Ir para setor" onchange="if(this.value){irParaSetor(this.value); this.selectedIndex=0;}"></select>
        </div>

        <!-- Cabeçalho de impressão (visível só no print) -->
        <div class="print-header">
            <div class="print-header-title">Hospital Regional do Oeste <span class="print-header-sub">· Escala Médica</span></div>
            <div class="print-header-date" id="print-date-display"></div>
        </div>

        <!-- Data selecionada -->
        <div class="date-display" id="data-selecionada"></div>

        <!-- Status de Atualização + próxima troca de plantão -->
        <div class="last-update">
            <span class="proxima-troca-chip" id="proxima-troca" hidden></span>
            <span class="freshness-stamp" id="freshness-stamp">
                <span class="update-status-indicator" id="status-indicator"></span>
                <span class="update-status-text" id="status-text"></span>
            </span>
        </div>

        <!-- Estatísticas -->
        <div class="stats" id="stats"></div>

        <!-- Categorias -->
        <div id="categorias"></div>
    </div>

    <!-- Barra de ações fixa (só mobile) -->
    <nav class="bottom-bar" aria-label="Ações rápidas">
        <button onclick="abrirListaContatos()"><span class="bb-icon"><svg class="ic" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg></span>Contatos</button>
        <button onclick="abrirDiretorioRamais()"><span class="bb-icon"><svg class="ic" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg></span>Ramais</button>
        <button onclick="focarBusca()"><span class="bb-icon"><svg class="ic" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg></span>Buscar</button>
        <button onclick="alternarTema()" id="btn-theme-mobile"><span class="bb-icon"><svg class="ic" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg></span>Tema</button>
        <button onclick="window.scrollTo({top:0, behavior:'smooth'})"><span class="bb-icon"><svg class="ic" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg></span>Topo</button>
    </nav>

    <script>
        // Autenticação persistente via localStorage

        // Initialize data safely with error handling
        let escalas = null;
        let ramaisData = null;
        let setorRamaisMapping = null;

        try {
            // Parse escalas data
            escalas = """ + json.dumps(escalas, ensure_ascii=False) + """;
            console.log('✅ Escalas carregadas com sucesso:', escalas ? Object.keys(escalas).length : 0, 'keys');
        } catch (e) {
            console.error('❌ Erro ao parsear dados de escalas:', e.message);
            console.error('Stack:', e.stack);
            escalas = { atual: { data: 'Erro', registros: [] }, anterior: { data: 'Erro', registros: [] }, seguinte: { data: 'Erro', registros: [] }, data_atualizacao: 'N/A', hora_atualizacao: 'N/A', status_atualizacao: 'erro' };
        }

        try {
            // Parse ramais data - assignment happens here
            console.log('📍 Antes de atribuir ramaisData');
            ramaisData = """ + json.dumps(ramais_data if ramais_data else {}, ensure_ascii=False) + """;
            console.log('✅ Imediatamente após atribuição - ramaisData tipo:', typeof ramaisData);

            if (ramaisData && ramaisData.departments) {
                console.log('✅ Dados de ramais carregados:', ramaisData.departments.length, 'departments');
            } else {
                console.warn('⚠️  ramaisData carregado mas sem departments. Type:', typeof ramaisData, 'Keys:', ramaisData ? Object.keys(ramaisData) : 'null');
            }
        } catch (e) {
            console.error('❌ ERRO CRÍTICO ao parsear dados de ramais:', e.message);
            console.error('❌ Stack:', e.stack);
            console.error('❌ Definindo ramaisData para {} como fallback');
            ramaisData = {};
        }

        try {
            // Parse sector mapping data
            setorRamaisMapping = """ + json.dumps(mapping_data if mapping_data else {}, ensure_ascii=False) + """;
            console.log('✅ Mapeamento de setores carregado:', setorRamaisMapping ? Object.keys(setorRamaisMapping).length : 0, 'keys:', setorRamaisMapping ? Object.keys(setorRamaisMapping) : 'empty');
        } catch (e) {
            console.error('❌ Erro ao parsear mapeamento de setores:', e.message);
            setorRamaisMapping = {};
        }

        let diaSelecionado = 'atual';

        // Função para obter ramais de um setor
        function obterRamaisSetor(setorNome) {
            try {
                if (!ramaisData || !ramaisData.departments || !setorRamaisMapping || !setorRamaisMapping.sector_mappings) {
                    console.warn('⚠️  Dados de ramais não carregados corretamente');
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
            } catch (e) {
                console.error('❌ Erro em obterRamaisSetor:', e);
                return [];
            }
        }

        // Função para formatar ramais para exibição
        function formatarRamaisDisplay(extensions) {
            try {
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
            } catch (e) {
                console.error('❌ Erro em formatarRamaisDisplay:', e);
                return '';
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
            try {
                const ramaisList = document.getElementById('ramais-list');

                console.log('%c🔄 renderizarDiretorioRamais - INICIANDO', 'color: green; font-weight: bold');
                console.log('ramaisData type:', typeof ramaisData);
                console.log('ramaisData keys:', ramaisData ? Object.keys(ramaisData) : 'null/undefined');
                console.log('ramaisData.departments:', ramaisData && ramaisData.departments ? 'exists, length: ' + ramaisData.departments.length : 'NOT FOUND');

                if (!ramaisList) {
                    console.error('❌ CRÍTICO: #ramais-list element not found!');
                    return;
                }

                if (!ramaisData || !ramaisData.departments) {
                    console.warn('⚠️  ramaisData.departments not available');
                    console.warn('Full ramaisData:', ramaisData);
                    ramaisList.innerHTML = '<p style="text-align: center; color: #666;">Dados de ramais não disponíveis.</p>';
                    return;
                }

                console.log('✅ ramaisData.departments encontrado com', ramaisData.departments.length, 'itens');

                const departamentos = [...ramaisData.departments].sort((a, b) =>
                    a.name.localeCompare(b.name, 'pt-BR')
                );

                const html = departamentos.map(dept => {
                    const extsStr = dept.extensions.join(', ');
                    // Cada ramal vira um link tel: (no celular, toca para discar)
                    const extsDisplay = dept.extensions.map(ext =>
                        `<a href="tel:${String(ext).replace(/\\D/g, '')}" class="ramal-tel-link">${ext}</a>`
                    ).join(' | ');
                    // Split department name by " - " to get main name and sub-area
                    const nameParts = dept.name.split(' - ');
                    const mainName = nameParts[0];
                    const subArea = nameParts.length > 1 ? nameParts.slice(1).join(' - ') : '';

                    return `
                        <div class="ramal-item" data-search="${dept.name.toLowerCase()} ${extsStr}">
                            <div class="ramal-dept-line">${mainName}${subArea ? ' | ' + subArea : ''}</div>
                            <div class="ramal-exts-line">${extsDisplay}</div>
                        </div>
                    `;
                }).join('');

                ramaisList.innerHTML = html;
                console.log('✅ renderizarDiretorioRamais completado com', departamentos.length, 'departamentos');
            } catch (error) {
                console.error('❌ ERRO em renderizarDiretorioRamais:', error.message);
                console.error('Stack:', error.stack);
                const ramaisList = document.getElementById('ramais-list');
                if (ramaisList) {
                    ramaisList.innerHTML = '<p style="text-align: center; color: #cc0000;">Erro ao carregar ramais: ' + error.message + '</p>';
                }
            }
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

        // Filtro ativo por período ('' = todos). Combina com a busca por texto.
        let filtroPeriodo = '';

        // Mapeia o tipo de badge para o grupo do chip de filtro
        function grupoDoTipo(tipo) {
            if (tipo === 'matutino' || tipo === 'diurno') return 'manha';
            if (tipo === 'vespertino') return 'tarde';
            if (tipo === 'noturno') return 'noite';
            if (tipo === 'sobreaviso') return 'sobreaviso';
            if (tipo === 'badge-24h') return '24h';
            return 'outro';
        }

        function tipoDoProf(prof) {
            const m = (prof.className.match(/stripe-([\\w-]+)/) || []);
            return m[1] || 'outro';
        }

        function filtrarProfissionais() {
            const search = document.getElementById('search').value.toLowerCase().trim();
            const profissionais = document.querySelectorAll('.profissional');
            const categorias = document.querySelectorAll('.category');

            let visibleCount = 0;
            profissionais.forEach(prof => {
                const searchText = prof.getAttribute('data-search') || '';
                const passaBusca = !search || searchText.includes(search);
                let passaPeriodo = true;
                if (filtroPeriodo === 'agora') {
                    passaPeriodo = prof.classList.contains('plantao-agora');
                } else if (filtroPeriodo) {
                    passaPeriodo = grupoDoTipo(tipoDoProf(prof)) === filtroPeriodo;
                }
                if (passaBusca && passaPeriodo) {
                    prof.style.display = 'block';
                    visibleCount++;
                } else {
                    prof.style.display = 'none';
                }
            });

            // Esconde categorias sem profissionais visíveis
            categorias.forEach(categoria => {
                let visibleInCategory = 0;
                categoria.querySelectorAll('.profissional').forEach(prof => {
                    if (prof.style.display !== 'none') visibleInCategory++;
                });
                categoria.style.display = visibleInCategory === 0 ? 'none' : 'block';
            });

            // Estado vazio com saída clara
            let emptyEl = document.getElementById('empty-state');
            if (visibleCount === 0 && (search || filtroPeriodo)) {
                if (!emptyEl) {
                    emptyEl = document.createElement('div');
                    emptyEl.id = 'empty-state';
                    emptyEl.className = 'empty-state';
                    document.getElementById('categorias').appendChild(emptyEl);
                }
                const criterio = search ? `para "<strong>${search}</strong>"` : 'para este filtro';
                emptyEl.innerHTML = `<p>Nenhum profissional encontrado ${criterio} neste dia.</p>` +
                    `<button onclick="limparFiltros()">Limpar busca e filtros</button>`;
                emptyEl.style.display = 'block';
            } else if (emptyEl) {
                emptyEl.style.display = 'none';
            }
        }

        function limparFiltros() {
            document.getElementById('search').value = '';
            filtroPeriodo = '';
            document.querySelectorAll('.filter-chip').forEach(c =>
                c.classList.toggle('active', c.getAttribute('data-filtro') === ''));
            filtrarProfissionais();
        }

        function definirFiltroPeriodo(filtro) {
            filtroPeriodo = (filtroPeriodo === filtro) ? '' : filtro;
            if (filtroPeriodo === '') filtro = '';
            document.querySelectorAll('.filter-chip').forEach(c =>
                c.classList.toggle('active', c.getAttribute('data-filtro') === filtroPeriodo));
            filtrarProfissionais();
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
                // Check more specific terms FIRST to avoid substring matching issues
                // e.g., "neurologia" contains "ologia" which could match "urologia" check
                if (turno.includes('neurocirurgia')) return { ordem: 5, nome: 'Sobreaviso Neurocirurgia' };
                if (turno.includes('neurologia')) return { ordem: 5, nome: 'Sobreaviso Neurologia' };
                if (turno.includes('cardiologia')) return { ordem: 5, nome: 'Sobreaviso Cardiologia' };
                if (turno.includes('oftalmologia')) return { ordem: 5, nome: 'Sobreaviso Oftalmologia' };
                if (turno.includes('urologia')) return { ordem: 5, nome: 'Sobreaviso Urologia' };
                if (turno.includes('oncologia')) return { ordem: 5, nome: 'Sobreaviso Oncologia' };
                if (turno.includes('endoscopia')) return { ordem: 5, nome: 'Sobreaviso Endoscopia' };
                if (turno.includes('pediátrica') || turno.includes('pediatrica')) return { ordem: 5, nome: 'Sobreaviso Cirurgia Pediátrica' };
                if (turno.includes('vascular')) return { ordem: 5, nome: 'Sobreaviso Cirurgia Vascular' };
                if (turno.includes('cirurgia')) {
                    if (turno.includes('equipe 1') || turno.includes(' 1')) {
                        return { ordem: 5, nome: 'Sobreaviso Cirurgia - Equipe 1' };
                    } else if (turno.includes('equipe 2') || turno.includes(' 2')) {
                        return { ordem: 5, nome: 'Sobreaviso Cirurgia - Equipe 2' };
                    }
                    return { ordem: 5, nome: 'Sobreaviso Cirurgia' };
                }
                return { ordem: 5, nome: 'Sobreaviso' };
            }

            // Plantão Diurno
            if (turno.includes('plantão diurno')) return { ordem: 1, nome: 'Plantão Diurno' };

            return { ordem: 99, nome: turnoOriginal };
        }

        function temMultiplosTurnos(setor) {
            // Check if this sector has multiple different shifts (turnos)
            // by examining the actual data, not just the sector name
            const profissionaisDaSetor = escalas.atual.registros.filter(reg => reg.setor === setor);
            if (profissionaisDaSetor.length === 0) return false;

            const turnosUnicos = new Set(profissionaisDaSetor.map(prof => {
                const { nome } = normalizarTurno(prof.tipo_turno);
                return nome;
            }));

            return turnosUnicos.size > 1;
        }

        function obterTipoTurno(turnoText, horarioText = '') {
            // Identifica o tipo de turno com detecção hierárquica
            // Prioridade: MISTO → 24H → SOBREAVISO+FIM SEMANA → FIM SEMANA → Específico → ROTINA → OUTRO
            if (!turnoText) return 'misto';

            const turno = turnoText.toLowerCase();
            const horario = horarioText ? horarioText.toLowerCase() : '';

            // PRIORIDADE 0: Detecta turnos MISTOS (combinações de múltiplos períodos)
            // Exemplos: "Vesp - Noturno", "Matutino - Vespertino", "Vespertino/Noturno"
            const periodosPresentes = [
                turno.includes('matutino') || turno.includes('manhã'),
                turno.includes('vespertino') || turno.includes('vesp') || turno.includes('tarde'),
                turno.includes('noturno') || turno.includes('noite')
            ].filter(Boolean).length;

            if (periodosPresentes > 1) {
                return 'misto';
            }

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
                'misto': 'MISTO',
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

        // ── Preferências por usuário ──────────────────────────────
        function getPrefs() {
            const user = localStorage.getItem('auth_user') || 'guest';
            const raw = localStorage.getItem('prefs_' + user);
            return raw ? JSON.parse(raw) : { favoritos: [], ocultos: [] };
        }
        function savePrefs(prefs) {
            const user = localStorage.getItem('auth_user') || 'guest';
            localStorage.setItem('prefs_' + user, JSON.stringify(prefs));
        }
        function toggleFavorito(setor) {
            const prefs = getPrefs();
            const idx = prefs.favoritos.indexOf(setor);
            if (idx === -1) prefs.favoritos.push(setor);
            else prefs.favoritos.splice(idx, 1);
            savePrefs(prefs);
            renderizarEscala();
        }
        function toggleOcultar(setor) {
            const prefs = getPrefs();
            const oIdx = prefs.ocultos.indexOf(setor);
            let ocultou = false;
            if (oIdx === -1) {
                prefs.ocultos.push(setor);
                const fIdx = prefs.favoritos.indexOf(setor);
                if (fIdx !== -1) prefs.favoritos.splice(fIdx, 1);
                ocultou = true;
            } else {
                prefs.ocultos.splice(oIdx, 1);
            }
            savePrefs(prefs);
            renderizarEscala();
            if (ocultou) mostrarToast('Setor ocultado — reexiba na barra no rodapé da lista.');
        }

        // Aviso temporário no rodapé da tela
        let _toastTimer = null;
        function mostrarToast(msg) {
            let t = document.getElementById('toast');
            if (!t) {
                t = document.createElement('div');
                t.id = 'toast';
                t.className = 'toast';
                document.body.appendChild(t);
            }
            t.textContent = msg;
            t.classList.add('show');
            clearTimeout(_toastTimer);
            _toastTimer = setTimeout(() => t.classList.remove('show'), 3200);
        }
        // ─────────────────────────────────────────────────────────

        function renderizarEscala() {
            try {
                console.log('%c🔄 Dashboard v3-ramais - INICIANDO RENDERIZAÇÃO', 'color: blue; font-weight: bold');

                // Validate escalas data structure
                console.log('1️⃣  Validando escalas:', typeof escalas, escalas ? 'não-null' : 'null');
                if (!escalas) {
                    console.error('❌ escalas é null/undefined');
                    return;
                }

                console.log('2️⃣  Chaves de escalas:', Object.keys(escalas));
                if (!escalas[diaSelecionado]) {
                    console.error(`❌ escalas['${diaSelecionado}'] não existe. Chaves disponíveis:`, Object.keys(escalas));
                    return;
                }

                const dados = escalas[diaSelecionado];
                console.log('3️⃣  Dados do dia selecionado:', dados ? 'obtido' : 'null', 'Keys:', dados ? Object.keys(dados) : 'N/A');

                if (!dados || !dados.registros || !Array.isArray(dados.registros)) {
                    console.error('❌ dados.registros não é um array:', dados);
                    return;
                }

                console.log(`✅ 4️⃣  Renderizando ${dados.registros.length} profissionais para ${diaSelecionado}`);

                document.getElementById('data-selecionada').textContent = dados.data;
                document.getElementById('print-date-display').textContent = dados.data;

                // Dia sem dados (ex: "Amanhã" ainda não disponível): mostra aviso
                if (dados.registros.length === 0) {
                    const rotuloDia = diaSelecionado === 'seguinte' ? 'do dia seguinte'
                                    : diaSelecionado === 'anterior' ? 'do dia anterior' : 'deste dia';
                    document.getElementById('stats').innerHTML = '';
                    document.getElementById('categorias').innerHTML =
                        '<p style="text-align:center;color:#666;padding:40px 20px;">A escala ' + rotuloDia +
                        ' ainda não está disponível.</p>';
                    return;
                }

            // Mostrar indicador de status (dot colorido)
            const statusAtualizacao = escalas.status_atualizacao;
            const statusIndicator = document.getElementById('status-indicator');
            statusIndicator.className = 'update-status-indicator';

            if (statusAtualizacao === 'sucesso') {
                statusIndicator.classList.add('sucesso');
            } else if (statusAtualizacao === 'pendente') {
                statusIndicator.classList.add('pendente');
            } else {
                statusIndicator.classList.add('erro');
            }

            // Texto com data/hora da última atualização
            const statusText = document.getElementById('status-text');
            if (statusText) {
                const dataAtu = escalas.data_atualizacao || 'N/A';
                const horaAtu = escalas.hora_atualizacao || '';
                statusText.textContent = horaAtu
                    ? `Atualizado em ${dataAtu} às ${horaAtu}`
                    : `Atualizado em ${dataAtu}`;
            }

            const porSetor = {};
            dados.registros.forEach(prof => {
                if (!porSetor[prof.setor]) {
                    porSetor[prof.setor] = [];
                }
                porSetor[prof.setor].push(prof);
            });

            const prefs = getPrefs();
            const todosSetores = Object.keys(porSetor).sort();
            const setoresVisiveis = [
                ...todosSetores.filter(s => prefs.favoritos.includes(s)),
                ...todosSetores.filter(s => !prefs.favoritos.includes(s) && !prefs.ocultos.includes(s))
            ];
            const setoresOcultos = todosSetores.filter(s => prefs.ocultos.includes(s));

            // Setores excluídos da impressão (foco no PS)
            const EXCLUIR_PRINT = [
                'Alojamento Conjunto',
                'Ambulatório De Oncologia Pediátrica',
                'Ambulatório Oncologia - Triagem',
                'Núcleo Interno de Regulação (NIR) Médico Regulador',
                'R2 Clínica Médica UTI',
                'Residência de Clínica Médica',
                'Transplante - Sobreaviso Cirurgia',
                'Unidade de Cuidados Intermediários Neonatais - UCINCo E Sala de Parto - Escala Médica',
                'Unidade de Terapia Intensiva (UTI) Adulto I',
                'Unidade de Terapia Intensiva (UTI) Adulto II',
                'Unidade de Terapia Intensiva (UTI) Adulto III',
                'Unidade de Terapia Intensiva (UTI) Neonatal - Plantão - Escala Médica',
                'Unidade de Terapia Intensiva (UTI) Pediátrica',
            ];

            let html = '';

            setoresVisiveis.forEach(setor => {
                const profissionais = porSetor[setor];
                const isFavorito = prefs.favoritos.includes(setor);
                const isPrintExcluded = EXCLUIR_PRINT.includes(setor);
                // Note: ramais display is disabled for now - only shown in the Ramais modal
                // const ramaisSetor = obterRamaisSetor(setor);
                // const ramaisDisplay = formatarRamaisDisplay(ramaisSetor);

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
                    <div class="category category-full${isFavorito ? ' setor-favorito' : ''}${isPrintExcluded ? ' print-exclude' : ''}">
                        <div class="categoria-header expanded">
                            <div class="categoria-header-text">
                                <div class="categoria-nome">${isFavorito ? '★ ' : ''}<span class="setor-nome-full">${setor}</span><span class="setor-nome-curto">${setor.replace(/\s*[-–]\s*(Sobreaviso|Plantão|Plantao).*$/i, '').trim()}</span></div>
                            </div>
                            <div class="setor-pref-btns" onclick="event.stopPropagation()">
                                <button class="btn-pref${isFavorito ? ' favorito-ativo' : ''}" onclick="toggleFavorito('${setor.replace(/'/g, "\\'")}')" title="${isFavorito ? 'Remover dos favoritos' : 'Favoritar setor'}">★</button>
                                <button class="btn-pref" onclick="toggleOcultar('${setor.replace(/'/g, "\\'")}')" title="Ocultar este setor da lista (reversível no rodapé)">✕</button>
                            </div>
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
                                                <div class="profissional stripe-${obterTipoTurno(prof.tipo_turno, prof.horario)}" data-prof="${prof.profissional}" data-setor="${setor}" data-turno="${turno}" data-tipo="${prof.tipo_turno}" data-hora="${prof.horario}" data-search="${prof.profissional.toLowerCase()} ${setor.toLowerCase()} ${turno.toLowerCase()}">
                                                    <div class="profissional-nome">
                                                        ${telefone !== 'N/A' ? `<a href="${whatsappUrl}" target="_blank" class="telefone-icon-btn" data-phone="${telefone}" title="WhatsApp: ${telefone}"><span class="telefone-icon"></span></a>` : ''}
                                                        <div class="profissional-nome-wrapper">
                                                            <span class="profissional-nome-text">${prof.profissional}</span><span class="profissional-nome-curto">${(p => p.length <= 2 ? p.join(' ') : p[0] + ' ' + p[p.length-1])(prof.profissional.trim().split(/\s+/))}</span>
                                                        </div>
                                                    </div>
                                                    <div class="profissional-info">
                                                        <span class="info-horario">${prof.horario}</span>
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
                    <div class="category${isFavorito ? ' setor-favorito' : ''}${isPrintExcluded ? ' print-exclude' : ''}">
                        <div class="categoria-header expanded">
                            <div class="categoria-header-text">
                                <div class="categoria-nome">${isFavorito ? '★ ' : ''}<span class="setor-nome-full">${setor}</span><span class="setor-nome-curto">${setor.replace(/\s*[-–]\s*(Sobreaviso|Plantão|Plantao).*$/i, '').trim()}</span></div>
                            </div>
                            <div class="setor-pref-btns" onclick="event.stopPropagation()">
                                <button class="btn-pref${isFavorito ? ' favorito-ativo' : ''}" onclick="toggleFavorito('${setor.replace(/'/g, "\\'")}')" title="${isFavorito ? 'Remover dos favoritos' : 'Favoritar setor'}">★</button>
                                <button class="btn-pref" onclick="toggleOcultar('${setor.replace(/'/g, "\\'")}')" title="Ocultar este setor da lista (reversível no rodapé)">✕</button>
                            </div>
                        </div>
                        <div class="categoria-content">
                            <div class="profissionais-list">
                                ${profissionais.map(prof => {
                                    const profData = mapaProfissionais[prof.profissional.toLowerCase()];
                                    const telefone = profData ? profData.phone : 'N/A';
                                    const telefoneLimpo = telefone.replace(/\D/g, '');
                                    const whatsappUrl = `https://wa.me/55${telefoneLimpo}`;
                                    return `
                                    <div class="profissional stripe-${obterTipoTurno(prof.tipo_turno, prof.horario)}" data-prof="${prof.profissional}" data-setor="${setor}" data-turno="${prof.tipo_turno}" data-tipo="${prof.tipo_turno}" data-hora="${prof.horario}" data-search="${prof.profissional.toLowerCase()} ${setor.toLowerCase()}">
                                        <div class="profissional-nome">
                                            ${telefone !== 'N/A' ? `<a href="${whatsappUrl}" target="_blank" class="telefone-icon-btn" data-phone="${telefone}" title="WhatsApp: ${telefone}"><span class="telefone-icon"></span></a>` : ''}
                                            <div class="profissional-nome-wrapper">
                                                <span class="profissional-nome-text">${prof.profissional}</span><span class="profissional-nome-curto">${(p => p.length <= 2 ? p.join(' ') : p[0] + ' ' + p[p.length-1])(prof.profissional.trim().split(/\s+/))}</span>
                                            </div>
                                        </div>
                                        <div class="profissional-info">
                                            <span class="info-horario">${prof.horario}</span>
                                            <span class="turno-badge ${obterTipoTurno(prof.tipo_turno, prof.horario)}" title="${prof.tipo_turno}">${formatarTipoBadge(obterTipoTurno(prof.tipo_turno, prof.horario))}</span>
                                        </div>
                                    </div>
                                `}).join('')}
                            </div>
                        </div>
                    </div>
                    `;
                }
            });

            // Barra de setores ocultos
            if (setoresOcultos.length > 0) {
                html += `
                <details class="setores-ocultos-bar">
                    <summary>🚫 ${setoresOcultos.length} setor${setoresOcultos.length > 1 ? 'es' : ''} oculto${setoresOcultos.length > 1 ? 's' : ''} — clique para gerenciar</summary>
                    <div class="setores-ocultos-lista">
                        ${setoresOcultos.map(s => `
                        <div class="setor-oculto-chip">
                            <span>${s}</span>
                            <button onclick="toggleOcultar('${s.replace(/'/g, "\\'")}')" title="Mostrar setor">👁 mostrar</button>
                        </div>`).join('')}
                    </div>
                </details>`;
            }

            // CRITICAL: Verify element exists before inserting
            const categoriasEl = document.getElementById('categorias');
            if (!categoriasEl) {
                console.error('❌ CRITICAL: #categorias element not found!');
            } else {
                document.getElementById('categorias').innerHTML = html;
                console.log('✅ HTML inserted into #categorias, length:', html.length);
            }

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

            // Pós-render: "agora", chips, índice de setores, a11y, frescor
            aposRenderizar(porSetor, setoresVisiveis);
            } catch (error) {
                console.error('❌ ERRO CRÍTICO em renderizarEscala:', error.message);
                console.error('Stack:', error.stack);

                // Display error message to user
                const categoriasEl = document.getElementById('categorias');
                if (categoriasEl) {
                    categoriasEl.innerHTML = `
                        <div style="padding: 20px; background: #ffe6e6; border: 2px solid #cc0000; border-radius: 8px; margin: 20px; color: #cc0000;">
                            <h3>⚠️ Erro ao carregar dados</h3>
                            <p>Mensagem: ${error.message}</p>
                            <p style="font-size: 12px; color: #999;">Tente recarregar a página.</p>
                        </div>
                    `;
                }
            }
        }


        /* ============================================================
           MELHORIAS V4 — tema, "agora", chips, índice, frescor, troca
           ============================================================ */

        const ROTULOS_PERIODO = {
            manha: 'Manhã', tarde: 'Tarde', noite: 'Noite',
            sobreaviso: 'Sobreaviso', '24h': '24h', outro: 'Outro'
        };

        function diaAtivo() {
            const btn = document.querySelector('.date-btn.active');
            return btn ? btn.getAttribute('data-dia') : 'atual';
        }

        function minutosDe(hhmm) {
            const partes = hhmm.trim().split(':');
            const h = parseInt(partes[0], 10);
            const m = parseInt(partes[1] || '0', 10);
            if (isNaN(h) || isNaN(m)) return null;
            return h * 60 + m;
        }

        // Marca quem está de plantão AGORA (só faz sentido no dia "atual")
        function marcarAgora() {
            const agora = new Date();
            const agoraMin = agora.getHours() * 60 + agora.getMinutes();
            const ehHoje = diaAtivo() === 'atual';

            document.querySelectorAll('.profissional').forEach(prof => {
                prof.classList.remove('plantao-agora', 'plantao-encerrado');
                const pill = prof.querySelector('.agora-pill');
                if (pill) pill.remove();
                if (!ehHoje) return;

                const hora = prof.getAttribute('data-hora') || '';
                if (!hora.includes('/')) return;
                const [entradaStr, saidaStr] = hora.split('/');
                const entrada = minutosDe(entradaStr);
                const saida = minutosDe(saidaStr);
                if (entrada === null || saida === null) return;

                let emServico = false;
                let encerrado = false;
                if (entrada === saida) {
                    emServico = true; // plantão de 24h
                } else if (saida < entrada) {
                    // vira a madrugada (ex: 19:00/07:00)
                    emServico = agoraMin >= entrada || agoraMin < saida;
                } else {
                    emServico = agoraMin >= entrada && agoraMin < saida;
                    encerrado = agoraMin >= saida;
                }

                if (emServico) {
                    prof.classList.add('plantao-agora');
                    const info = prof.querySelector('.profissional-info');
                    if (info && !info.querySelector('.agora-pill')) {
                        const span = document.createElement('span');
                        span.className = 'agora-pill';
                        span.textContent = 'Agora';
                        info.appendChild(span);
                    }
                } else if (encerrado) {
                    prof.classList.add('plantao-encerrado');
                }
            });
        }

        // Chips de filtro por período, com contagens do dia visível
        function renderizarChips() {
            const el = document.getElementById('filter-chips');
            if (!el) return;
            const contagens = { manha: 0, tarde: 0, noite: 0, sobreaviso: 0, '24h': 0 };
            let agoraCount = 0;
            document.querySelectorAll('.profissional').forEach(prof => {
                const g = grupoDoTipo(tipoDoProf(prof));
                if (contagens[g] !== undefined) contagens[g]++;
                if (prof.classList.contains('plantao-agora')) agoraCount++;
            });

            let html = `<button class="filter-chip${filtroPeriodo === '' ? ' active' : ''}" data-filtro="" onclick="definirFiltroPeriodo('')">Todos</button>`;
            if (agoraCount > 0) {
                html += `<button class="filter-chip${filtroPeriodo === 'agora' ? ' active' : ''}" data-filtro="agora" onclick="definirFiltroPeriodo('agora')"><span class="chip-dot"></span>Agora · ${agoraCount}</button>`;
            }
            ['manha', 'tarde', 'noite', 'sobreaviso', '24h'].forEach(g => {
                if (contagens[g] > 0) {
                    html += `<button class="filter-chip${filtroPeriodo === g ? ' active' : ''}" data-filtro="${g}" onclick="definirFiltroPeriodo('${g}')">${ROTULOS_PERIODO[g]} · ${contagens[g]}</button>`;
                }
            });
            el.innerHTML = html;
        }

        // Dropdown "Ir para setor" (compacto, sem scroll horizontal)
        function renderizarSetorIndex(porSetor, setoresVisiveis) {
            const el = document.getElementById('setor-index');
            if (!el) return;
            const options = setoresVisiveis.map(setor => {
                const n = (porSetor[setor] || []).length;
                const nomeCurto = setor.replace(/\\s*[-–]\\s*(Sobreaviso|Plantão|Plantao|Escala).*$/i, '').trim();
                return `<option value="${setor.replace(/"/g, '&quot;')}">${nomeCurto} (${n})</option>`;
            }).join('');
            el.innerHTML = `<option value="">Ir para setor…</option>` + options;
        }

        function irParaSetor(setor) {
            const alvo = Array.from(document.querySelectorAll('.category')).find(cat => {
                const nome = cat.querySelector('.setor-nome-full');
                return nome && nome.textContent === setor;
            });
            if (!alvo) return;
            alvo.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        // Chip "próxima troca de plantão" (07h / 13h / 19h)
        function atualizarProximaTroca() {
            const el = document.getElementById('proxima-troca');
            if (!el) return;
            const TROCAS = [7 * 60, 13 * 60, 19 * 60];
            const agora = new Date();
            const agoraMin = agora.getHours() * 60 + agora.getMinutes();
            let proxima = TROCAS.find(t => t > agoraMin);
            let delta;
            if (proxima === undefined) {
                proxima = TROCAS[0];
                delta = (24 * 60 - agoraMin) + proxima;
            } else {
                delta = proxima - agoraMin;
            }
            const h = Math.floor(delta / 60);
            const m = delta % 60;
            const quando = h > 0 ? `${h}h${String(m).padStart(2, '0')}` : `${m} min`;
            el.innerHTML = `<svg class="ic" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg> Próxima troca às ${String(proxima / 60).padStart(2, '0')}:00 · em ${quando}`;
            el.hidden = false;
        }

        // Selo de frescor: verde se os dados são de hoje, vermelho caso contrário
        function atualizarFrescor() {
            const stamp = document.getElementById('freshness-stamp');
            const statusText = document.getElementById('status-text');
            if (!stamp || !statusText || !escalas) return;
            const dataAtu = escalas.data_atualizacao || escalas.data_backup ||
                            (escalas.atual && escalas.atual.data_simples) || '';
            if (!statusText.textContent && dataAtu) {
                const horaAtu = escalas.hora_atualizacao || escalas.hora_backup || '';
                statusText.textContent = horaAtu ? `Atualizado em ${dataAtu} às ${horaAtu}` : `Atualizado em ${dataAtu}`;
            }
            const hoje = new Date();
            const hojeStr = String(hoje.getDate()).padStart(2, '0') + '/' +
                            String(hoje.getMonth() + 1).padStart(2, '0') + '/' + hoje.getFullYear();
            stamp.classList.remove('fresco', 'velho');
            if (dataAtu === hojeStr) {
                stamp.classList.add('fresco');
            } else if (dataAtu) {
                stamp.classList.add('velho');
                statusText.textContent = `⚠️ Dados de ${dataAtu} — atualização pode ter falhado`;
            }
        }

        // Tema claro/escuro (segue o sistema por padrão; toggle persiste)
        const SVG_SOL = `<svg class="ic" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`;
        const SVG_LUA = `<svg class="ic" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
        function aplicarTema(tema) {
            document.documentElement.setAttribute('data-theme', tema);
            const btn = document.getElementById('btn-theme');
            if (btn) btn.innerHTML = tema === 'dark' ? SVG_SOL : SVG_LUA;
            const btnM = document.querySelector('#btn-theme-mobile .bb-icon');
            if (btnM) btnM.innerHTML = tema === 'dark' ? SVG_SOL : SVG_LUA;
        }

        function alternarTema() {
            const atual = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
            const novo = atual === 'dark' ? 'light' : 'dark';
            localStorage.setItem('tema', novo);
            aplicarTema(novo);
        }

        function iniciarTema() {
            // Padrão é SEMPRE claro; escuro só se o usuário escolheu no toggle
            aplicarTema(localStorage.getItem('tema') === 'dark' ? 'dark' : 'light');
        }

        // Modo compacto (densidade)
        function alternarCompacto() {
            const ativo = document.body.classList.toggle('compacto');
            localStorage.setItem('compacto', ativo ? '1' : '0');
            const btn = document.getElementById('btn-compacto');
            if (btn) btn.title = ativo ? 'Voltar ao modo normal' : 'Alternar modo compacto (mais setores por tela)';
        }

        function focarBusca() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
            setTimeout(() => document.getElementById('search').focus(), 350);
        }


        // Pós-render: tudo que depende do DOM das categorias
        function aposRenderizar(porSetor, setoresVisiveis) {
            marcarAgora();
            renderizarChips();
            renderizarSetorIndex(porSetor, setoresVisiveis);
            atualizarProximaTroca();
            atualizarFrescor();
            if (filtroPeriodo || document.getElementById('search').value) filtrarProfissionais();
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

        // Autenticar: aceita a senha geral OU os 4 últimos dígitos do telefone
        // de qualquer profissional cadastrado (preserva o hábito antigo de login).
        function autenticarOutro() {
          const input = document.getElementById('auth-input-outro').value.trim();
          const errorMsg = document.getElementById('auth-error-outro');
          const senhaCorreta = 'HRO-ALVF';

          if (!input) {
            errorMsg.textContent = 'Digite os 4 dígitos do telefone ou a senha';
            errorMsg.classList.add('show');
            return;
          }

          // Aceita a senha geral (case-insensitive) ...
          const senhaOk = input.toLowerCase() === senhaCorreta.toLowerCase();
          // ... ou os 4 últimos dígitos de algum profissional cadastrado.
          const digitos = input.replace(/\D/g, '');
          const last4Ok = digitos.length === 4 && (profissionaisData.professionals || []).some(
            prof => (prof.last4 || '') === digitos
          );

          if (senhaOk || last4Ok) {
            localStorage.setItem('authenticated', 'true');
            localStorage.setItem('auth_user', senhaOk ? 'admin' : digitos);
            document.getElementById('auth-modal').classList.add('hidden');
            document.getElementById('main-content').classList.remove('blurred');
            errorMsg.classList.remove('show');
          } else {
            errorMsg.textContent = 'Telefone ou senha não reconhecidos';
            errorMsg.classList.add('show');
            document.getElementById('auth-input-outro').value = '';
          }
        }

        // Verifica autenticação ao carregar
        function verificarAutenticacao() {
          // Verificar se já foi autenticado
          if (localStorage.getItem('authenticated') === 'true') {
            // Já foi autenticado, esconder modal e mostrar dashboard
            document.getElementById('auth-modal').classList.add('hidden');
            document.getElementById('main-content').classList.remove('blurred');
          } else {
            // Não foi autenticado, mostrar modal
            document.getElementById('auth-modal').classList.remove('hidden');
            document.getElementById('main-content').classList.add('blurred');
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
            const telefoneLimpo = (prof.phone || '').replace(/\D/g, '');
            const temTelefone = telefoneLimpo.length >= 10;
            const whatsappUrl = `https://wa.me/55${telefoneLimpo}`;
            const infoHtml = temTelefone
              ? `<a href="${whatsappUrl}" target="_blank" class="contact-phone">${prof.phone}</a>`
              : `<span class="contact-phone-vazio">Sem telefone cadastrado</span>`;
            return `
              <div class="contact-item">
                <div class="contact-name">${prof.name}</div>
                <div class="contact-info">${infoHtml}</div>
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

        // Tooltip positioning for WhatsApp icons
        function setupPhoneTooltips() {
            const phoneButtons = document.querySelectorAll('.telefone-icon-btn');
            phoneButtons.forEach(btn => {
                // Create tooltip element
                const tooltip = document.createElement('div');
                tooltip.className = 'phone-tooltip';
                tooltip.textContent = btn.getAttribute('data-phone');
                document.body.appendChild(tooltip);

                // Create arrow element
                const arrow = document.createElement('div');
                arrow.className = 'phone-tooltip-arrow';
                document.body.appendChild(arrow);

                // Position tooltip on hover
                btn.addEventListener('mouseenter', (e) => {
                    const rect = btn.getBoundingClientRect();
                    const tooltipWidth = 120; // Approximate width
                    const tooltipHeight = 40; // Approximate height

                    let left = rect.left + rect.width / 2 - tooltipWidth / 2;
                    let top = rect.top - tooltipHeight - 15;

                    // Adjust if tooltip goes off-screen horizontally
                    if (left < 10) {
                        left = 10;
                    } else if (left + tooltipWidth > window.innerWidth - 10) {
                        left = window.innerWidth - tooltipWidth - 10;
                    }

                    // Adjust if tooltip goes off-screen vertically
                    if (top < 10) {
                        top = rect.bottom + 10;
                        arrow.style.transform = 'rotate(180deg)';
                    } else {
                        arrow.style.transform = 'rotate(0deg)';
                    }

                    tooltip.style.left = left + 'px';
                    tooltip.style.top = top + 'px';
                    tooltip.classList.add('show');

                    arrow.style.left = (rect.left + rect.width / 2) + 'px';
                    arrow.style.top = (top + (top < rect.top - 10 ? 40 : -10)) + 'px';
                    arrow.classList.add('show');
                });

                btn.addEventListener('mouseleave', () => {
                    tooltip.classList.remove('show');
                    arrow.classList.remove('show');
                });
            });
        }

        // Global error handler
        window.addEventListener('error', function(event) {
            console.error('❌ GLOBAL ERROR:', event.message);
            console.error('Source:', event.filename, 'Line:', event.lineno, 'Column:', event.colno);
            console.error('Error object:', event.error);
        });

        // Setup tooltips after page loads
        try {
            console.log('📍 Iniciando setup...');
            setupPhoneTooltips();
            console.log('✅ Tooltips configurados');
        } catch (e) {
            console.error('❌ Erro ao configurar tooltips:', e.message);
        }

        // Aguardar DOM estar completamente carregado antes de verificar autenticação
        document.addEventListener('DOMContentLoaded', function() {
            // Tema e densidade (antes de renderizar, para evitar flash)
            try {
                iniciarTema();
                if (localStorage.getItem('compacto') === '1') {
                    document.body.classList.add('compacto');
                }
            } catch (e) {
                console.error('❌ Erro ao aplicar tema:', e.message);
            }

            // Verifica antes de renderizar
            try {
                console.log('📍 Verificando autenticação...');
                verificarAutenticacao();
                console.log('✅ Autenticação verificada');
            } catch (e) {
                console.error('❌ Erro ao verificar autenticação:', e.message);
            }

            // Renderizar escala
            try {
                console.log('📍 Iniciando renderização...');
                renderizarEscala();
                console.log('✅ Renderização concluída');
            } catch (e) {
                console.error('❌ Erro ao renderizar escala:', e.message);
                console.error('Stack:', e.stack);
            }

            // Atualiza "agora" e a contagem de troca a cada minuto
            setInterval(function() {
                try {
                    marcarAgora();
                    renderizarChips();
                    atualizarProximaTroca();
                    if (filtroPeriodo === 'agora') filtrarProfissionais();
                } catch (e) { /* silencioso */ }
            }, 60000);
        });

    </script>

    </div> <!-- Fecha main-content -->

    <!-- Rodapé -->
    <footer class="app-footer">
        <p class="footer-title">Escala Médica HRO</p>
        <p class="footer-text" id="footer-credit">ALVF - HRO - Todos os direitos reservados</p>
    </footer>

</body>
<script>
    // ==================== EASTER EGG ====================
    document.addEventListener('DOMContentLoaded', function() {
        const footerCredit = document.getElementById('footer-credit');
        let isShowing = false;

        footerCredit.addEventListener('click', function() {
            if (!isShowing) {
                footerCredit.textContent = 'Desenvolvido por @joaohperes';
                isShowing = true;
            } else {
                footerCredit.textContent = 'ALVF - HRO - Todos os direitos reservados';
                isShowing = false;
            }
        });
    });
</script>
</html>"""

    # Substituir placeholder de profissionais com dados reais
    profissionais_json_str = json.dumps(profissionais_data)
    html = html.replace('PROFISSIONAIS_JSON', profissionais_json_str)
    html = html.replace('VERSAO_GERACAO', datetime.now().strftime('%Y%m%d_%H%M%S'))

    # Salvar arquivo em múltiplos locais para garantir que seja atualizado
    output_files = [
        '/tmp/dashboard_executivo.html',
        str(Path(__file__).parent / 'index.html'),
        str(Path(__file__).parent / 'docs' / 'index.html')
    ]

    for output_file in output_files:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ Dashboard salvo: {output_file}")
        except Exception as e:
            print(f"⚠️  Erro ao salvar {output_file}: {e}")

    print(f"✅ Dashboard executivo criado com sucesso!")
    if ramais_data and mapping_data:
        print(f"📞 Funcionalidade de ramais integrada com sucesso!")

if __name__ == '__main__':
    gerar_dashboard()
