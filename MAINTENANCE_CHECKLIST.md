# 🔧 MAINTENANCE & SAFETY CHECKLIST - ESCALA HRO

**Última atualização**: 17/11/2025
**Status**: PRODUÇÃO ESTÁVEL V1.0
**Versão**: Final - Sem mais mudanças estruturais

---

## ⚠️ REGRAS IMUTÁVEIS (NUNCA QUEBRAR!)

### 1. RAMAIS - FUNÇÃO FIXA CRÍTICA 🔴

**Status**: CRÍTICO - Se falhar, todo dashboard quebra

#### O que NÃO fazer:
- ❌ Remover `ramais_hro` do arquivo de extração
- ❌ Deixar ramais carregarem de arquivo separado APENAS
- ❌ Ignorar erro de validação "Ramais não foram embarcados"
- ❌ Assumir que ramais "ficam ali por si"

#### O que FAZER:
- ✅ SEMPRE embarcar `ramais_hro` e `setor_ramais_mapping` em `/tmp/extracao_inteligente.json`
- ✅ Validar ao final de `extracao_inteligente.py`:
  ```python
  assert 'ramais_hro' in output, "❌ ERRO CRÍTICO: Ramais não embarcados!"
  assert len(output['ramais_hro']) > 0, "❌ ERRO CRÍTICO: Ramais vazios!"
  print(f"✅ Validação PASSOU: {len(output['ramais_hro'])} ramais embarcados")
  ```
- ✅ Validar no dashboard que recebe os dados:
  ```python
  # Em gerar_dashboard_executivo.py
  if 'ramais_hro' not in escala_data:
      raise ValueError("ERRO: Ramais não encontrados na extração!")
  ```

#### Localização dos Ramais:
```
ramais_hro.json                          ← Fonte original (não muda)
setor_ramais_mapping.json                ← Mapeamento (não muda)
    ↓
extracao_inteligente.py                  ← EMBARCA aqui
    ↓
/tmp/extracao_inteligente.json           ← Contém ramais_hro (✅ crítico!)
    ↓
gerar_dashboard_executivo.py             ← Carrega daqui
    ↓
index.html                               ← Exibe no dashboard
```

---

### 2. DIA ANTERIOR - ROLLING WINDOW D-1 📅

**Status**: CRÍTICO - Se falhar, histórico fica quebrado

#### O que NÃO fazer:
- ❌ Deixar anterior com 2+ dias de diferença
- ❌ Assumir que "sempre vai estar atualizado"
- ❌ Não validar a data ao carregar cache
- ❌ Usar dados de 14 nov quando estamos em 17 nov

#### O que FAZER:
- ✅ Rolling window correto:
  ```
  Dia 17 de novembro (HOJE):
    - Extrai escalas de 17 nov
    - Carrega anterior de 16 nov (D-1) ← SEMPRE 1 dia atrás!

  Dia 18 de novembro (AMANHÃ):
    - Extrai escalas de 18 nov
    - Anterior será 17 nov (dados de hoje viram anterior amanhã)
  ```

- ✅ Validar em `extracao_inteligente.py`:
  ```python
  dias_diff = (hoje - data_anterior).days

  if dias_diff == 1:
      print(f"✅ CORRETO: Anterior é de exatamente 1 dia atrás")
      usar_cache()
  elif dias_diff == 2:
      print(f"⚠️  AVISO: Anterior é de 2 dias atrás (workflow perdido)")
      usar_fallback_e_alertar()
  elif dias_diff > 2:
      print(f"❌ ERRO: Anterior com {dias_diff} dias de diferença!")
      raise Exception("Cache muito antigo - impossível usar")
  ```

#### Cache Management:
```
Arquivo: data/extracao_inteligente_anterior_cache.json

Estrutura necessária:
{
  "atual": {
    "data": "17 novembro 2025",      ← Data de HOJE
    "registros": [...]
  },
  "anterior": {
    "data": "16 novembro 2025",      ← Data de ONTEM (D-1)
    "registros": [...]
  }
}

O que muda a cada dia:
- Dia 17: atual=17nov, anterior=16nov
- Dia 18: atual=18nov, anterior=17nov (dados do dia 17 movem para anterior)
- Dia 19: atual=19nov, anterior=18nov (dados do dia 18 movem para anterior)
```

---

### 3. AUTENTICAÇÃO - NUNCA REMOVER 🔐

**Status**: CRÍTICO - Protege dados

#### O que NÃO fazer:
- ❌ Auto-autenticar sem pedir login
- ❌ Permitir acesso ao dashboard sem verificação
- ❌ Remover o `sessionStorage.removeItem('authenticated')`

#### O que FAZER:
- ✅ Sempre exigir login:
  ```javascript
  // Início de cada carregamento
  sessionStorage.removeItem('authenticated');

  // Mostrar modal até autenticação válida
  if (sessionStorage.getItem('authenticated') !== 'true') {
      mostrar_auth_modal();
  }
  ```

---

## 📋 DAILY MAINTENANCE CHECKLIST

### A cada execução do workflow (GitHub Actions)

**Antes da extração:**
- [ ] Verificar que `ramais_hro.json` existe e não está vazio
- [ ] Verificar que `setor_ramais_mapping.json` existe e não está vazio
- [ ] Confirmar que `data/extracao_inteligente_anterior_cache.json` existe

**Durante a extração (`extracao_inteligente.py`):**
- [ ] Validação no final: Ramais embarcados? ✅
- [ ] Validação: Anterior tem data D-1? ✅
- [ ] Log mostra: `✅ Ramais embarcados: X departamentos`
- [ ] Log mostra: `✅ Data anterior: XX novembro 2025`

**Depois do dashboard (`gerar_dashboard_executivo.py`):**
- [ ] Verificar que ramais foram carregados: `✅ Ramais data loaded: 134 departments`
- [ ] Verificar que anterior está correto no HTML
- [ ] Testar no navegador: clique em "Ramais" → deve mostrar diretório com dados

**Antes do deploy:**
- [ ] `git diff` mostra APENAS alterações esperadas
- [ ] Sem `profissionais_autenticacao.json` sendo modificado sem razão
- [ ] Sem mudanças acidentais em `escalas_multiplos_dias.json`

---

## 🚨 SINAIS DE ALERTA - O QUE PROCURAR

### Ramais desapareceram:
```
❌ SINTOMA: "Dados de ramais não disponíveis" no modal
VERIFICAR:
1. /tmp/extracao_inteligente.json tem "ramais_hro"?
2. gerar_dashboard_executivo.py está pegando de lá?
3. HTML tem os dados injetados no JavaScript?
```

### Dia anterior com data errada:
```
❌ SINTOMA: Mostra "14 novembro" quando é dia 17
VERIFICAR:
1. data/extracao_inteligente_anterior_cache.json tem anterior correto?
2. Workflow rodou no dia 16 (ontem)?
3. Dias de diferença são exatamente 1?
```

### Dashboard não carrega:
```
❌ SINTOMA: Página fica vazia ou mostra erro
VERIFICAR:
1. AuthenticationModal está pedindo login?
2. Console tem erros de JavaScript?
3. sessionStorage foi limpo corretamente?
```

---

## 🔄 PROCEDIMENTO DE RECUPERAÇÃO

### Se Ramais sumirem:

1. **Verificar**:
   ```bash
   python3 << 'EOF'
   import json
   with open('/tmp/extracao_inteligente.json', 'r') as f:
       data = json.load(f)
   print(f"Ramais presentes? {'ramais_hro' in data}")
   print(f"Ramais count: {len(data.get('ramais_hro', []))}")
   EOF
   ```

2. **Se vazios ou faltando**:
   - Abrir `extracao_inteligente.py`
   - Procurar função `carregar_ramais_data()`
   - Verificar que está sendo chamada ANTES de salvar output
   - Verificar que dados estão sendo embarcados

3. **Se recuperado**:
   ```bash
   python3 gerar_dashboard_executivo.py
   git add -A && git commit -m "fix: Restore ramais to extraction output"
   git push origin main
   ```

### Se Dia Anterior estiver errado:

1. **Verificar**:
   ```bash
   python3 << 'EOF'
   import json
   with open('data/extracao_inteligente_anterior_cache.json', 'r') as f:
       data = json.load(f)
   print(f"Atual: {data['atual']['data']}")
   print(f"Anterior: {data['anterior']['data']}")
   EOF
   ```

2. **Se diferença > 1 dia**:
   - Workflow perdeu dias
   - Usar dados da última extração bem-sucedida
   - Atualizar manualmente:
     ```bash
     python3 atualizar_cache_anterior.py --data "16 novembro 2025"
     ```

3. **Se recuperado**:
   ```bash
   python3 gerar_dashboard_executivo.py
   git add -A && git commit -m "fix: Correct anterior date to D-1"
   git push origin main
   ```

---

## 📊 VERSÃO FINAL - IMUTÁVEL

```
╔════════════════════════════════════════════════════════╗
║                                                        ║
║   ESCALA HRO - VERSÃO FINAL ESTÁVEL                  ║
║                                                        ║
║   Status: ✅ PRONTO PARA PRODUÇÃO PERMANENTE         ║
║   Versão: 1.0 FINAL                                  ║
║   Data: 17/11/2025                                   ║
║                                                        ║
║   Funcionalidades Críticas:                           ║
║   ✅ Autenticação obrigatória (não remove)           ║
║   ✅ Ramais SEMPRE embarcados (função fixa)          ║
║   ✅ Dia anterior sempre D-1 (rolling window)        ║
║   ✅ 171 profissionais consolidados (sem duplicatas) ║
║   ✅ 134 ramais com 36 mapeamentos                   ║
║   ✅ Dashboard responsivo e minimalista              ║
║   ✅ Footer com easter-egg @joaohperes               ║
║   ✅ Status indicator verde/vermelho                 ║
║                                                        ║
║   PRÓXIMAS MUDANÇAS: NENHUMA!                         ║
║   (Apenas manutenção de dados e logs)                ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
```

---

## 📞 CONTATOS & REFERÊNCIAS

**Desenvolvido por**: @joaohperes
**Repositório**: github.com/joaohperes/escala-hro
**Deploy**: escala-hro.vercel.app

**Commits Principais**:
- `0ff9a22`: docs: Add final workflow documentation and validation
- `ac1903e`: fix: Remove duplicate professional entries and fix anterior date display
- `75d0917`: feat: Add missing professional contact - Maisa Miranda Cascaes
- `930f77e`: style: Refine footer easter-egg and status indicator display
- `24f24ba`: feat: Restore footer with easter-egg @joaohperes

---

**REMEMBER**: Este é o workflow FINAL. Não quebre as 3 regras críticas acima. 🚀
