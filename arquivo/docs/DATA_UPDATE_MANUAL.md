# 📊 ATUALIZAÇÃO MANUAL DE DADOS - ESCALA HRO

**Status**: INFORMAÇÃO CRÍTICA
**Data**: 17/11/2025

---

## ⚠️ PROBLEMA IDENTIFICADO

O dashboard está mostrando dados **ESTÁTICOS** em vez de dados **REAIS** de hoje e ontem.

**Exemplo:**
- Esperado: Paulo Felipe de manhã, Leonardo Lock de tarde no P1 do PS
- Exibindo: Patricia Carla De Lima no Ambulatório de Oncologia

---

## 🔍 RAIZ DO PROBLEMA

### Por que isso acontece?

1. **GitHub Actions workflow roda diariamente** ✅
   - Configurado para executar às 10h UTC (7h Brasília)
   - Tenta extrair dados frescos via `extracao_inteligente.py`

2. **Extração falha silenciosamente** ❌
   - Precisa de credenciais: `ESCALA_USERNAME` + `ESCALA_PASSWORD`
   - Credenciais vêm dos GitHub Secrets
   - Se credenciais estiverem erradas/vazias, falha sem aviso

3. **Fallback para dados estáticos** ⚠️
   - Se extração falhar, usa `escalas_multiplos_dias.json`
   - Este arquivo é de **teste/amostra**, não dados reais
   - Dashboard mostra sempre os mesmos dados

---

## 🔧 COMO CORRIGIR

### Opção 1: Verificar Credenciais do GitHub

1. Acesse: https://github.com/joaohperes/escala-hro/settings/secrets/actions
2. Verifique se existem:
   - `ESCALA_USERNAME` - Email/usuário de login
   - `ESCALA_PASSWORD` - Senha

Se não existirem ou estiverem vazias:
- Adicione: Settings → Secrets and variables → Actions → New repository secret
  ```
  ESCALA_USERNAME = seu_email@exemplo.com
  ESCALA_PASSWORD = sua_senha
  ```

### Opção 2: Atualizar Dados Manualmente (Imediato)

Se precisa de dados atualizados AGORA:

```bash
# 1. Executar extração manualmente
python3 extracao_inteligente.py

# 2. Gerar dashboard
python3 gerar_dashboard_executivo.py

# 3. Verificar validação
python3 validar_producao.py

# 4. Fazer commit
git add index.html
git commit -m "Atualizar dashboard com dados manuais"
git push origin main
```

### Opção 3: Rodar Workflow Manualmente no GitHub

1. Acesse: https://github.com/joaohperes/escala-hro/actions
2. Clique em: "Atualizar Escala Diária HRO"
3. Clique em: "Run workflow" → "Run workflow"
4. Aguarde completar (5-10 minutos)

---

## 📋 CHECKLIST DE MANUTENÇÃO

### Daily:
- [ ] Verificar se dashboard mostra dados de hoje
- [ ] Confirmar que "Dia Anterior" tem profissionais reais
- [ ] Verificar se P1 do PS tem pessoas conhecidas

### Weekly:
- [ ] Verificar logs do GitHub Actions
- [ ] Confirmar que workflow rodou com sucesso
- [ ] Se falhou: Verificar credenciais

### Monthly:
- [ ] Validar com `python3 validar_producao.py`
- [ ] Revisar logs de erro (se houver)
- [ ] Testar manual extraction para garantir funcionamento

---

## 🚨 SINAIS DE QUE DADOS ESTÃO ERRADOS

- ❌ Mesmo profissional em vários lugares
- ❌ Horários duplicados (ex: 07:00/07:00)
- ❌ Datas antigas (14 nov quando é 17 nov)
- ❌ Profissionais que não existem
- ❌ Dados que não mudam dia a dia

Se ver esses sinais → Dados são do arquivo estático, não reais!

---

## 🔄 FLUXO ESPERADO DE ATUALIZAÇÃO

```
GitHub Actions (diário às 7h Brasília)
    ↓
extracao_inteligente.py
    ├─ Tenta: escala.med.br
    ├─ Se sucesso: Extrai dados REAIS
    └─ Se falha: Usa cache/fallback
    ↓
gerar_dashboard_executivo.py
    ├─ Prioritário: /tmp/extracao_inteligente.json (dados frescos)
    └─ Fallback: escalas_multiplos_dias.json (teste/antigos)
    ↓
Commit e Push para GitHub
    ↓
Vercel Deploy Automático
    ↓
escala-hro.vercel.app ATUALIZADO
```

---

## 📞 O QUE FAZER SE CONTINUAR COM DADOS ERRADOS

1. **Verificar logs do workflow**:
   - GitHub → Actions → "Atualizar Escala Diária HRO"
   - Abrir o último run
   - Procurar por erros na seção "Atualizar Escala e Dashboard"

2. **Testar credenciais manualmente**:
   ```bash
   # Editar e substituir pelos seus valores:
   export ESCALA_USERNAME="seu_email@hospital.com"
   export ESCALA_PASSWORD="sua_senha"
   python3 extracao_inteligente.py
   ```

3. **Se continuar falhando**:
   - Verificar se escala.med.br está online
   - Verificar se credenciais estão corretas
   - Verificar se página HTML mudou (layout modificado)
   - Se necessário: atualizar lógica de parsing em `extracao_inteligente.py`

---

## ✅ GARANTIA DE DADOS REAIS

Para garantir que dados REAIS são usados:

**Cada dia ao acordar:**
```bash
# Verificar que dados estão atualizados
grep -i "17 november\|16 november" index.html
# Se mostrar datas corretas: ✅ OK
# Se mostrar datas antigas (14 nov): ⚠️ Dados estáticos
```

**Se dados forem estáticos:**
```bash
# Rodar extração manual e regenerar
python3 extracao_inteligente.py && python3 gerar_dashboard_executivo.py
git add index.html && git commit -m "Manual data update" && git push
```

---

## 🎯 RESUMO EXECUTIVO

| Aspecto | Status | Ação |
|---------|--------|------|
| Dashboard Visual | ✅ Funcionando | Nenhuma |
| Autenticação | ✅ Ativa | Nenhuma |
| Ramais | ✅ Embarcados | Nenhuma |
| Dados Reais | ⚠️ Estáticos | Verificar credenciais GitHub |
| Workflow Automático | ✅ Roda diariamente | Monitorar logs |

**Ação Imediata Sugerida:**
1. Verificar credenciais em GitHub Secrets
2. Rodar workflow manualmente para testar
3. Se não funcionar: Investigar logs de erro

---

**IMPORTANTE**: Este é um documento de conhecimento crítico. Compartilhe com qualquer pessoa que faça manutenção do sistema!
