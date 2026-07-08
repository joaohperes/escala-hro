# Rolling Window Logic - Dia Anterior (Previous Day) Automation

## Overview
The dashboard automatically maintains the previous day's schedule using a **rolling window** pattern. This means `Dia Anterior` is always automatically the previous day, without manual intervention.

## How It Works

### Daily Extraction Flow

**Day N (Example: Nov 6):**
1. Extract Nov 6 data from Notion via `extracao_inteligente.py`
2. Load `/tmp/extracao_inteligente_anterior.json` (contains Nov 5 data)
3. Use Nov 5 data as "anterior" (previous day)
4. Output: `ATUAL=Nov 6`, `ANTERIOR=Nov 5` ✅
5. Save this to `/tmp/extracao_inteligente.json`
6. Save Nov 6 data as backup in `/tmp/extracao_inteligente_anterior.json` for tomorrow

**Day N+1 (Example: Nov 7):**
1. Extract Nov 7 data from Notion
2. Load `/tmp/extracao_inteligente_anterior.json` (now contains Nov 6 data)
3. Use Nov 6 data as "anterior"
4. Output: `ATUAL=Nov 7`, `ANTERIOR=Nov 6` ✅

## Key Files

| File | Purpose | Updated | Used |
|------|---------|---------|------|
| `/tmp/extracao_inteligente.json` | Today's extraction (ATUAL + ANTERIOR) | Daily by extraction script | By dashboard generator |
| `/tmp/extracao_inteligente_anterior.json` | Backup of today's data for tomorrow | Daily by extraction script | Next day's extraction |

## Script Implementation Details

The `extracao_inteligente.py` script implements this logic (lines 443-504):

1. **Define backup file path (line 443)**
   - `arquivo_anterior = '/tmp/extracao_inteligente_anterior.json'`

2. **Load yesterday's data (lines 446-456)**
   - Check if backup file exists
   - Extract the "atual" field from backup
   - This becomes today's "anterior"

3. **Use yesterday's data as anterior (lines 477-486)**
   - If backup exists: `output['anterior'] = resultado_anterior_salvo`
   - If not (first run): create empty anterior

4. **Save today's data for tomorrow (lines 495-504)**
   - Create backup structure with today's "atual"
   - Save to `arquivo_anterior` for next day's extraction

## Manual Verification

Check if rolling window is properly set up:

```bash
python3 << 'EOF'
import json

# Check current extraction
with open('/tmp/extracao_inteligente.json', 'r') as f:
    current = json.load(f)
    print(f"Current ATUAL: {current['atual']['data']}")
    print(f"Current ANTERIOR: {current['anterior']['data']}")

# Check backup for tomorrow
with open('/tmp/extracao_inteligente_anterior.json', 'r') as f:
    backup = json.load(f)
    print(f"Tomorrow will use as ANTERIOR: {backup['atual']['data']}")
EOF
```

## Current Status (Nov 5, 2025)

- ✅ ATUAL: 05 novembro 2025 (92 professionals)
- ✅ ANTERIOR: 04 novembro 2025 (93 professionals)
- ✅ Backup prepared: Contains Nov 5 data for Nov 6

## What Happens Next

When `extracao_inteligente.py` runs on Nov 6:

1. Extracts Nov 6 data from Notion
2. Loads `/tmp/extracao_inteligente_anterior.json` (which has Nov 5)
3. Uses Nov 5 as `anterior`
4. **Result: Dashboard automatically shows Nov 6 (atual) + Nov 5 (anterior)**
5. No manual intervention needed! 🎉

## Edge Cases

### First-time setup or missing backup file
If `/tmp/extracao_inteligente_anterior.json` doesn't exist:
- Script creates empty anterior: `{"data": "N/A", "registros": []}`
- Next run will have proper data

### After restoring from git
If you restore the HTML files from git history:
1. Manual update the backup file with the correct previous day data
2. The extraction script will handle everything automatically from then on

### Testing the logic
You can manually simulate tomorrow's extraction without actually running it:
```bash
# Just copy current extraction to backup
cp /tmp/extracao_inteligente.json /tmp/extracao_inteligente_anterior.json
# Now when extraction runs, it will use this as anterior
```
