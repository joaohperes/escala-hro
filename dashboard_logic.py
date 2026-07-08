#!/usr/bin/env python3
"""
Lógica pura do dashboard (classificação de turnos, ramais).

Extraída de gerar_dashboard_executivo.py para permitir testes unitários
sem gerar HTML. Nenhuma função aqui tem efeito colateral além de prints.
"""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent


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
        # Check more specific terms FIRST to avoid substring matching issues
        # e.g., "neurologia" contains "ologia" which could match "urologia" check
        if 'neurocirurgia' in turno:
            return (5, "Sobreaviso Neurocirurgia")
        elif 'neurologia' in turno:
            return (5, "Sobreaviso Neurologia")
        elif 'cardiologia' in turno:
            return (5, "Sobreaviso Cardiologia")
        elif 'oftalmologia' in turno:
            return (5, "Sobreaviso Oftalmologia")
        elif 'urologia' in turno:
            return (5, "Sobreaviso Urologia")
        elif 'oncologia' in turno:
            return (5, "Sobreaviso Oncologia")
        elif 'endoscopia' in turno:
            return (5, "Sobreaviso Endoscopia")
        elif 'pediátrica' in turno or 'pediatrica' in turno:
            return (5, "Sobreaviso Cirurgia Pediátrica")
        elif 'vascular' in turno:
            return (5, "Sobreaviso Cirurgia Vascular")
        elif 'cirurgia' in turno:
            if 'equipe 1' in turno or ' 1' in turno:
                return (5, "Sobreaviso Cirurgia - Equipe 1")
            elif 'equipe 2' in turno or ' 2' in turno:
                return (5, "Sobreaviso Cirurgia - Equipe 2")
            return (5, "Sobreaviso Cirurgia")
        return (5, "Sobreaviso")

    # Plantão Diurno
    if 'plantão diurno' in turno:
        return (1, "Plantão Diurno")

    # Manter o original para casos não identificados
    return (99, turno_original)

def carregar_ramais_data(escala_data=None):
    """Carrega dados de ramais e mapeamento de setores

    Prioridade:
    1. Usar dados embutidos no arquivo de extração (escala_data)
    2. Carregar de arquivos individuais (ramais_hro.json e setor_ramais_mapping.json)
    """
    import os
    from pathlib import Path

    ramais_data = None
    mapping_data = None

    # PRIORIDADE 1: Procurar no arquivo de extração (novo comportamento)
    if escala_data:
        if 'ramais_hro' in escala_data:
            # Transformar array para estrutura esperada { departments: [...] }
            ramais_array = escala_data['ramais_hro']
            if isinstance(ramais_array, list):
                ramais_data = {'departments': ramais_array}
            else:
                ramais_data = ramais_array
            print(f"✅ Ramais carregados do arquivo de extração")
        if 'setor_ramais_mapping' in escala_data:
            mapping_array = escala_data['setor_ramais_mapping']
            if isinstance(mapping_array, list):
                mapping_data = {'sector_mappings': mapping_array}
            else:
                mapping_data = mapping_array
            print(f"✅ Mapeamento de setores carregado do arquivo de extração")

    # PRIORIDADE 2: Se não encontrou no arquivo de extração, carregar de arquivo separado
    if not ramais_data:
        ramais_paths = [
            BASE_DIR / 'ramais_hro.json',
            Path.cwd() / 'ramais_hro.json',
        ]

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

    if not mapping_data:
        mapping_paths = [
            BASE_DIR / 'setor_ramais_mapping.json',
            Path.cwd() / 'setor_ramais_mapping.json',
        ]

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

