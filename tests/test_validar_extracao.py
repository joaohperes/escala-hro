"""Testes da validação de sanidade pós-extração."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import validar_extracao
from validar_extracao import contar_registros


def _janela(n, data_simples=None):
    regs = [{"nome": f"Prof {i}"} for i in range(n)]
    bloco = {"registros": regs, "total": n}
    if data_simples:
        bloco["data_simples"] = data_simples
    return {"atual": bloco}


class TestContarRegistros:
    def test_conta_atual(self):
        assert contar_registros(_janela(5)) == 5

    def test_estruturas_vazias(self):
        assert contar_registros({}) == 0
        assert contar_registros(None) == 0
        assert contar_registros({"atual": None}) == 0
        assert contar_registros({"atual": {"registros": None}}) == 0


class TestMain:
    def _rodar(self, tmp_path, monkeypatch, extracao=None, baseline=None):
        ext = tmp_path / "extracao.json"
        base = tmp_path / "baseline.json"
        if extracao is not None:
            ext.write_text(json.dumps(extracao), encoding="utf-8")
        if baseline is not None:
            base.write_text(json.dumps(baseline), encoding="utf-8")
        monkeypatch.setattr(validar_extracao, "EXTRACAO", ext)
        monkeypatch.setattr(validar_extracao, "BASELINE", base)
        return validar_extracao.main()

    def test_arquivo_ausente_falha(self, tmp_path, monkeypatch):
        assert self._rodar(tmp_path, monkeypatch) == 1

    def test_poucos_registros_falha(self, tmp_path, monkeypatch):
        assert self._rodar(tmp_path, monkeypatch, extracao=_janela(3)) == 1

    def test_extracao_saudavel_passa(self, tmp_path, monkeypatch):
        hoje = validar_extracao.datetime.now(validar_extracao.BRT).strftime("%d/%m/%Y")
        rc = self._rodar(tmp_path, monkeypatch,
                         extracao=_janela(100, hoje), baseline=_janela(105))
        assert rc == 0

    def test_queda_brusca_falha(self, tmp_path, monkeypatch):
        hoje = validar_extracao.datetime.now(validar_extracao.BRT).strftime("%d/%m/%Y")
        rc = self._rodar(tmp_path, monkeypatch,
                         extracao=_janela(30, hoje), baseline=_janela(100))
        assert rc == 1

    def test_data_velha_falha(self, tmp_path, monkeypatch):
        rc = self._rodar(tmp_path, monkeypatch,
                         extracao=_janela(100, "01/01/2020"), baseline=_janela(100))
        assert rc == 1
