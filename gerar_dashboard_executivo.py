#!/usr/bin/env python3
"""
Dashboard Executivo - Visual Premium
Com banner ALVF e design sofisticado
"""

import json
from datetime import datetime

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

    # DIA / NOITE (Residência)
    if turno == 'dia':
        return (1, "Período Diurno")
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

    try:
        with open('/tmp/escalas_multiplos_dias.json', 'r', encoding='utf-8') as f:
            escalas = json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo de escalas não encontrado.")
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

        /* Header com banner */
        .header-banner {
            background: linear-gradient(135deg, #0d3b66 0%, #1a5f8f 100%);
            padding: 30px 20px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        }

        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 30px;
            flex-wrap: wrap;
        }

        .header-logo {
            font-family: 'Merriweather', serif;
            color: white;
            font-size: 2.5em;
            font-weight: 700;
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        .header-info {
            color: white;
            text-align: left;
        }

        .header-info h2 {
            font-family: 'Merriweather', serif;
            font-size: 1.8em;
            font-weight: 700;
            margin-bottom: 5px;
            letter-spacing: 0.5px;
        }

        .header-info p {
            font-size: 0.95em;
            opacity: 0.95;
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

        /* Estatísticas */
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            border-left: 4px solid #0d3b66;
            text-align: center;
        }

        .stat-number {
            font-size: 2.8em;
            font-weight: 700;
            color: #0d3b66;
            margin-bottom: 8px;
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
        }

        .categoria-header.expanded .categoria-toggle {
            transform: rotate(180deg);
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
            background: linear-gradient(135deg, #f8fbff 0%, #f0f5fa 100%);
            border-radius: 10px;
            padding: 18px;
            border: 1px solid #e8eef7;
            transition: all 0.3s ease;
        }

        .turno-coluna:hover {
            border-color: #0d3b66;
            box-shadow: 0 4px 12px rgba(13, 59, 102, 0.1);
        }

        .turno-title {
            font-weight: 700;
            color: #0d3b66;
            margin-bottom: 15px;
            padding-bottom: 12px;
            border-bottom: 2px solid #0d3b66;
            text-align: center;
            font-size: 0.95em;
            letter-spacing: 0.3px;
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

        /* Responsivo */
        @media (max-width: 768px) {
            .header-content {
                flex-direction: column;
                text-align: center;
                gap: 15px;
            }

            .header-logo {
                font-size: 2em;
            }

            .header-info {
                text-align: center;
            }

            .header-info h2 {
                font-size: 1.4em;
            }

            .controls-bar {
                flex-direction: column;
                align-items: stretch;
            }

            .search-section {
                min-width: auto;
            }

            .action-buttons {
                width: 100%;
            }

            .action-buttons .btn {
                flex: 1;
            }

            .turnos-container {
                grid-template-columns: 1fr;
            }

            .stats {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- Header com Banner -->
    <div class="header-banner">
        <div class="header-content">
            <div class="header-logo">ALVF</div>
            <div class="header-info">
                <h2>Escala Médica</h2>
                <p>Associação Hospitalar Lenoir Vargas Ferreira</p>
            </div>
        </div>
    </div>

    <!-- Container Principal -->
    <div class="container">
        <!-- Controles -->
        <div class="controls-bar">
            <div class="date-selector">
                <button class="date-btn" data-dia="anterior" onclick="selecionarDia('anterior')">← Anterior</button>
                <button class="date-btn active" data-dia="atual" onclick="selecionarDia('atual')">📅 Hoje</button>
            </div>
            <div class="search-section">
                <input type="text" class="search-input" id="search" placeholder="Busque por nome, setor, turno..." onkeyup="filtrarProfissionais()">
            </div>
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="expandirTodas()">Expandir</button>
                <button class="btn btn-secondary" onclick="colapsoTodas()">Fechar</button>
            </div>
        </div>

        <!-- Data selecionada -->
        <div class="date-display" id="data-selecionada"></div>

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
        function normalizarTurno(turnoText) {
            if (!turnoText) return { ordem: 99, nome: 'Outro' };

            const turno = turnoText.toLowerCase().trim();
            const turnoOriginal = turnoText.trim();

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

            // DIA / NOITE
            if (turno === 'dia') return { ordem: 1, nome: 'Período Diurno' };
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
                        const { ordem, nome } = normalizarTurno(turnoOriginal);

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
                                <div class="categoria-count">${profissionais.length} profissionais</div>
                            </div>
                            <div class="categoria-toggle">▼</div>
                        </div>
                        <div class="categoria-content">
                            <div class="turnos-container">
                                ${turnosOrdenados.map(turno => `
                                    <div class="turno-coluna">
                                        <div class="turno-title">${turno}</div>
                                        <div class="profissionais-list">
                                            ${porTurno[turno].map(prof => `
                                                <div class="profissional" data-search="${prof.profissional.toLowerCase()} ${setor.toLowerCase()} ${turno.toLowerCase()}">
                                                    <div class="profissional-nome">${prof.profissional}</div>
                                                    <div class="profissional-info">
                                                        <span class="info-label">Horário:</span> ${prof.horario}
                                                    </div>
                                                </div>
                                            `).join('')}
                                        </div>
                                    </div>
                                `).join('')}
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
                                <div class="categoria-count">${profissionais.length} profissionais</div>
                            </div>
                            <div class="categoria-toggle">▼</div>
                        </div>
                        <div class="categoria-content">
                            <div class="profissionais-list">
                                ${profissionais.map(prof => `
                                    <div class="profissional" data-search="${prof.profissional.toLowerCase()} ${setor.toLowerCase()}">
                                        <div class="profissional-nome">${prof.profissional}</div>
                                        <div class="profissional-info">
                                            <span class="info-label">Turno:</span> ${prof.tipo_turno}<br>
                                            <span class="info-label">Horário:</span> ${prof.horario}
                                        </div>
                                    </div>
                                `).join('')}
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

        function expandirTodas() {
            document.querySelectorAll('.categoria-header').forEach(h => {
                h.classList.add('expanded');
                h.nextElementSibling.classList.remove('collapsed');
            });
        }

        function colapsoTodas() {
            document.querySelectorAll('.categoria-header').forEach(h => {
                h.classList.remove('expanded');
                h.nextElementSibling.classList.add('collapsed');
            });
        }

        function filtrarProfissionais() {
            const searchText = document.getElementById('search').value.toLowerCase();
            const profissionais = document.querySelectorAll('.profissional');

            profissionais.forEach(prof => {
                const texto = prof.getAttribute('data-search');
                if (searchText === '' || texto.includes(searchText)) {
                    prof.style.display = 'block';
                } else {
                    prof.style.display = 'none';
                }
            });

            document.querySelectorAll('.category').forEach(category => {
                const content = category.querySelector('.categoria-content');
                const header = category.querySelector('.categoria-header');
                const vistos = content.querySelectorAll('.profissional[style*="display: block"]').length;

                if (searchText === '') {
                    category.style.display = 'block';
                } else {
                    if (vistos > 0) {
                        category.style.display = 'block';
                        content.classList.remove('collapsed');
                        header.classList.add('expanded');
                    } else {
                        category.style.display = 'none';
                    }
                }
            });
        }

        renderizarEscala();
    </script>
</body>
</html>"""

    # Salvar arquivo
    output_file = '/tmp/dashboard_executivo.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Dashboard executivo criado!")
    print(f"📍 Arquivo: {output_file}")

if __name__ == '__main__':
    gerar_dashboard()
