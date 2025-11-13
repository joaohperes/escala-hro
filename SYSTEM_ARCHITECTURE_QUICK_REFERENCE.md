# System Architecture - Quick Reference Guide

## Project Overview

**Hospital Regional do Oeste (HRO) - Medical Schedule Dashboard**
- **Type**: Automated schedule extraction + web dashboard
- **Data Source**: escala.med.br (via Selenium automation)
- **Published**: GitHub Pages (index.html)
- **Update Frequency**: Daily (automated + manual)

---

## File Organization

```
escalaHRO/
├── 📊 DASHBOARDS (Published & Generated)
│   ├── index.html                    [2,599 lines] MAIN - Published to GitHub Pages
│   ├── dashboard_final.html          [1,386 lines] Reference/Documentation
│   └── dashboard_executivo.html      [1,724 lines] Generated artifact (not used)
│
├── 📄 DATA FILES (Source of Truth)
│   ├── escalas_multiplos_dias.json   [Fallback schedule data, stale]
│   ├── profissionais_autenticacao.json [~100 professionals, auth data]
│   ├── ramais_hro.json               [Hospital extensions directory]
│   └── setor_ramais_mapping.json     [Sector→Department mapping]
│
├── 🐍 PYTHON SCRIPTS (Processing)
│   ├── extracao_inteligente.py       [Extract from escala.med.br] ★ CRITICAL
│   ├── gerar_dashboard_executivo.py  [Generate HTML, 3,200 lines]
│   ├── update_dashboard.py           [Orchestrate extraction+generation]
│   ├── update_escala_data_only.py    [Update JSON in HTML, safer]
│   ├── fix_previous_day.py           [Manual rolling window fix]
│   ├── extract_ramais_pdf.py         [Extract from PDF, unused]
│   └── publicar_notion.py            [Publish to Notion, unused]
│
├── ⚙️ AUTOMATION (GitHub Actions)
│   ├── .github/workflows/atualizar-dashboard.yml   [Daily 07:01 UTC, broken]
│   └── .github/workflows/daily-escala.yml          [Daily 07:00 UTC, conflicts]
│
├── 📚 DOCUMENTATION
│   ├── README_DASHBOARD.md           [How to update manually]
│   ├── GUIA_RAPIDO_ATUALIZACAO.md   [Quick update guide]
│   ├── ROLLING_WINDOW_LOGIC.md      [Dia Anterior mechanism]
│   ├── PORQUE_ESTE_E_O_ARQUIVO_FINAL.md [Why dashboard_final.html]
│   └── COMPREHENSIVE_SYSTEM_ANALYSIS.md [This analysis!]
│
├── 📦 TEMPORARY FILES (GitHub Actions only, not committed)
│   ├── /tmp/extracao_inteligente.json           [Today's extraction]
│   ├── /tmp/extracao_inteligente_anterior.json  [Tomorrow's "Dia Anterior"]
│   └── /tmp/dashboard_executivo.html            [Generated HTML]
│
└── ⚙️ CONFIG
    ├── .env                         [Credentials, not in repo]
    ├── .env.example                 [Template]
    ├── requirements.txt             [Python dependencies]
    └── _config.yml                  [Jekyll config]
```

---

## Daily Update Flows

### Current Reality (BROKEN - Race Condition)

```
10:00 UTC (Daily)
├─ atualizar-dashboard.yml
│  └─ Extract → converter_inteligente.py [❌ FILE MISSING]
│
└─ daily-escala.yml
   └─ Extract → Generate → Commit
   
PROBLEM: Both run simultaneously, race condition!
```

### Recommended Single Flow

```
07:00 UTC (Daily)
Extract (extracao_inteligente.py)
  ├─ Login to escala.med.br
  ├─ Get today's schedule
  ├─ Load yesterday's data (rolling window)
  └─ Save: /tmp/extracao_inteligente.json
         
  ↓
  
Update Data (update_escala_data_only.py)
  ├─ Read extraction JSON
  ├─ Find "const escalas = {...}" in index.html
  ├─ Replace ONLY the JSON
  └─ Save: index.html
  
  ↓
  
Commit & Push
  ├─ git add index.html
  ├─ git commit "Update: escalas MM-DD HH:MM"
  └─ git push origin main
```

---

## Data Flow Diagram

```
┌─────────────────────┐
│  escala.med.br      │
│  (Web Schedule)     │
└──────────┬──────────┘
           │
           │ Selenium automation
           ▼
┌─────────────────────────────────────┐
│ extracao_inteligente.py             │
│ ├─ Login + Extract schedule         │
│ ├─ Load /tmp/..._anterior.json      │
│ ├─ Use as "anterior"                │
│ └─ Save /tmp/extracao_inteligente   │
└──────────┬──────────────────────────┘
           │
           │ JSON (atual + anterior)
           ▼
    ┌──────────────────────────────────────────┐
    │ Option A: gerar_dashboard_executivo.py   │
    │ (Generate full HTML, 3,200 lines)        │
    │                                          │
    │ Option B: update_escala_data_only.py     │
    │ (Update JSON only, 95 lines) ← BETTER    │
    └──────────┬───────────────────────────────┘
               │
               │ HTML with data
               ▼
        ┌──────────────────┐
        │   index.html     │
        │  Published via   │
        │  GitHub Pages    │
        └──────────────────┘
```

---

## Rolling Window Mechanism (Dia Anterior)

### How Yesterday's Schedule Appears

```
Day 1 (Nov 5):
  Extract → /tmp/extracao_inteligente.json
    {atual: Nov 5, anterior: empty}
  
  Backup → /tmp/extracao_inteligente_anterior.json
    {atual: Nov 5} ← Ready for tomorrow

Day 2 (Nov 6):
  Load backup → /tmp/extracao_inteligente_anterior.json
    Has {atual: Nov 5}
  
  Extract → /tmp/extracao_inteligente.json
    {atual: Nov 6, anterior: Nov 5} ✅ Automatic!
  
  Backup → /tmp/extracao_inteligente_anterior.json
    {atual: Nov 6} ← Ready for next day
```

### ⚠️ Critical Risk: /tmp Files Are Ephemeral

**What Could Break It**:
1. GitHub Actions runner restart
2. /tmp cleanup between runs
3. Different runner assigned (new /tmp)

**Solution**: Commit backup files to repo

---

## Key Components Explained

### 1. extracao_inteligente.py (The Extractor)
- **What**: Logs in to escala.med.br via Selenium
- **How**: JavaScript X-coordinate based sector detection
- **Output**: `/tmp/extracao_inteligente.json` (today + yesterday)
- **Reliability**: ⭐⭐⭐⭐⭐ Robust with fallback selectors

### 2. index.html (The Dashboard)
- **What**: Published schedule viewer
- **Features**: Dark theme, authentication, search, sector grouping
- **Size**: 2,599 lines, ~164 KB
- **Updates**: Daily OR manual edits
- **Problem**: Two ways to update it → confusion

### 3. gerar_dashboard_executivo.py (The Generator)
- **What**: Converts JSON to HTML dashboard
- **Size**: 3,211 lines (huge!)
- **Problem**: Hard to maintain, fragile
- **Alternative**: update_escala_data_only.py (95 lines)

### 4. Rolling Window Backup
- **What**: Yesterday's schedule shown as "Dia Anterior"
- **How**: Backup file read next day
- **Problem**: Backup in /tmp (ephemeral)
- **Fix**: Commit to repo

### 5. GitHub Actions Workflows
- **atualizar-dashboard.yml**: Calls missing converter, does nothing
- **daily-escala.yml**: Actually updates dashboard
- **Problem**: Both run at same time → race condition

---

## Critical Issues at a Glance

| Issue | Severity | Impact | Status |
|-------|----------|--------|--------|
| Missing converter_inteligente.py | 🔴 HIGH | Workflow fails silently | Unfixed |
| Two workflows race condition | 🔴 HIGH | Unpredictable commits | Unfixed |
| /tmp rolling window backup | 🔴 CRITICAL | Data loss on runner reset | Unfixed |
| 3,200-line generator | 🟡 MEDIUM | Hard to maintain | Workaround exists |
| Multiple HTML files | 🟡 MEDIUM | Version confusion | Unclear |
| No validation | 🟡 MEDIUM | Bad HTML published | Unfixed |
| Silent failures | 🟡 MEDIUM | Undetected breakage | Unfixed |

---

## Quick Decision Tree

### "I need to fix a bug in the dashboard"

```
Is it in HTML/CSS/JavaScript?
├─ YES → Edit index.html directly
│        Git add, commit, push
└─ NO → Data from schedule

Is it in the schedule data?
├─ YES → Run: python3 extracao_inteligente.py
│        Then: python3 update_escala_data_only.py
└─ NO → Check professional authentication data

Is it in professional info?
├─ YES → Edit profissionais_autenticacao.json
│        Update embedded profissionaisData in index.html
└─ NO → Check sector-department mapping
```

### "Dashboard didn't update today"

```
1. Check if extraction ran:
   ls -l /tmp/extracao_inteligente.json

2. Check if it has data:
   python3 << 'EOF'
   import json
   with open('/tmp/extracao_inteligente.json') as f:
       d = json.load(f)
       print(f"Atual: {d['atual']['total']} registros")
       print(f"Anterior: {d['anterior']['total']} registros")
   EOF

3. Check workflow status:
   GitHub repo → Actions → Latest run

4. Manual update:
   python3 update_escala_data_only.py
```

### "Dia Anterior is empty"

```
1. Check backup file:
   ls -l /tmp/extracao_inteligente_anterior.json

2. If missing:
   # Rolling window broke, recreate from git
   python3 fix_previous_day.py

3. Verify it's fixed:
   python3 << 'EOF'
   import json
   with open('/tmp/extracao_inteligente.json') as f:
       d = json.load(f)
       print(f"Anterior data: {d['anterior']['data']}")
   EOF
```

---

## What's Working ✅ vs Broken ❌

### Dashboard Features (All Working!)
- ✅ Dark theme UI
- ✅ Authentication (email or last4 digits)
- ✅ Two-day view (today + previous day)
- ✅ Professional search
- ✅ Sector grouping
- ✅ Turno classification (colors)
- ✅ Mobile responsive
- ✅ Contact/extension modals

### Data Extraction (All Working!)
- ✅ Login to escala.med.br
- ✅ Extract schedule data
- ✅ 90+ professionals per day
- ✅ Sector detection
- ✅ Rolling window mechanism
- ✅ Fallback selectors

### Automation (Some Broken!)
- ❌ converter_inteligente.py missing
- ❌ Race condition between workflows
- ❌ /tmp files lost on runner restart
- ⚠️ Generator script 3,200 lines (unused)
- ⚠️ Multiple conflicting update methods

### Data Sync (Some Manual)
- ⚠️ Professional list manual only
- ⚠️ Sector-ramais mapping manual
- ⚠️ Extension directory manual
- ⚠️ Notion publishing not automated

---

## Files You Can Safely Edit

### For Updates
```bash
# Update schedule data only
python3 update_escala_data_only.py

# Update professional list
# Edit profissionais_autenticacao.json

# Update extensions
# Edit ramais_hro.json

# Update sector mapping
# Edit setor_ramais_mapping.json
```

### For Styling/Features
```bash
# Edit index.html directly
# Change anything in <style> or <script>
# CSS changes, JavaScript fixes, HTML structure
```

### DO NOT EDIT
```bash
# ❌ Do not edit dashboard_final.html
#    It's reference only, workflow doesn't use it

# ❌ Do not edit gerar_dashboard_executivo.py
#    It's not used by active workflow

# ❌ Do not edit dashboard_executivo.html
#    It's generated, changes will be lost
```

---

## Estimated Fix Times

| Task | Time | Difficulty | Impact |
|------|------|-----------|--------|
| Remove converter from workflow | 5 min | Easy | High |
| Consolidate workflows | 15 min | Easy | High |
| Commit rolling window files | 20 min | Medium | Critical |
| Add validation script | 1 hour | Medium | Medium |
| Replace generator with injector | 2 hours | Medium | High |
| Implement git-based rolling window | 1 hour | Medium | High |
| Add error alerting | 30 min | Medium | Medium |

**Total for all fixes**: ~5-6 hours

---

## Where to Get Help

**For schedule data issues**: Check escalas_multiplos_dias.json structure
**For extraction problems**: Review extracao_inteligente.py logs
**For display issues**: Check browser console (F12)
**For automation issues**: Review GitHub Actions logs
**For data sync**: Check which JSON files are current

---

**Last Updated**: Nov 8, 2025
**Maintainer**: Claude Code Analysis
**Status**: Complete Overview Provided

