# 📅 Histórico do Dashboard - Como Funciona

## Visão Geral

O dashboard mantém automaticamente um **histórico dos últimos 3 dias** de escalas para que você possa consultar dados anteriores sem perder informações.

---

## 🔄 Como o Histórico Funciona

### Processo Diário

**Todos os dias às 7:01 AM (Brasília)**:

1. **Extração** (`extracao_inteligente.py`)
   - Extrai dados de TODAY
   - Salva em: `/tmp/extracao_inteligente.json`

2. **Conversão** (`converter_inteligente.py`)
   - Lê dados extraídos de TODAY
   - Carrega histórico anterior (se existir)
   - Monta estrutura com 3 dias:
     - **Anterior**: Dia anterior ao arquivo anterior
     - **Atual**: TODAY (dados novos)
     - **Próxima**: Próximo dia (vazio até ser extraído)
   - Salva em: `/tmp/escalas_multiplos_dias.json`

3. **Dashboard** (`gerar_dashboard_executivo.py`)
   - Lê os 3 dias do histórico
   - Gera HTML com abas/filtros para cada dia
   - Salva em: `/tmp/dashboard_executivo.html`

4. **Publicação** (GitHub Pages)
   - Copia HTML para GitHub Pages
   - Dashboard online atualizado

---

## 📊 Estrutura do Histórico

```json
{
  "anterior": {
    "data": "01 novembro 2025",
    "data_simples": "01/11/2025",
    "registros": [...],
    "total": 75,
    "nota": "Dados do dia anterior para consulta histórica"
  },
  "atual": {
    "data": "02 novembro 2025",
    "data_simples": "02/11/2025",
    "registros": [...],
    "total": 78,
    "nota": "Dados de hoje extraídos de escala.med.br"
  },
  "proxima": {
    "data": "03 novembro 2025",
    "data_simples": "03/11/2025",
    "registros": [],
    "total": 0,
    "nota": "Próximo dia (dados indisponíveis no momento)"
  }
}
```

---

## 🗓️ Exemplos de Sequência Diária

### Dia 1 (01 de novembro)
```
Anterior: (vazio)
Atual: 01/11 - 75 registros ✅
Próxima: (vazio)
```

### Dia 2 (02 de novembro) - 7:01 AM
```
Anterior: 01/11 - 75 registros (preservado!) ✅
Atual: 02/11 - 78 registros ✅
Próxima: (vazio)
```

### Dia 3 (03 de novembro) - 7:01 AM
```
Anterior: 02/11 - 78 registros (preservado!) ✅
Atual: 03/11 - 80 registros ✅
Próxima: (vazio)
```

---

## 🎯 Funcionalidades do Histórico

### Dashboard Mostra

✅ **Abas/Filtros por Data**
- Usuário pode clicar em diferentes datas
- Ver escalas do dia anterior, hoje ou próximo dia

✅ **Contador de Registros**
- Mostra total para cada dia
- Fácil comparação entre dias

✅ **Busca em Todo Período**
- Procurar profissional nos últimos 3 dias
- Encontrar quando ele trabalhou

✅ **Estatísticas**
- Total de profissionais
- Total de setores
- Distribuição por período

---

## 💾 Armazenamento

### Arquivo Principal
- **Localização**: `/tmp/escalas_multiplos_dias.json`
- **Atualizado**: Diariamente às 7:01 AM
- **Tamanho**: ~30-50 KB (varia com número de registros)
- **Formato**: JSON estruturado com 3 dias

### Histórico Anterior
- Quando novo dia é processado, o arquivo anterior é usado como referência
- Cascata automática: `anterior` → `atual` → `proxima`
- Dados não são perdidos até 3 dias atrás

---

## ⚠️ Limitações Atuais

### Não Há Persistência Permanente
- Apenas últimos **3 dias** mantidos
- Dados mais antigos são sobrescritos
- Se você quer histórico de meses, veja seção abaixo

### Próximo Dia Vazio
- Campo `proxima` está vazio até ser extraído
- Quando extraído no dia seguinte, passa para `anterior`
- Mantém movimentação de 3 dias

---

## 🚀 Futuras Melhorias (Opcional)

Se você quiser manter histórico **permanente**, podemos:

### Opção 1: Arquivo de Histórico Expandido
```
/tmp/escalas_historico_completo.json
{
  "01/11/2025": { registros: [...] },
  "02/11/2025": { registros: [...] },
  "03/11/2025": { registros: [...] },
  ...
}
```

### Opção 2: Banco de Dados
- SQLite para histórico completo
- Querys para diferentes períodos
- Gráficos de tendências

### Opção 3: GitHub Storage
- Cada dia um arquivo separado
- Histórico versionado no Git
- Acesso a qualquer data histórica

---

## 📝 Exemplos de Uso

### Usuário quer ver escalas de ontem
1. Abra dashboard
2. Clique na aba "01 novembro"
3. Busque o profissional desejado
4. Veja turnos, horários, contatos

### Usuário quer comparar profissional em 3 dias
1. Abra dashboard
2. Use a busca para o profissional
3. Selecione diferentes abas de data
4. Compare turnos e horários

### Usuário quer histórico de um profissional
1. Use a busca para o nome
2. Veja em quais dias ele aparece
3. Clique em cada dia para ver detalhes

---

## 🔍 Verificação de Histórico

### Ver arquivo atual do conversor
```bash
cat /tmp/escalas_multiplos_dias.json | python3 -m json.tool
```

### Verificar contagem de registros
```bash
# Anterior
jq '.anterior.total' /tmp/escalas_multiplos_dias.json

# Atual
jq '.atual.total' /tmp/escalas_multiplos_dias.json

# Próxima
jq '.proxima.total' /tmp/escalas_multiplos_dias.json
```

---

## 📊 Fluxo de Dados Simplificado

```
escala.med.br
     ↓
extracao_inteligente.py (extrai TODAY)
     ↓
/tmp/extracao_inteligente.json (TODAY)
     ↓
converter_inteligente.py (com histórico)
     ↓
/tmp/escalas_multiplos_dias.json (3 dias)
     ↓
gerar_dashboard_executivo.py
     ↓
/tmp/dashboard_executivo.html
     ↓
GitHub Pages (publicado)
     ↓
https://joaohperes.github.io/escala-hro/ (visível!)
```

---

## ✅ Resumo

| Aspecto | Detalhes |
|---------|----------|
| **Dias Mantidos** | 3 (anterior, atual, próximo) |
| **Atualização** | Diariamente às 7:01 AM |
| **Armazenamento** | `/tmp/escalas_multiplos_dias.json` |
| **Formato** | JSON estruturado |
| **Perda de Dados** | Após 3 dias (se quer permanente, solicite melhoria) |
| **Visibilidade** | Dashboard com abas/filtros por data |

---

**Última atualização**: 02 de Novembro de 2025
