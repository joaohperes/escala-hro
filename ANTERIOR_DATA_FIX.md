# Fix: Recurrent Anterior Data Error

## Problem Summary
The "Dia Anterior" tab was showing stale data (days or even weeks old) instead of yesterday's schedule.

## Root Cause
**The issue was a perfect storm of three problems:**

1. **GitHub Actions doesn't clean /tmp between executions**
   - Old files like `/tmp/extracao_inteligente_anterior.json` persisted
   - These files might be days old but still existed

2. **Extraction script prioritized /tmp over persistent cache**
   ```python
   # WRONG (old code):
   arquivo_para_carregar = arquivo_anterior if os.path.exists(arquivo_anterior) else arquivo_anterior_persistente
   # This checked /tmp FIRST!
   ```

3. **No age validation for /tmp files**
   - Script accepted ANY data in /tmp as valid
   - Even 2-week-old data was used as "yesterday"

## Why It Was Recurrent
This created a **vicious cycle**:
```
Day 1: /tmp has day N data
Day 2: Script loads day N from /tmp
       → Saves it as anterior in data/
       → Dashboard shows day N (wrong!)
       → /tmp still has day N data
Day 3: Script loads day N+1 from /tmp (tomorrow's data from previous run)
       → Saves it as anterior (wrong again!)
       → Problem gets worse each day
```

## Solution Implemented

### 1. Remove /tmp as Primary Source
```python
# NEW (correct code):
# ONLY load from persistent cache (data/)
# DO NOT load from /tmp (ephemeral)
if os.path.exists(arquivo_anterior_persistente):
    arquivo_para_carregar = arquivo_anterior_persistente
```

### 2. Add Cleanup Step to Workflow
```yaml
- name: Limpar arquivos antigos de /tmp
  run: |
    rm -f /tmp/extracao_inteligente*.json
    rm -f /tmp/escalas*.json
```

### 3. Strengthen Data Validation
```python
# Reject data older than 2 days
elif dias_diff > 2:
    print(f"⚠️  REJEITAR: Arquivo anterior muito antigo ({dias_diff} dias)")
    resultado_anterior_salvo = None
    # Fall back to other sources
```

## Architecture Changes

### Before (Problematic)
```
GitHub Actions Execution
├─ Extract data → /tmp/extracao_inteligente.json (NEW)
├─ Load anterior → /tmp/extracao_inteligente_anterior.json (STALE!)
├─ Save cache → data/extracao_inteligente_anterior_cache.json (CORRUPTED with stale data)
└─ Dashboard uses corrupted cache
```

### After (Correct)
```
GitHub Actions Execution
├─ Cleanup /tmp (remove stale files)
├─ Extract data → /tmp/extracao_inteligente.json (NEW)
├─ Load anterior → data/extracao_inteligente_anterior_cache.json (FRESH!)
│  └─ If stale: use fallback
│  └─ If missing: use fallback
├─ Save cache → data/extracao_inteligente_anterior_cache.json (CORRECT)
└─ Dashboard uses correct data
```

## Files Changed
- `extracao_inteligente.py` - Removed /tmp dependency, strengthened validation
- `.github/workflows/daily-escala.yml` - Added /tmp cleanup step
- `data/extracao_inteligente_anterior_cache.json` - Restored with correct day 13 data
- `data/extracao_inteligente_anterior_fallback.json` - Restored with correct fallback

## Testing
After this fix, the system has:
✅ Clean /tmp at start of each workflow
✅ Only uses persistent cache (data/)
✅ Age validation (rejects >2 day old data)
✅ Fallback mechanism if cache is missing
✅ Clear separation: /tmp = ephemeral, data/ = persistent

## Future Prevention
If you need to debug anterior data issues:

1. **Check cache freshness**
   ```bash
   python3 -c "import json; d=json.load(open('data/extracao_inteligente_anterior_cache.json')); print('Atual:', d['atual']['data']); print('Anterior:', d['anterior']['data'])"
   ```

2. **Verify /tmp is clean**
   ```bash
   ls /tmp/extracao* 2>/dev/null || echo "Clean!"
   ```

3. **Check extraction logs**
   Look for lines like: "REJEITAR: Arquivo anterior muito antigo"

## Lessons Learned
- ❌ Never trust ephemeral storage (/tmp) as primary state
- ✅ Always validate data age before using it
- ✅ Use persistent storage (data/) as source of truth
- ✅ Clean up ephemeral files at workflow start
- ✅ Have multiple fallback mechanisms
