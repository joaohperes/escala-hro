#!/usr/bin/env python3
"""
Validação de sanidade pós-extração.

Roda no workflow DEPOIS da extração/geração e ANTES do commit.
Objetivo: nunca publicar um dashboard vazio ou drasticamente menor que o
normal por causa de uma mudança silenciosa no layout do site de origem.

Regras:
1. O arquivo de extração precisa existir e ser JSON válido.
2. 'atual' precisa ter registros (> MINIMO_ABSOLUTO profissionais).
3. Se houver baseline (cache do dia anterior), a queda em relação a ela
   não pode passar de QUEDA_MAXIMA_PCT.
4. A data de 'atual' precisa ser a de hoje (fuso de Brasília).

Exit code 0 = ok para publicar; 1 = NÃO publicar (workflow falha e alerta).
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).parent
EXTRACAO = Path('/tmp/extracao_inteligente.json')
BASELINE = BASE_DIR / 'data' / 'extracao_inteligente_anterior_cache.json'

MINIMO_ABSOLUTO = 10      # menos que isso nunca é uma escala real do HRO
QUEDA_MAXIMA_PCT = 40     # queda > 40% vs baseline = suspeito

BRT = timezone(timedelta(hours=-3))


def contar_registros(dados, chave='atual'):
    bloco = (dados or {}).get(chave) or {}
    return len(bloco.get('registros') or [])


def main():
    erros = []
    avisos = []

    if not EXTRACAO.exists():
        print(f"❌ Arquivo de extração não encontrado: {EXTRACAO}")
        return 1

    try:
        dados = json.loads(EXTRACAO.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"❌ JSON inválido em {EXTRACAO}: {e}")
        return 1

    total = contar_registros(dados)
    print(f"📊 Registros extraídos (atual): {total}")

    # Regra 2: mínimo absoluto
    if total < MINIMO_ABSOLUTO:
        erros.append(
            f"Apenas {total} registros extraídos (mínimo: {MINIMO_ABSOLUTO}). "
            "Possível mudança de layout no site de origem ou falha de login."
        )

    # Regra 3: comparação com baseline
    if BASELINE.exists():
        try:
            baseline = json.loads(BASELINE.read_text(encoding='utf-8'))
            base_total = contar_registros(baseline)
            if base_total > 0:
                queda = (base_total - total) / base_total * 100
                print(f"📊 Baseline (cache anterior): {base_total} registros "
                      f"(variação: {-queda:+.1f}%)")
                if queda > QUEDA_MAXIMA_PCT:
                    erros.append(
                        f"Queda de {queda:.0f}% vs baseline "
                        f"({base_total} → {total} registros). "
                        f"Limite: {QUEDA_MAXIMA_PCT}%."
                    )
        except Exception as e:
            avisos.append(f"Baseline ilegível ({e}); pulando comparação.")
    else:
        avisos.append("Sem baseline para comparar (primeira execução?).")

    # Regra 4: data de 'atual' deve ser hoje (BRT)
    hoje = datetime.now(BRT).strftime('%d/%m/%Y')
    data_atual = ((dados.get('atual') or {}).get('data_simples') or '').strip()
    if data_atual and data_atual != hoje:
        erros.append(
            f"Data de 'atual' é {data_atual}, mas hoje é {hoje} (BRT). "
            "Extração pode ter pego dados velhos."
        )
    elif not data_atual:
        avisos.append("Campo data_simples ausente em 'atual'; data não verificada.")

    for a in avisos:
        print(f"⚠️  {a}")

    if erros:
        print("\n❌ VALIDAÇÃO FALHOU — dashboard NÃO deve ser publicado:")
        for e in erros:
            print(f"   • {e}")
        return 1

    print("\n✅ Validação de sanidade OK — seguro publicar.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
