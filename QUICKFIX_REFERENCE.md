# Quick Fix Reference - Anterior Data Error

## What Was Wrong
"Dia Anterior" showed stale data (days/weeks old) instead of yesterday's schedule.

## Why It Happened (3 Problems)
1. **GitHub Actions doesn't clean /tmp** → Old files stayed around
2. **Extraction script checked /tmp FIRST** → Used stale data from ephemeral storage
3. **No age validation** → Accepted any data, no matter how old

## The Vicious Cycle
```
Old file in /tmp → Load it as anterior → Save to cache → Use corrupted cache
→ Tomorrow repeat with even older data → Problem gets worse
```

## Permanent Fixes

### Fix 1: Remove /tmp Priority
```python
# WRONG: arquivo_para_carregar = arquivo_anterior if os.path.exists(arquivo_anterior)
# RIGHT: Only load from data/ (persistent)
if os.path.exists(arquivo_anterior_persistente):
    arquivo_para_carregar = arquivo_anterior_persistente
```

### Fix 2: Add Cleanup Step
```yaml
- name: Limpar arquivos antigos de /tmp
  run: |
    rm -f /tmp/extracao_inteligente*.json
    rm -f /tmp/escalas*.json
```

### Fix 3: Validate Data Age
```python
if dias_diff > 2:
    print(f"⚠️  REJEITAR: Arquivo anterior muito antigo ({dias_diff} dias)")
    # Use fallback instead
```

## Files Changed
- `extracao_inteligente.py` - Remove /tmp dependency
- `.github/workflows/daily-escala.yml` - Add cleanup step
- `ANTERIOR_DATA_FIX.md` - Full documentation

## How to Verify It Works

### Check cache freshness
```bash
python3 << 'EOF'
import json
d = json.load(open('data/extracao_inteligente_anterior_cache.json'))
print('Atual:', d['atual']['data'])
print('Anterior:', d['anterior']['data'])
EOF
```

### Check if /tmp is clean
```bash
ls /tmp/extracao* 2>/dev/null || echo "Clean!"
```

### Check workflow logs
Look for: "REJEITAR: Arquivo anterior muito antigo" or "Limpando /tmp"

## If It Happens Again
1. Verify /tmp cleanup step ran: `git log --oneline | grep clean`
2. Check cache file: `cat data/extracao_inteligente_anterior_cache.json | head -20`
3. If cache is corrupted: restore from git history or manually fix
4. Read: `ANTERIOR_DATA_FIX.md` for full details

## Key Learning
✅ **Never trust ephemeral storage (/tmp) as source of truth**
✅ **Always validate data age before using it**
✅ **Use persistent storage (data/) as single source of truth**
