"""Testes da lógica pura do dashboard (classificação de turnos e ramais)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dashboard_logic import (
    obter_tipo_turno,
    normalizar_turno,
    obter_ramais_setor,
    formatar_ramais_display,
)


class TestObterTipoTurno:
    def test_vazio_retorna_outro(self):
        assert obter_tipo_turno("") == "outro"
        assert obter_tipo_turno(None) == "outro"

    def test_noturno_por_horario_19h(self):
        # 19:00/00:00 é noturno, NÃO 24h (caso das residências)
        assert obter_tipo_turno("Plantão", "19:00/00:00") == "noturno"
        assert obter_tipo_turno("Plantão", "19:00/07:00") == "noturno"
        assert obter_tipo_turno("Rotina", "20:00/06:00") == "noturno"

    def test_entrada_igual_saida_e_24h(self):
        assert obter_tipo_turno("Plantão", "07:00/07:00") == "badge-24h"
        assert obter_tipo_turno("Oncall", "13:00/13:00") == "badge-24h"

    def test_sobreaviso_explicito_e_24h(self):
        assert obter_tipo_turno("Sobreaviso 24h", "08:00/12:00") == "badge-24h"

    def test_diurno_residencia(self):
        assert obter_tipo_turno("Plantão", "07:00/19:00") == "diurno"

    def test_sobreaviso_com_periodo(self):
        assert obter_tipo_turno("Sobreaviso Matutino", "") == "matutino"
        assert obter_tipo_turno("Sobreaviso Cirurgia", "") == "sobreaviso"

    def test_final_de_semana_retorna_periodo(self):
        assert obter_tipo_turno("Rotina Vespertino - Final de Semana", "") == "vespertino"

    def test_periodos_por_palavra_chave(self):
        assert obter_tipo_turno("Plantão Matutino", "") == "matutino"
        assert obter_tipo_turno("Plantão Vespertino", "") == "vespertino"
        assert obter_tipo_turno("Plantão Noturno", "") == "noturno"

    def test_fallback_por_horario(self):
        assert obter_tipo_turno("Ambulatório", "08:00/12:00") == "matutino"
        assert obter_tipo_turno("Ambulatório", "13:00/17:00") == "vespertino"

    def test_horario_invalido_nao_quebra(self):
        # horário malformado não levanta exceção; cai na palavra-chave 'plantão'
        assert obter_tipo_turno("Plantão XYZ", "abc/def") == "plantao"
        assert obter_tipo_turno("Ambulatório", "abc/def") == "outro"


class TestNormalizarTurno:
    def test_vazio(self):
        assert normalizar_turno("") == (99, "Outro")
        assert normalizar_turno(None) == (99, "Outro")

    def test_ordem_cronologica(self):
        ordem_m, _ = normalizar_turno("Plantão Matutino")
        ordem_v, _ = normalizar_turno("Plantão Vespertino")
        ordem_n, _ = normalizar_turno("Plantão Noturno")
        ordem_r, _ = normalizar_turno("Rotina")
        ordem_s, _ = normalizar_turno("Sobreaviso")
        assert ordem_m < ordem_v < ordem_n < ordem_r < ordem_s

    def test_hospitalista_comanejo(self):
        assert normalizar_turno("Hospitalista Comanejo Matutino") == (1, "Comanejo Matutino")
        assert normalizar_turno("Hospitalista Urgência Noturno") == (3, "Urgência Noturno")

    def test_sobreaviso_neurologia_vs_neurocirurgia(self):
        # regressão: 'neurocirurgia' precisa ser checado antes de 'neurologia'
        assert normalizar_turno("Sobreaviso Neurocirurgia") == (5, "Sobreaviso Neurocirurgia")
        assert normalizar_turno("Sobreaviso Neurologia") == (5, "Sobreaviso Neurologia")

    def test_desconhecido_preserva_original(self):
        assert normalizar_turno("Turno Exótico") == (99, "Turno Exótico")


class TestRamais:
    RAMAIS = {'departments': [
        {'name': 'UTI Geral', 'extensions': ['2201', '2202']},
        {'name': 'Emergência', 'extensions': ['2100']},
    ]}
    MAPPING = {'sector_mappings': [
        {'dashboard_sector': 'UTI', 'ramais_departments': ['UTI Geral', 'Emergência']},
    ]}

    def test_obter_ramais_setor(self):
        assert obter_ramais_setor('UTI', self.RAMAIS, self.MAPPING) == ['2201', '2202', '2100']

    def test_setor_sem_mapeamento(self):
        assert obter_ramais_setor('Inexistente', self.RAMAIS, self.MAPPING) == []

    def test_dados_ausentes(self):
        assert obter_ramais_setor('UTI', None, self.MAPPING) == []

    def test_formatar_vazio(self):
        assert formatar_ramais_display([]) == ""

    def test_formatar_remove_duplicatas(self):
        out = formatar_ramais_display(['2201', '2201', '2202'])
        assert out.count('2201') == 1
        assert '2202' in out

    def test_formatar_limita_a_5(self):
        exts = [str(2200 + i) for i in range(8)]
        out = formatar_ramais_display(exts)
        assert '...' in out
