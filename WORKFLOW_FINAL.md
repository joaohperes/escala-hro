# 🚀 WORKFLOW FINAL - ESCALA HRO

## Princípios Fundamentais

Este documento define o workflow final e definitivo para evitar erros recorrentes.

### 1. RAMAIS - NUNCA MUDAM ✅
- **Localização**: `ramais_hro.json` e `setor_ramais_mapping.json`
- **Persistência**: SEMPRE embarcados no `/tmp/extracao_inteligente.json`
- **Responsabilidade**: `extracao_inteligente.py` carregar e embutir na extração
- **Backup**: Duplicados em `data/extracao_inteligente_anterior_cache.json`
- **Validação**: Após cada extração, verificar que `"ramais_hro"` está presente

```json
{
  "atual": { ... },
  "anterior": { ... },
  "ramais_hro": [ ... ],  // SEMPRE PRESENTE
  "setor_ramais_mapping": [ ... ]  // SEMPRE PRESENTE
}
```

**Código de validação**:
```python
# No final de extracao_inteligente.py
assert 'ramais_hro' in output_data, "❌ Ramais não foram embarcados!"
assert len(output_data['ramais_hro']) > 0, "❌ Ramais vazios!"
```

---

### 2. DIA ANTERIOR - ROLLING WINDOW (D-1) ✅

#### Lógica Correta:

**Hoje (D)**: Primeira execução do dia
- Extrai dados atuais → `/tmp/extracao_inteligente.json['atual']`
- Carrega cache anterior → `/tmp/extracao_inteligente.json['anterior']`
- Data do anterior deve ser exatamente **D-1** (ontem)

**Amanhã (D+1)**: Segunda execução
- Extrai dados atuais → `/tmp/extracao_inteligente.json['atual']` (novo)
- `atual` de hoje (D) vira `anterior` de amanhã (D+1)

#### Fluxo de Dados:

```
Dia 14 (Execução 1):
  atual: 14 nov (dados extraídos)
  anterior: 13 nov (do cache anterior)

Dia 15 (Execução 2):
  atual: 15 nov (dados extraídos)
  anterior: 14 nov (atual do dia anterior)

Dia 16 (Execução 3):
  atual: 16 nov (dados extraídos)
  anterior: 15 nov (atual do dia anterior)
```

#### Código em `extracao_inteligente.py`:

```python
# Na seção de salvamento:
atual_salvo = resultado  # Dados de hoje
anterior_anterior = resultado_anterior_salvo  # Dados de ontem

# Preparar cache para amanhã
cache_proximo = {
    'atual': atual_salvo,      # Será o anterior amanhã
    'anterior': anterior_anterior  # Será descartado
}

# Salvar cache
with open(arquivo_anterior_persistente, 'w') as f:
    json.dump(cache_proximo, f, ensure_ascii=False, indent=2)
```

---

### 3. PROFISSIONAIS - GESTÃO DE CONTATOS ✅

#### Localização
- `profissionais_autenticacao.json` - Banco de dados único
- Estrutura única e consolidada (sem duplicatas)

#### Adicionar Contatos
Use `add_contacts_bulk.py`:
```bash
python3 add_contacts_bulk.py novos_contatos.json
```

#### Validação Automática
- ✅ Detecta duplicatas por nome normalizado
- ✅ Mantém entrada com mais campos preenchidos
- ✅ Não cria duplicatas

#### Limpeza Periódica
Executar mensalmente:
```bash
python3 remove_duplicates.py
```

---

## Checklist de Execução Diária

### ✅ Antes da Extração (GitHub Actions)
- [ ] Ramais estão atualizados em `ramais_hro.json`?
- [ ] Arquivo anterior cache existe? (`data/extracao_inteligente_anterior_cache.json`)

### ✅ Durante a Extração
- [ ] `extracao_inteligente.py` executa sem erros
- [ ] Output contém `"ramais_hro"` e `"setor_ramais_mapping"`
- [ ] Anterior data está correta (D-1)

### ✅ Após Dashboard
- [ ] `gerar_dashboard_executivo.py` carrega ramais do arquivo de extração
- [ ] Dashboard mostra dia atual e anterior corretos
- [ ] Todos os profissionais têm contatos atualizados

### ✅ Antes do Deploy
- [ ] Sem duplicatas em `profissionais_autenticacao.json`
- [ ] Git status limpo (sem alterações não commitadas)
- [ ] Vercel deploy automático (via GitHub)

---

## Arquivos Críticos

### Configuração
| Arquivo | Função | Atualização |
|---------|--------|-------------|
| `ramais_hro.json` | Mapeamento de ramais | Manual (raro) |
| `setor_ramais_mapping.json` | Mapeamento setor→ramais | Manual (raro) |
| `profissionais_autenticacao.json` | Banco de profissionais | Por script ou manual |

### Dinâmicos (Atualizados Diariamente)
| Arquivo | Função | Atualização |
|---------|--------|-------------|
| `/tmp/extracao_inteligente.json` | Extração do dia | Workflow automático |
| `data/extracao_inteligente_anterior_cache.json` | Cache para próximo dia | Workflow automático |
| `index.html` | Dashboard público | Workflow automático |

### Scripts
| Script | Função |
|--------|--------|
| `extracao_inteligente.py` | Extrai e embaça ramais |
| `gerar_dashboard_executivo.py` | Gera HTML final |
| `add_contacts_bulk.py` | Adiciona contatos em massa |
| `remove_duplicates.py` | Remove duplicatas (mensal) |

---

## Histórico de Erros Evitados

### ❌ Erro 1: Ramais não persistindo
**Causa**: Ramais carregados de arquivos separados não disponíveis em workflows
**Solução**: Embutir sempre em `/tmp/extracao_inteligente.json`
**Validação**: `assert 'ramais_hro' in output_data`

### ❌ Erro 2: Dia anterior com 2 dias de diferença
**Causa**: Workflow não rodou no dia anterior (feriado/fim de semana)
**Solução**: Usar dia anterior do cache anterior (não de 2 dias atrás)
**Validação**: Data do anterior deve ser sempre `datetime.now() - timedelta(days=1)`

### ❌ Erro 3: Duplicatas de profissionais
**Causa**: Script adicionava nomes sem verificar existentes
**Solução**: Normalizar nomes e comparar antes de adicionar
**Validação**: Executar `remove_duplicates.py` antes de cada deploy

---

## Comandos Úteis

### Validar Extração
```bash
python3 << 'EOF'
import json
with open('/tmp/extracao_inteligente.json', 'r') as f:
    data = json.load(f)
print(f"✅ Atual: {data['atual']['data']}")
print(f"✅ Anterior: {data['anterior']['data']}")
print(f"✅ Ramais: {len(data.get('ramais_hro', []))} departamentos")
assert 'ramais_hro' in data, "❌ Ramais faltando!"
print(f"✅ Tudo correto!")
EOF
```

### Validar Profissionais
```bash
python3 << 'EOF'
import json
from collections import Counter

with open('profissionais_autenticacao.json', 'r') as f:
    data = json.load(f)

# Verificar duplicatas
nomes = [p['name'].lower() for p in data['professionals']]
duplicatas = [nome for nome, count in Counter(nomes).items() if count > 1]

if duplicatas:
    print(f"❌ Duplicatas encontradas: {duplicatas}")
else:
    print(f"✅ {len(data['professionals'])} profissionais sem duplicatas")
EOF
```

---

## Próximas Execuções (Garantido)

✅ **Dia 17 de novembro (amanhã)**
- Extrai dados de 17 nov
- Anterior: 16 nov (do cache de hoje)
- Ramais: Embarcados ✅
- Profissionais: Consolidados ✅

✅ **Fins de semana/Feriados**
- Se workflow não rodar: Usa anterior do cache (não de 2+ dias atrás)
- Se rodar: Atualiza normal com D-1

---

## Contato de Referência

**Última atualização**: 16/11/2025 às 13:45 UTC
**Profissionais no sistema**: 171
**Ramais no sistema**: 134 departamentos
**Status**: ✅ PRODUÇÃO ESTÁVEL

---

**IMPORTANTE**: Este é o workflow final. Não fazer mudanças sem atualizar este documento!
