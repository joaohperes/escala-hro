# 🎯 Plano de Estabilização do Dashboard Escala HRO

## 📊 Situação Atual

### ✅ O que está funcionando PERFEITAMENTE
- **Extração de dados**: `extracao_inteligente.py` extrai 90+ profissionais diariamente
- **Dashboard UI**: Interface responsive, beautiful, todas as features funcionais
- **Autenticação**: Email ou últimos 4 dígitos
- **Lógica de "Dia Anterior"**: Mecanismo de janela rolante funciona
- **Transformação de dados**: Classificação de setores, detecção de turno

### ❌ O que está QUEBRADO
1. **Dois workflows em conflito** (HIGH RISK)
   - `atualizar-dashboard.yml` (10:01 UTC) - Desatualizado
   - `daily-escala.yml` (10:00 UTC) - Correto, usando `update_dashboard.py`
   - Causa: Conflito de timing, possível sobrescrita de dados

2. **Arquivo faltando no workflow** (HIGH RISK)
   - `converter_inteligente.py` não existe (linha 43 do atualizar-dashboard.yml)
   - Falha silenciosa por `continue-on-error: true`

3. **Dados temporários em /tmp** (CRITICAL RISK)
   - `/tmp/extracao_inteligente_anterior.json` (dia anterior)
   - Perdido quando GitHub Actions reinicia
   - Causa dados N/A e vazio

4. **Desalinhamento ocasional** (MEDIUM RISK)
   - Cards cortados no mobile
   - Causado por versões desincronizadas do HTML

---

## 🔧 Plano de Ação (3 Fases)

### FASE 1: CORREÇÃO CRÍTICA (30 minutos)

#### 1.1 Remover workflow duplicado
```bash
# Deletar o workflow antigo
rm .github/workflows/atualizar-dashboard.yml

# Commit
git add .github/workflows/
git commit -m "fix: Remove duplicate workflow to prevent conflicts"
git push
```
**Resultado**: Elimina conflito de dois workflows

#### 1.2 Verificar requirements.txt
```bash
# Verificar se existe
ls -la requirements.txt

# Se não existir, criar com dependências necessárias:
```

**requirements.txt:**
```
selenium==4.14.0
webdriver-manager==4.0.1
pydantic==2.5.0
```

**Resultado**: `daily-escala.yml` funciona corretamente

#### 1.3 Validar dados persistentes
```bash
# Verificar se extracao_inteligente.json existe
ls -la /tmp/extracao_inteligente.json
ls -la /tmp/extracao_inteligente_anterior.json

# Se não existir, criar um vazio para hoje:
echo '{"professionals": [], "data": "2025-11-08"}' > extracao_inteligente_atual.json
```

**Resultado**: Garantir que dados de "Dia Anterior" sempre existem

---

### FASE 2: CONSOLIDAÇÃO DE DADOS (1 hora)

#### 2.1 Commit dados de exemplo no repo
```bash
# Criar arquivo com dados de referência
# Isso garante que se /tmp for limpo, temos fallback

mkdir -p data
cp /tmp/extracao_inteligente.json data/extracao_inteligente_sample.json
cp /tmp/escalas_multiplos_dias.json data/escalas_multiplos_dias_sample.json (se existir)

git add data/
git commit -m "docs: Add sample data files for reference and fallback"
git push
```

**Resultado**: Fallback de dados se extração falhar

#### 2.2 Atualizar gerar_dashboard_executivo.py
```python
# Adicionar fallback para dados
DATA_PATHS = [
    "/tmp/extracao_inteligente.json",           # Dados de hoje (temp)
    "/tmp/extracao_inteligente_anterior.json",  # Dados de ontem (temp)
    "./data/extracao_inteligente_sample.json",  # Fallback do repo
]

# Se nenhum tiver dados, usar valores padrão
```

**Resultado**: Dashboard nunca fica vazio

---

### FASE 3: VALIDAÇÃO E MONITORAMENTO (30 minutos)

#### 3.1 Criar script de health check
```bash
# health_check.py
```

**health_check.py:**
```python
#!/usr/bin/env python3
"""
Verifica a saúde do sistema de atualização
"""
import json
from pathlib import Path

def check_system():
    checks = {
        "extraction_file": Path("/tmp/extracao_inteligente.json").exists(),
        "previous_day_file": Path("/tmp/extracao_inteligente_anterior.json").exists(),
        "dashboard_exists": Path("index.html").exists(),
        "has_workflows": any(Path(".github/workflows").glob("*.yml")),
    }

    return all(checks.values()), checks

if __name__ == "__main__":
    healthy, details = check_system()
    print("✅ Sistema OK" if healthy else "❌ Problemas encontrados")
    for check, status in details.items():
        print(f"  {'✓' if status else '✗'} {check}")
    exit(0 if healthy else 1)
```

#### 3.2 Testar fluxo completo
```bash
# Executar extraction manualmente
python3 extracao_inteligente.py

# Executar dashboard generation
python3 gerar_dashboard_executivo.py

# Verificar resultado
python3 health_check.py
```

#### 3.3 Adicionar monitoramento ao workflow
```yaml
# No daily-escala.yml, adicionar step final:
- name: Health Check
  run: python3 health_check.py
```

---

## 📋 Arquivos para Organização

### ✅ Manter (CORE do sistema)
```
/
├── index.html                          # Dashboard principal (MANTER, não regerar)
├── extracao_inteligente.py             # Extração de dados
├── gerar_dashboard_executivo.py        # Geração do dashboard
├── update_dashboard.py                 # Orquestração
├── requirements.txt                    # Dependências (CRIAR)
├── .github/workflows/
│   └── daily-escala.yml                # ÚNICO workflow (manter)
└── data/                               # Dados de fallback (CRIAR)
    ├── extracao_inteligente_sample.json
    └── escalas_multiplos_dias_sample.json
```

### ❌ Deletar (OBSOLETO)
```
├── .github/workflows/atualizar-dashboard.yml     # ← DELETAR
├── converter_inteligente.py                      # Não existe, causa erro
├── gerar_dashboard_*.py (antigos)                # Se houver duplicatas
└── dashboard_final.html, dashboard_executivo.html (obsoletos)
```

### 📚 Manter como referência
```
├── ESTABILIZACAO_PROJETO.md            # Este arquivo
├── docs/index.html                     # Backup/docs
├── publicar_notion.py                  # Se útil
└── fix_previous_day.py                 # Se necessário depois
```

---

## 🚀 Checklist de Implementação

### FASE 1 (30 min)
- [ ] Deletar `atualizar-dashboard.yml`
- [ ] Criar `requirements.txt`
- [ ] Verificar que `daily-escala.yml` tem todas as dependências
- [ ] Commit e push

### FASE 2 (1 hora)
- [ ] Copiar dados de amostra para `data/`
- [ ] Atualizar `gerar_dashboard_executivo.py` com fallbacks
- [ ] Testar extração e geração localmente
- [ ] Commit e push

### FASE 3 (30 min)
- [ ] Criar `health_check.py`
- [ ] Adicionar step de health check no workflow
- [ ] Testar fluxo completo (workflow_dispatch)
- [ ] Verificar logs do GitHub Actions
- [ ] Commit e push

---

## ✨ Resultado Final

Depois dessas alterações:

✅ **Workflow automático estável**
- Executa 1x por dia às 10:00 UTC
- Sem conflitos
- Falhas não causam dados vazio

✅ **Dados persistentes**
- "Dia Anterior" sempre disponível
- Ramais sempre visível
- Fallback se extração falhar

✅ **Fácil monitoramento**
- Health check automático
- Logs do workflow claros
- Alerts via GitHub Actions

✅ **Dashboard sempre funcional**
- Nunca fica vazio
- Sempre com dados do dia anterior
- Sem desalinhamentos

---

## 📞 Troubleshooting

| Problema | Causa | Solução |
|----------|-------|--------|
| "Dia Anterior" = N/A | /tmp limpo | Commit dados no repo |
| Ramais vazio | Extração falhou | Usar fallback sample data |
| Dashboard não atualiza | Workflow não rodou | Usar workflow_dispatch |
| Cards cortados mobile | Versão desincronizada | Única versão no repo |

---

## 📅 Próximos Passos (Opcional)

Depois que estável, considere:

1. **Backup automático** de dados em S3 ou GitHub Releases
2. **Notificações** se atualização falhar (email, Slack)
3. **Dashboard de status** mostrando última atualização
4. **Versioning** automático (v1.0, v1.1, etc)
5. **Cache inteligente** se API do Escala cair

