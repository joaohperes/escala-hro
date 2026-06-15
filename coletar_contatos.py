#!/usr/bin/env python3
"""
PENTE-FINO de contatos — varre vários dias da escala (com o filtro de contato
ligado) acumulando contatos únicos e faz merge em profissionais_autenticacao.json.

- Reaproveita ExtractorInteligente (login, iframe, filtro de contato, extrair_dia).
- Navega para o próximo dia clicando na seta ">" do cabeçalho de data.
- Merge: preenche telefone/email de quem falta e cadastra profissionais novos.
  NUNCA sobrescreve um telefone já existente na base.

Uso:
    ESCALA_BROWSER=safari python3 coletar_contatos.py [num_dias]   # padrão 14
    ESCALA_BROWSER=safari python3 coletar_contatos.py 14 --dry-run # só relatório
"""
import os
import sys
import json
import time
import unicodedata
from datetime import datetime

os.environ.setdefault('ESCALA_BROWSER', 'safari')

from selenium.webdriver.common.by import By
from extracao_inteligente import ExtractorInteligente, corrigir_portugues

BASE = os.path.dirname(os.path.abspath(__file__))
PROF_FILE = os.path.join(BASE, 'profissionais_autenticacao.json')


def norm(n):
    n = ''.join(c for c in unicodedata.normalize('NFKD', n or '') if not unicodedata.combining(c))
    return ' '.join(n.lower().split())


def last4(phone):
    digs = ''.join(ch for ch in (phone or '') if ch.isdigit())
    return digs[-4:] if len(digs) >= 4 else ''


def navegar_proximo_dia(driver):
    """Clica na seta '>' do cabeçalho de data. Retorna a data textual após clicar."""
    antes = driver.execute_script(r"""
      for(var e of document.querySelectorAll('*')){
        if(e.childElementCount===0){var t=(e.textContent||'').trim();
          if(/^\d{1,2}\s+[A-Za-zçÇ]+\s+\d{4}$/.test(t)) return t;}
      }
      return null;
    """)
    # clica no elemento '>' mais próximo do texto da data
    driver.execute_script(r"""
      var cands=[];
      for(var e of document.querySelectorAll('button,span,div,i,svg,a')){
        var t=(e.textContent||'').trim();
        var aria=(e.getAttribute('aria-label')||'');
        if(t==='>'||/next|forward|chevron.?right|arrow.?right|proxim/i.test(aria)){ cands.push(e); }
      }
      if(cands.length){ cands[cands.length-1].click(); }
    """)
    time.sleep(4)
    depois = driver.execute_script(r"""
      for(var e of document.querySelectorAll('*')){
        if(e.childElementCount===0){var t=(e.textContent||'').trim();
          if(/^\d{1,2}\s+[A-Za-zçÇ]+\s+\d{4}$/.test(t)) return t;}
      }
      return null;
    """)
    return antes, depois


def main():
    num_dias = 14
    dry_run = '--dry-run' in sys.argv
    for a in sys.argv[1:]:
        if a.isdigit():
            num_dias = int(a)

    print("=" * 80)
    print(f"📞 PENTE-FINO DE CONTATOS — varrendo {num_dias} dia(s)")
    print("=" * 80)

    extractor = ExtractorInteligente(headless=False)
    contatos = {}  # norm -> {name, phone, email, setor}
    try:
        extractor.login()
        extractor.driver.get("https://escala.med.br/painel/#!/day_grid")
        time.sleep(5)
        frames = extractor.driver.find_elements(By.TAG_NAME, "iframe")
        if frames:
            extractor.driver.switch_to.frame(frames[0])

        extractor.ativar_filtro_contato()

        for dia in range(num_dias):
            res = extractor.extrair_dia()
            regs = res.get('registros', [])
            novos_no_dia = 0
            for r in regs:
                k = norm(r.get('profissional'))
                if not k:
                    continue
                if k not in contatos:
                    contatos[k] = {
                        'name': (r.get('profissional') or '').strip(),
                        'phone': r.get('phone', ''),
                        'email': r.get('email', ''),
                        'setor': corrigir_portugues(r.get('setor', '')),
                    }
                    novos_no_dia += 1
                else:
                    if not contatos[k]['phone'] and r.get('phone'):
                        contatos[k]['phone'] = r['phone']
                    if not contatos[k]['email'] and r.get('email'):
                        contatos[k]['email'] = r['email']
            print(f"  📅 {res.get('data','?'):<22} | {len(regs):3d} reg | +{novos_no_dia} pessoas novas (total únicos: {len(contatos)})")

            if dia < num_dias - 1:
                antes, depois = navegar_proximo_dia(extractor.driver)
                if antes == depois:
                    print(f"  ⚠️  Navegação não avançou ({depois}); encerrando varredura.")
                    break
    finally:
        extractor.close()

    # ===== VALIDAÇÃO DE CONFIANÇA =====
    # O site às vezes faz um card herdar o contato de um vizinho na mesma coluna
    # (mesmo telefone/email aparece em 2 pessoas diferentes). Esses são ambíguos:
    # descartamos para não gravar contato trocado.
    from collections import Counter
    tel_count = Counter(v['phone'] for v in contatos.values() if v['phone'])
    mail_count = Counter(v['email'].lower() for v in contatos.values() if v['email'])

    suspeitos = []
    for k, v in contatos.items():
        tel_ok = v['phone'] and tel_count[v['phone']] == 1
        mail_ok = (not v['email']) or mail_count[v['email'].lower()] == 1
        if v['phone'] and not (tel_ok and mail_ok):
            suspeitos.append(v)
            v['_ambiguo'] = True

    if suspeitos:
        print(f"⚠️  {len(suspeitos)} contato(s) AMBÍGUO(S) descartado(s) (telefone/email compartilhado):")
        for v in suspeitos:
            print(f"   - {v['name']:<38} {v['phone']} / {v['email']}")
        print()

    com_tel = {k: v for k, v in contatos.items() if v['phone'] and not v.get('_ambiguo')}
    print(f"📊 Coletados {len(contatos)} únicos | {len(com_tel)} com telefone confiável.\n")

    # ===== MERGE =====
    with open(PROF_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    profs = data['professionals']
    idx = {norm(p['name']): p for p in profs}

    preenchidos, adicionados = [], []
    for k, v in sorted(com_tel.items(), key=lambda kv: kv[1]['name']):
        if k in idx:
            if not idx[k].get('phone'):
                idx[k]['phone'] = v['phone']
                idx[k]['email'] = idx[k].get('email') or v['email']
                idx[k]['last4'] = last4(v['phone'])
                preenchidos.append(v)
        else:
            profs.append({
                'name': v['name'],
                'email': v['email'],
                'phone': v['phone'],
                'last4': last4(v['phone']),
            })
            adicionados.append(v)

    print(f"📞 Preenchidos (cadastrados sem telefone): {len(preenchidos)}")
    for v in preenchidos:
        print(f"   - {v['name']:<38} {v['phone']}")
    print(f"\n🆕 Novos cadastrados: {len(adicionados)}")
    for v in adicionados:
        print(f"   - {v['name']:<38} {v['phone']}")

    if dry_run:
        print("\n🔸 --dry-run: nenhuma alteração salva.")
        return 0

    if preenchidos or adicionados:
        with open(PROF_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Base atualizada: {PROF_FILE} (agora {len(profs)} profissionais)")
    else:
        print("\n✅ Nada a atualizar — base já completa para os dias varridos.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
