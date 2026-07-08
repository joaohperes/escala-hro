# 🚀 Início Rápido - Escala HRO

## 1️⃣ Verificar Extração (LOCAL)

```bash
cd /Users/joaoperes/escalaHRO
python3 extracao_inteligente.py
```

**Resultado esperado**: 78+ registros extraídos em ~30 segundos

---

## 2️⃣ Converter Dados

```bash
python3 converter_inteligente.py
```

**Resultado esperado**: Dados convertidos para formato de dashboard

---

## 3️⃣ Gerar Dashboard

```bash
python3 gerar_dashboard_executivo.py
```

**Resultado esperado**: HTML gerado em `/tmp/dashboard_executivo.html`

---

## 4️⃣ Ver Dashboard Online

Acesse: https://joaohperes.github.io/escala-hro/

**Você deve ver**:
- 51 profissionais únicos
- 32 setores
- 78 registros de turnos
- Busca e filtros funcionando

---

## 5️⃣ Testar Automação (GitHub Actions)

1. Acesse: https://github.com/joaohperes/escala-hro
2. Vá para **Actions**
3. Clique em **"Atualizar Escala HRO Diariamente"**
4. Clique em **"Run workflow"**

**A automação rodará e atualizará o dashboard em ~5 minutos**

---

## ⏰ Automação Automática

- **Horário**: Todos os dias às 7:01 AM (horário de Brasília)
- **Dia da semana**: Segunda a domingo (inclusive)
- **Resultado**: Dashboard atualizado em ~5 minutos

---

## 📊 O que Está Sendo Extraído

✅ **Profissionais**: 51 únicos
✅ **Turnos**: 78 registros
✅ **Setores**: 32 diferentes
✅ **Horários**: Cada turno com horário completo
✅ **Contatos**: Email e telefone de cada profissional

---

## 🔧 Se Algo Não Funcionar

### Extração Retorna 0 Registros?
```bash
# Verificar credenciais em .env
cat .env | grep ESCALA
```

### Dashboard Vazio?
```bash
# Verificar arquivo JSON
cat /tmp/escalas_multiplos_dias.json | python3 -m json.tool | head -20
```

### GitHub Actions Falhando?
- Verificar **Secrets** em Settings → Secrets
- Verificar **Logs** em Actions → Workflow run

---

## 📚 Documentação Completa

- **Todos os scripts**: [SCRIPTS_ESSENCIAIS.md](SCRIPTS_ESSENCIAIS.md)
- **Checklist final**: [CHECKLIST_FINAL.md](CHECKLIST_FINAL.md)
- **README**: [README.md](README.md)

---

## 💡 Próximas Vezes

### Para testar localmente:
```bash
python3 extracao_inteligente.py && \
python3 converter_inteligente.py && \
python3 gerar_dashboard_executivo.py
```

### Para rodar tudo com Notion:
```bash
bash rodar_diariamente.sh
```

---

## ✅ Pronto!

Seu sistema está **100% pronto** para produção. A automação rodará todos os dias automaticamente! 🎉

---

**Última atualização**: 02 de Novembro de 2025
