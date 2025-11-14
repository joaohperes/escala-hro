# System Architecture - Anterior Data Flow

## Problem Solved
Fixed recurrent "Dia Anterior" (previous day schedule) showing stale data.

## Data Flow Architecture

### ✅ CORRECT FLOW (Current Implementation)

```
GitHub Actions Execution
│
├─ Step 1: Cleanup /tmp
│  └─ Removes: /tmp/extracao*.json, /tmp/escalas*.json
│  └─ Reason: Prevents stale file accumulation
│
├─ Step 2: Run Extraction Script
│  └─ Extracts TODAY's data from website
│  └─ Saves to: /tmp/extracao_inteligente.json (ephemeral)
│
├─ Step 3: Load Previous Day Data
│  ├─ Source Priority:
│  │  1. data/extracao_inteligente_anterior_cache.json (PERSISTENT)
│  │     └─ Check: Is data exactly 1 day old? → USE
│  │     └─ Check: Is data from today (updated today)? → USE anterior field
│  │     └─ Check: Is data >2 days old? → REJECT, use fallback
│  │  
│  │  2. data/extracao_inteligente_anterior_fallback.json (BACKUP)
│  │     └─ Only if cache is stale or missing
│  │  
│  │  3. None
│  │     └─ First run or everything failed
│  │
│  └─ /tmp is IGNORED (never checked for anterior)
│
├─ Step 4: Build Rolling Window
│  ├─ atual: Today's data (fresh from extraction)
│  └─ anterior: Yesterday's data (from persistent cache)
│
├─ Step 5: Save Rolling Window
│  ├─ /tmp/extracao_inteligente.json (ephemeral, for this run)
│  ├─ data/extracao_inteligente_anterior_cache.json (persistent, for next run)
│  └─ data/extracao_inteligente_anterior_fallback.json (fallback update)
│
├─ Step 6: Generate Dashboard
│  └─ Embeds rolling window data into HTML
│  └─ Result: Dashboard shows correct atual + anterior
│
└─ Step 7: Commit & Deploy
   └─ Push to GitHub → Vercel deploys automatically
```

## Storage Strategy

### Persistent Storage (data/)
```
data/extracao_inteligente_anterior_cache.json
├─ Survives between workflows ✓
├─ Contains rolling window: { atual: {...}, anterior: {...} }
├─ Updated daily by workflow
└─ Single source of truth for anterior data

data/extracao_inteligente_anterior_fallback.json
├─ Also survives between workflows ✓
├─ Backup copy of previous day's data
├─ Used only if cache is stale/missing
└─ Provides resilience
```

### Ephemeral Storage (/tmp)
```
/tmp/extracao_inteligente.json
├─ Fresh extraction (today's data)
├─ Cleaned at start of each workflow
├─ NOT used to load anterior (prevents stale accumulation)
└─ Only used as output for dashboard generation

/tmp/extracao_inteligente_anterior.json
├─ DEPRECATED (no longer used)
├─ Used to be checked first (BUG!)
├─ Removed from loading logic
└─ Now cleaned automatically by workflow
```

## Data Age Validation

```python
# How age is determined
dias_diff = (datetime.now() - data_from_file).days

# Decision logic
if dias_diff == 1:
    # Perfect! Yesterday's data
    USE resultado_anterior_salvo
    
elif dias_diff == 0:
    # Cache was updated today
    # Use 'anterior' field instead of 'atual'
    USE resultado_anterior_salvo = cache['anterior']
    
elif dias_diff > 2:
    # Data is stale (>2 days)
    REJECT and load fallback
    print(f"⚠️  REJEITAR: Arquivo anterior muito antigo ({dias_diff} dias)")
    
else:
    # dias_diff is 2 or between 0-2 (excluding 0 and 1)
    WARN but USE (acceptable)
```

## Fallback Mechanism

```
Primary Source Fails?
│
├─ /tmp is ignored anyway (never checked)
├─ data/extracao_inteligente_anterior_cache.json doesn't exist?
│  └─ Try: data/extracao_inteligente_anterior_fallback.json
│
├─ Both missing?
│  └─ First execution or disaster
│  └─ anterior = empty array
│  └─ Dashboard shows "Sem dados do dia anterior"
│
└─ Fallback file missing?
   └─ Use: data/extracao_inteligente_sample.json
   └─ Sample data included in repo
```

## Why This Works

### 1. Persistent Storage First
- `data/` files survive GitHub Actions cleanup
- Not dependent on ephemeral /tmp

### 2. Clean Start
- /tmp cleaned before each execution
- Prevents accumulation of old files

### 3. Age Validation
- Rejects data older than 2 days
- Logs clearly when rejecting

### 4. No Circular Dependency
- /tmp is output only, never input for anterior
- Breaks the vicious cycle

### 5. Cascading Fallback
- Primary → Fallback → None
- System keeps running even if primary fails


## Example Timeline

### Day 14 (Thursday)
```
Morning Workflow:
├─ /tmp cleanup: Remove old files
├─ Extract: Day 14 data → /tmp/extracao_inteligente.json
├─ Load anterior: data/ has day 13 (yesterday)
├─ Save rolling window: atual=day14, anterior=day13
├─ Generate dashboard: Shows day 14 (atual) + day 13 (anterior)
└─ Result: ✅ CORRECT
```

### Day 15 (Friday)
```
Morning Workflow:
├─ /tmp cleanup: Remove old files (including day 14 data)
├─ Extract: Day 15 data → /tmp/extracao_inteligente.json
├─ Load anterior: data/ has day 14 (now anterior from yesterday's save)
├─ Validation: dias_diff = 1 ✓ Perfect!
├─ Save rolling window: atual=day15, anterior=day14
├─ Generate dashboard: Shows day 15 (atual) + day 14 (anterior)
└─ Result: ✅ CORRECT
```

### Day 16 (Saturday)
```
Same as Day 15...
└─ Result: ✅ CORRECT (cycle continues forever)
```

## Key Differences: Before vs After

### ❌ BEFORE (Broken)
```
Load anterior from: /tmp (checked FIRST)
                     ↓ (persists between runs)
                     ↓ (accepted without age check)
                     → Corrupts data/ cache
                     → Dashboard shows stale
                     → Next run uses even older data
                     → Problem gets worse each day
```

### ✅ AFTER (Fixed)
```
Load anterior from: /tmp → IGNORED
                    data/ → CHECK FIRST (persistent)
                            ├─ Age check: >2 days? REJECT
                            ├─ Too old? Use fallback
                            └─ Valid? Use it
                    fallback → Fallback file
                              └─ Last resort
```

## Files Involved

```
Code:
├─ extracao_inteligente.py (extraction + rolling window logic)
└─ .github/workflows/daily-escala.yml (cleanup + orchestration)

Data:
├─ data/extracao_inteligente_anterior_cache.json (persistent rolling window)
├─ data/extracao_inteligente_anterior_fallback.json (fallback copy)
├─ data/extracao_inteligente_sample.json (sample data for emergency)
├─ /tmp/extracao_inteligente.json (ephemeral extraction output)
└─ /tmp/extracao_inteligente_anterior.json (DEPRECATED - cleaned away)

Documentation:
├─ ANTERIOR_DATA_FIX.md (full explanation)
├─ QUICKFIX_REFERENCE.md (quick guide)
└─ ARCHITECTURE.md (this file)
```

## Monitoring & Debugging

### Check if system is working correctly
```bash
# 1. Verify cache freshness
python3 -c "import json; d=json.load(open('data/extracao_inteligente_anterior_cache.json')); print('Atual:', d['atual']['data'], '|', 'Anterior:', d['anterior']['data'])"

# 2. Check if /tmp is clean
ls /tmp/extracao* 2>/dev/null || echo "✅ Clean!"

# 3. Verify workflow cleanup step
grep -A5 "Limpar" .github/workflows/daily-escala.yml

# 4. Check dashboard has both days
grep -c "novembro 2025" index.html
```

### If something goes wrong
1. Check workflow logs: Look for "REJEITAR" or cleanup messages
2. Check cache file: Is anterior date reasonable?
3. Check fallback: Is fallback file up to date?
4. Manual fix: Read ANTERIOR_DATA_FIX.md → "Future Prevention"

