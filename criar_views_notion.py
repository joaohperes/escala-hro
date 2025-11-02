#!/usr/bin/env python3
"""
Cria automaticamente Views filtradas no Notion para melhor organização
Cada view mostra apenas uma especialidade
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv('NOTION_API_KEY')
DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

print(f"\n{'='*100}")
print("📱 CRIANDO VIEWS FILTRADAS NO NOTION")
print(f"{'='*100}\n")

# Definir views a criar
views = [
    {
        'name': '🚨 Emergência',
        'icon': '🚨',
        'filters': ['Pronto', 'Emergência']
    },
    {
        'name': '🏥 UTI',
        'icon': '🏥',
        'filters': ['Terapia Intensiva', 'UTI']
    },
    {
        'name': '🔪 Cirurgia',
        'icon': '🔪',
        'filters': ['Cirurgia', 'Transplante', 'Vascular', 'Neurocirurgia']
    },
    {
        'name': '👶 Obstetrícia',
        'icon': '👶',
        'filters': ['Gineco', 'Obstet', 'Neonatal', 'Parto']
    },
    {
        'name': '⚕️ Clínica',
        'icon': '⚕️',
        'filters': ['Clínica', 'Hospitalista', 'Comanejo']
    },
    {
        'name': '🩺 Ambulatório',
        'icon': '🩺',
        'filters': ['Ambulatório', 'Oncologia']
    },
    {
        'name': '📚 Residência',
        'icon': '📚',
        'filters': ['Residência', 'Residencia']
    }
]

# Nota: Criar views via API do Notion é limitado
# As views precisam ser criadas manualmente no Notion
# Mas podemos criar um guia automático

print("⚠️  NOTA IMPORTANTE:")
print("A API do Notion não permite criar views programaticamente.")
print("Mas vou criar um arquivo de configuração que você segue passo-a-passo.\n")

# Gerar arquivo de instrução
instruction_file = '/Users/joaoperes/escalaHRO/CRIAR_VIEWS_PASSO_A_PASSO.md'

content = """# 📱 Guia: Criar Views Filtradas no Notion (Passo-a-Passo)

## Por que criar views separadas?

A tabela única mistura todas as especialidades, deixando confuso.
Com views filtradas, você vê apenas uma especialidade por aba.

---

## 🚀 Como Criar (5 minutos)

### PASSO 1: Abra seu Database no Notion
1. Vá para "Escala HRO" no seu Notion
2. Clique em "+ Adicionar uma view" (canto superior direito)

### PASSO 2: Crie a View "🚨 Emergência"
1. **Nome:** 🚨 Emergência
2. **Tipo:** Tabela
3. **Depois de criar**, clique em **"Filtro"** (no topo)
4. **Adicione filtro:**
   - Campo: **Setor**
   - Condição: **contém**
   - Valor: **Pronto**
5. **Adicione outro filtro (com OR):**
   - Campo: **Setor**
   - Condição: **contém**
   - Valor: **Emergência**
6. **Aplicar filtro**

---

### PASSO 3: Crie a View "🏥 UTI"
1. **Nome:** 🏥 UTI
2. **Tipo:** Tabela
3. **Filtros (com OR entre eles):**
   - Setor contém "Terapia Intensiva"
   - OU Setor contém "UTI"

---

### PASSO 4: Crie a View "🔪 Cirurgia"
1. **Nome:** 🔪 Cirurgia
2. **Tipo:** Tabela
3. **Filtros (com OR entre eles):**
   - Setor contém "Cirurgia"
   - OU Setor contém "Transplante"
   - OU Setor contém "Vascular"
   - OU Setor contém "Neurocirurgia"

---

### PASSO 5: Crie a View "👶 Obstetrícia"
1. **Nome:** 👶 Obstetrícia
2. **Tipo:** Tabela
3. **Filtros (com OR entre eles):**
   - Setor contém "Gineco"
   - OU Setor contém "Obstet"
   - OU Setor contém "Neonatal"

---

### PASSO 6: Crie a View "⚕️ Clínica"
1. **Nome:** ⚕️ Clínica
2. **Tipo:** Tabela
3. **Filtros (com OR entre eles):**
   - Setor contém "Clínica"
   - OU Setor contém "Hospitalista"
   - OU Setor contém "Comanejo"

---

### PASSO 7: Crie a View "🩺 Ambulatório"
1. **Nome:** 🩺 Ambulatório
2. **Tipo:** Tabela
3. **Filtros (com OR entre eles):**
   - Setor contém "Ambulatório"
   - OU Setor contém "Oncologia"

---

### PASSO 8: Crie a View "📚 Residência"
1. **Nome:** 📚 Residência
2. **Tipo:** Tabela
3. **Filtro:**
   - Setor contém "Residência"

---

## 🎨 (Opcional) Customizações

### Ocultar colunas desnecessárias
Em cada view, você pode ocultar colunas:
1. Clique em **⚙️ Propriedades** (topo direita)
2. Desmarque as colunas que não quer ver
3. **Recomendação:** Deixe visível apenas:
   - ✓ Data
   - ✓ Profissional
   - ✓ Setor
   - ✓ Período
   - ✗ Observações (oculte para ganhar espaço)

### Adicionar cor às views (Visual)
1. Clique nos 3 pontinhos (...) próximo ao nome da view
2. Clique em "Editar view"
3. Procure por "Cor" ou "Ícone"
4. Configure uma cor diferente para cada view

### Reordenar views
Você pode arrastar as abas para reordenar:
```
[🚨 Emergência] [🏥 UTI] [🔪 Cirurgia] [👶 Obstetrícia] [⚕️ Clínica] [🩺 Ambulatório] [📚 Residência]
```

---

## ✅ Resultado Final

Depois disso, seu Notion ficará assim:

```
┌─────────────────────────────────────────────────────────────────┐
│ Escala HRO                                                      │
├─────────────────────────────────────────────────────────────────┤
│ [🚨 Emergência] [🏥 UTI] [🔪 Cirurgia] [👶 Obstetrícia] ...   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Mostrando apenas registros de Emergência (10 profissionais)     │
│                                                                 │
│ Data | Profissional | Setor | Período | Observações            │
│ ...                                                             │
```

---

## 🎯 Vantagens

✅ Muito mais **claro e organizado**
✅ Cada especialidade em uma aba diferente
✅ Fácil de **buscar e filtrar**
✅ Não fica **confuso** com tudo misturado
✅ Cada aba tem **sua cor** para identificação rápida

---

## 💡 Dica Extra

Se quiser uma alternativa **ainda mais visual**, use o Dashboard HTML:
```
/tmp/escala_hro_dashboard.html
```

O Dashboard é ainda **mais bonito e rápido**!

---

**Pronto!** Seu Notion ficará muito melhor organizado! 🎉
"""

with open(instruction_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Arquivo de instruções criado:")
print(f"📄 {instruction_file}\n")

print("📋 RESUMO DAS VIEWS A CRIAR:\n")

for view in views:
    print(f"{view['icon']} {view['name']}")
    print(f"   Filtros: {', '.join(view['filters'])}\n")

print("\n" + "="*100)
print("🚀 PRÓXIMO PASSO:")
print("="*100)
print(f"\n1. Abra: {instruction_file}")
print("2. Siga o guia passo-a-passo")
print("3. Crie as 7 views no seu Notion")
print("\nIsso levará apenas 5-10 minutos!")
print("Depois, seu Notion ficará MUITO mais organizado! 🎉\n")
