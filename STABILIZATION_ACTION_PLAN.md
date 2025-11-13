# Stabilization Action Plan
## Hospital Regional do Oeste - Medical Schedule Dashboard

**Document Date**: November 8, 2025
**Status**: Ready for Implementation
**Estimated Total Time**: 5-6 hours (can be done incrementally)

---

## Overview

Your dashboard system is **mature but fragile**. This document provides a step-by-step plan to fix critical issues and stabilize operations.

**Current Critical Issues**:
1. Missing converter_inteligente.py (workflow fails)
2. Two workflows running simultaneously (race condition)
3. Critical data in /tmp (lost on runner restart)
4. No validation or monitoring
5. Silent failures everywhere

**After implementing this plan**:
- Single, reliable daily workflow
- Persistent rolling window data
- Validation before publishing
- Error alerting
- Clear documentation

---

## Phase 1: IMMEDIATE FIXES (30 minutes)

### Issue 1: Remove Missing File from Workflow

**Problem**: atualizar-dashboard.yml tries to run converter_inteligente.py which doesn't exist

**Solution**: Remove from workflow

File: .github/workflows/atualizar-dashboard.yml
- Delete lines 42-44 (the converter step)
- After deletion, the workflow will only extract (no HTML generation)

Time: 5 minutes

### Issue 2: Fix the Race Condition

**Problem**: Both workflows run at 10:00 UTC, updating index.html simultaneously

**Solution**: Keep only daily-escala.yml, delete atualizar-dashboard.yml

Current state:
- atualizar-dashboard.yml: Extracts but doesn't update HTML (broken)
- daily-escala.yml: Extracts + generates + updates HTML (works)

Action: Delete atualizar-dashboard.yml
Reason: daily-escala.yml does everything needed

After:
- Single workflow at 10:00 UTC
- Extract → Generate → Commit
- Predictable results

File to delete: .github/workflows/atualizar-dashboard.yml
Time: 5 minutes

### Issue 3: Document Current Architecture

**Problem**: No clear documentation of what each file does

**Solution**: Use provided documentation files

Already done: COMPREHENSIVE_SYSTEM_ANALYSIS.md and SYSTEM_ARCHITECTURE_QUICK_REFERENCE.md created

Time: 0 minutes

---

## Phase 2: STABILIZE DATA (45 minutes)

### Issue 4: Move Rolling Window Data to Repository

**Problem**: /tmp/extracao_inteligente_anterior.json is ephemeral, lost on runner restart

**Solution**: Commit rolling window backup to repo

Actions:
1. Create data/rolling-window/ directory
2. Copy /tmp/extracao_inteligente_anterior.json to data/rolling-window/previous-day.json
3. Update extracao_inteligente.py line 443 to use repo location instead of /tmp

After:
1. Backup persists in git
2. No dependency on /tmp
3. Can restore from git history
4. Version controlled

Files to create/edit:
- Create: data/rolling-window/previous-day.json
- Edit: extracao_inteligente.py (line 443)

Time: 15 minutes

### Issue 5: Add Validation Before Commit

**Problem**: Bad HTML can be published without detection

**Solution**: Create validation script

The script should validate:
1. index.html exists
2. escalas JSON is valid
3. Current day has data (total > 0)
4. Required fields present
5. Auth data embedded
6. Extension data embedded

Integration:
- Add validation step to daily-escala.yml
- Only commit if validation passes
- Fail workflow if validation fails

Files to create/edit:
- Create: validate_dashboard.py
- Edit: .github/workflows/daily-escala.yml (add validation step)

Time: 30 minutes

---

## Phase 3: SIMPLIFY ARCHITECTURE (2 hours)

### Issue 6: Replace Large Generator with Data Injector

**Problem**: gerar_dashboard_executivo.py is 3,200 lines, fragile, hard to maintain

**Solution**: Use update_escala_data_only.py approach (95 lines, already exists!)

Current methods:
- gerar_dashboard_executivo.py (3,200 lines) - regenerate entire HTML
- update_escala_data_only.py (95 lines) - inject data only

Recommended: Use data injection approach

Why?
- Smaller codebase (95 vs 3,200 lines)
- Preserves all manual edits
- Faster execution
- Easier to debug
- Safer (less can break)

Workflow change:
Replace the gerar_dashboard_executivo.py call with update_escala_data_only.py

Files to edit:
- Edit: .github/workflows/daily-escala.yml (replace generator with injector)
- Keep: update_escala_data_only.py (already good)
- Optional: Delete gerar_dashboard_executivo.py (no longer needed)

Time: 30 minutes

### Issue 7: Improve Error Visibility

**Problem**: Failures are silent (continue-on-error: true everywhere)

**Solution**: Remove silent failures, add error notifications

Current (bad practice):
- continue-on-error: true hides failures

Better practice:
- Remove continue-on-error: true
- Workflow stops if step fails
- Failures visible in GitHub Actions
- Can add Slack notifications if desired

Files to edit:
- Edit: .github/workflows/daily-escala.yml
- Remove: All continue-on-error: true statements
- Add: Error notifications (optional)

Time: 20 minutes

---

## Phase 4: IMPROVE ROBUSTNESS (2+ hours, Optional)

### Issue 8: Document Data Source Priority

**Problem**: Multiple data sources, unclear which is authoritative

**Solution**: Document and enforce clear fallback order

Expected behavior:
1. Try: Fresh extraction from escala.med.br
2. Fallback: escalas_multiplos_dias.json (hardcoded data)
3. Fallback: Last known state from git
4. Fallback: Empty with warning

Files to review/document:
- Review: gerar_dashboard_executivo.py (data source logic)
- Create: DATA_SOURCES.md (document fallback order)

Time: 20 minutes

### Issue 9: Git-Based Rolling Window (Advanced)

**Problem**: Even with repo files, still vulnerable if repo not accessible

**Solution**: Read "anterior" from git history instead of file

Instead of reading backup file from /tmp/extracao_inteligente_anterior.json:
- git show HEAD~1:index.html
- Extract escalas object
- Use its atual as our anterior

Advantages:
- No /tmp dependency at all
- Self-documenting (in git history)
- No file loss possible
- Works across runners

Time: 1-1.5 hours

---

## Implementation Timeline

### Quick Start (30 min): High-Priority Fixes Only
Day 1:
- Remove missing converter (5 min)
- Delete atualizar-dashboard.yml (5 min)
- Read analysis docs (20 min)

Status: Workflows no longer conflict, system stable

### Standard (2.5 hours): Critical + Core Stabilization
Day 1: (30 min)
- Phase 1: Remove converter, delete workflow
- Push changes

Day 2: (45 min)
- Phase 2: Persist rolling window, add validation
- Push changes

Day 3: (1 hour 15 min)
- Phase 3: Replace generator, improve errors
- Push changes, test workflow

---

## Success Criteria

After implementation you should have:

Automation:
- Single daily workflow (no race condition)
- Reliable data extraction
- Automatic rolling window
- Validation before publishing

Data:
- Rolling window backup in repo (persistent)
- Clear fallback sources
- Version controlled history

Reliability:
- Error visibility (no silent failures)
- Validation before commit
- Graceful degradation

Maintainability:
- Single source of truth (index.html)
- Clear documentation
- Smaller codebase

---

## Next Steps

1. Read COMPREHENSIVE_SYSTEM_ANALYSIS.md (understand system)
2. Read SYSTEM_ARCHITECTURE_QUICK_REFERENCE.md (quick reference)
3. Implement Phase 1 (30 min - just remove/delete files)
4. Test next workflow run (automatic next day)
5. Implement Phase 2-3 as needed (incremental is fine)

---

**Created**: November 8, 2025
**Status**: Ready for Implementation
**Documents**: See COMPREHENSIVE_SYSTEM_ANALYSIS.md and SYSTEM_ARCHITECTURE_QUICK_REFERENCE.md

