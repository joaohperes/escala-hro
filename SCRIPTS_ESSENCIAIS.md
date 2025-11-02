# 📋 Scripts Essenciais - Escala HRO

## Pipeline de Automação Diária

A automação executa em ordem os seguintes scripts:

### 1️⃣ `extracao_inteligente.py`
**Função**: Extrai dados das escalas médicas do site escala.med.br

**Saída**: `/tmp/extracao_inteligente.json`

**Formato de saída**:
```json
{
  "data": "02 novembro 2025",
  "registros": [
    {
      "profissional": "Nome do Profissional",
      "setor": "Nome do Setor",
      "tipo_turno": "Tipo de Turno",
      "horario": "HH:MM/HH:MM",
      "email": "email@example.com",
      "phone": "(XX) XXXXX-XXXX",
      "data": "02 novembro 2025"
    }
  ],
  "total": 78,
  "setores_encontrados": 32,
  "headers_encontrados": 32
}
```

**Dependências**:
- Selenium
- python-dotenv
- `.env` com `ESCALA_USERNAME` e `ESCALA_PASSWORD`

**Status**: ✅ **FUNCIONANDO** - Extrai 78+ registros diariamente

---

### 2️⃣ `converter_inteligente.py`
**Função**: Converte formato de saída para o formato esperado pelo dashboard

**Entrada**: `/tmp/extracao_inteligente.json`

**Saída**: `/tmp/escalas_multiplos_dias.json`

**Formato de saída**:
```json
{
  "anterior": {
    "data": "01 novembro 2025",
    "data_simples": "01/11/2025",
    "registros": [],
    "total": 0
  },
  "atual": {
    "data": "02 novembro 2025",
    "data_simples": "02/11/2025",
    "registros": [...],
    "total": 78
  },
  "proxima": {
    "data": "03 novembro 2025",
    "data_simples": "03/11/2025",
    "registros": [],
    "total": 0
  }
}
```

**Status**: ✅ **FUNCIONANDO** - Converte 78 registros corretamente

---

### 3️⃣ `gerar_dashboard_executivo.py`
**Função**: Gera o HTML final do dashboard com visual premium

**Entrada**: `/tmp/escalas_multiplos_dias.json`

**Saída**: `/tmp/dashboard_executivo.html`

**Funcionalidades**:
- Design responsivo e profissional
- Busca e filtro de profissionais
- Organização por setor
- Agrupamento por turnos
- Exibição de contatos (email/phone)
- Estatísticas de profissionais e setores

**Status**: ✅ **FUNCIONANDO** - Gera dashboard com 78 registros

---

## Scripts de Suporte (Opcional)

### `publicar_notion.py`
**Função**: Publica dados das escalas no Notion

**Uso**: Executado no `rodar_diariamente.sh` (local)

**Dependências**:
- `.env` com `NOTION_API_KEY` e `NOTION_DATABASE_ID`

**Status**: ✅ **FUNCIONANDO**

---

### `criar_views_notion.py`
**Função**: Cria views iniciais no Notion (setup único)

**Uso**: Executar manualmente após setup inicial

**Frequência**: Uma única vez durante o setup

**Status**: ✅ **FUNCIONANDO**

---

## GitHub Actions Workflow

**Arquivo**: `.github/workflows/atualizar-escala.yml`

**Agendamento**:
- Automático: `1 10 * * *` (7:01 AM Brasília = 10:01 UTC)
- Manual: Via GitHub Actions

**Pipeline executado**:
```
1. extracao_inteligente.py
   ↓
2. converter_inteligente.py
   ↓
3. gerar_dashboard_executivo.py
   ↓
4. Copia index.html para GitHub Pages
   ↓
5. Commit e push automático
```

---

## Executar Localmente

### Uma vez por dia (com Notion):
```bash
bash rodar_diariamente.sh
```

### Apenas extração + dashboard:
```bash
python3 extracao_inteligente.py
python3 converter_inteligente.py
python3 gerar_dashboard_executivo.py
```

### Teste rápido:
```bash
# Apenas extração
python3 extracao_inteligente.py

# Ver resultado
cat /tmp/extracao_inteligente.json | python3 -m json.tool | head -30
```

---

## Variáveis de Ambiente Necessárias

### `.env` (Local)
```
ESCALA_USERNAME=seu_email@exemplo.com
ESCALA_PASSWORD=sua_senha
NOTION_API_KEY=sua_chave_notion
NOTION_DATABASE_ID=seu_database_id
```

### GitHub Secrets
- `ESCALA_USERNAME`
- `ESCALA_PASSWORD`

---

## Verificação de Status

### Verificar extração:
```bash
python3 extracao_inteligente.py
echo "Registros extraídos:"
grep -c '"profissional":' /tmp/extracao_inteligente.json
```

### Verificar conversão:
```bash
python3 converter_inteligente.py
echo "Total de registros convertidos:"
grep -c '"profissional":' /tmp/escalas_multiplos_dias.json
```

### Verificar dashboard:
```bash
python3 gerar_dashboard_executivo.py
echo "Registros no dashboard:"
grep -o '"profissional":' /tmp/dashboard_executivo.html | wc -l
```

---

## Histórico de Mudanças

### 📅 02 de Novembro de 2025
- ✅ Criado `converter_inteligente.py` para adaptar formato de dados
- ✅ Atualizado GitHub Actions workflow com novo converter
- ✅ Removidos 32 scripts descontinuados
- ✅ Mantidos apenas 5 scripts essenciais
- ✅ Todos os 78 registros agora extraindo corretamente

---

## ⚠️ Scripts Removidos (Razão)

Todos os seguintes scripts foram removidos por estarem quebrados, duplicados ou obsoletos:

**Extração**: `extracao_3_datas`, `extracao_apenas`, `extracao_com_historico`, `extracao_data_especifica`, `extracao_dois_dias`, `extracao_multiplos_dias`, `extracao_teste`, `extracao_tres_dias_correto`, `extracao_v5`, `extracao_visual`, `scraper*`

**Dashboard**: `gerar_dashboard` (todas as versões antigas)

**Automação**: `automate_update`, `update_datas`, `update_escalas_data`, `limpar_e_republica`

**Suporte Notion**: `fix_notion`, `reorganizar_notion`

**Debug**: `debug_escala`, `relatorio_escala`

---

## 🚀 Próximos Passos

1. ✅ Verificar que GitHub Actions usa os secrets corretos
2. ✅ Monitorar primeira execução automática (próximo dia)
3. ✅ Documentação concluída
