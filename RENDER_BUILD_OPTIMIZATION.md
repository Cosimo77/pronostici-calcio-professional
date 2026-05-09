# 🚨 Render Build Minutes Optimization Plan

**Data**: 20 Aprile 2026
**Alert**: >70% utilizzo (350+/500 minuti free mensili)
**Rischio**: Addebito $5/1000 minuti extra

---

## 📊 Situazione Attuale

### Utilizzo Aprile 2026
- **Commit totali**: 94
- **Build minutes utilizzati**: >350 (70%+)
- **Rimanenti**: <150 minuti (~18 deploy residui)
- **Media per build**: ~8-9 minuti
- **Deploy stimati**: ~40-45 (da 94 commit)

### Problemi Identificati
1. ✅ **Auto-deploy su ogni push a `main`** (configurato su Render dashboard)
2. ⚠️ **Build command pesante**: `pip install + build_models_render.py`
3. ⚠️ **Nessuna cache Docker layer** (ricompila tutto ogni volta)
4. ⚠️ **Deploy anche per fix minori** (typo, docs, commenti)

---

## 🎯 Piano Ottimizzazione IMMEDIATO (Oggi)

### ✅ Azione 1: Disabilita Auto-Deploy (URGENTE)
**Dove**: Render Dashboard → Settings → Build & Deploy
**Cambia**: Auto-Deploy "On" → **"Off"**

**Impatto**: -90% deploy automatici
**Risparmio**: ~300 minuti/mese

**Workflow nuovo**:
```bash
# Deploy SOLO quando necessario
git commit -m "fix: importante"
git push origin main
# POI vai su Render dashboard e click "Manual Deploy" SOLO se necessario
```

### ✅ Azione 2: Deploy Solo su Tag/Release
**Implementa**: Strategia tag-based deployment

```bash
# Batch commits localmente
git commit -m "feat: funzionalità A"
git commit -m "fix: bug B"
git commit -m "perf: ottimizzazione C"

# Push senza deploy automatico
git push origin main

# Deploy SOLO quando pronto (es. fine giornata)
git tag v1.0.14
git push origin v1.0.14
# Manuale deploy su Render con tag v1.0.14
```

**Impatto**: Da 94 deploy/mese → ~10-15 deploy/mese
**Risparmio**: 80-120 minuti → 120-200 minuti totali (80% reduction)

### ✅ Azione 3: Ottimizza Build Command
**File**: `render.yaml`

```yaml
# ❌ PRIMA (lento)
buildCommand: pip install -r requirements.txt && python3 scripts/build_models_render.py

# ✅ DOPO (con cache)
buildCommand: |
  pip install --cache-dir /opt/render/.cache/pip -r requirements.txt && \
  python3 scripts/build_models_render.py --use-cached-models
```

**Impatto**: Build time 8-9 min → 4-5 min (-50%)
**Risparmio**: ~200 minuti/mese con 40 deploy

---

## 🛠️ Piano Ottimizzazione MEDIO TERMINE (Settimana)

### Azione 4: Skip Build per Commit Non-Critici
**Aggiungi**: Skip deploy marker in commit message

```bash
# Deploy skippato automaticamente
git commit -m "docs: aggiorna README [skip ci]"
git push origin main
# NO deploy triggered
```

**Configurazione**: Render dashboard → Build Filters
**Pattern skip**: Commit message con `[skip ci]`, `[ci skip]`, `[skip deploy]`

**Impatto**: -30% deploy inutili

### Azione 5: GitHub Actions Deploy Hook (Manuale)
**Crea**: Workflow deploy controllato

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Render
on:
  workflow_dispatch:  # SOLO manuale
    inputs:
      reason:
        description: 'Reason for deploy'
        required: true
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Render Deploy
        run: |
          curl -X POST https://api.render.com/deploy/srv-xxx?key=${{ secrets.RENDER_DEPLOY_HOOK }}
```

**Impatto**: Deploy controllato, no auto-trigger

### Azione 6: Preview Environments (Disabilita)
**Dove**: Render Dashboard → Preview Environments
**Cambia**: "Enabled" → **"Disabled"**

**Impatto**: Zero build su PR/branches
**Risparmio**: ~100 minuti/mese

---

## 📈 Monitoraggio e Limiti

### Custom Build Minute Limit (Raccomandato)
**Dove**: Render Dashboard → Billing → Pipeline Minutes
**Imposta**: Limite custom a **450 minuti/mese**

**Effetto**: Render PAUSA build quando raggiungi 450 min (invece di addebitare automaticamente)

### Dashboard Monitoring
**URL**: https://dashboard.render.com/billing/usage
**Controlla**: Settimanalmente (ogni lunedì)

### Alert Setup
**Configura**: Email alert al 80% utilizzo (400 min)

---

## 🎓 Best Practices Going Forward

### Strategia Deploy Efficace

**BATCH Commits**:
```bash
# Raccogli 3-5 fix/features
git commit -m "feat: feature A"
git commit -m "fix: bug B"
git commit -m "perf: optimization C"

# Push senza auto-deploy
git push origin main

# Deploy MANUALE 1 volta/giorno (fine giornata)
# Render Dashboard → Manual Deploy
```

**Deploy Frequency Target**:
- **Dev/Fix**: 2-3 deploy/settimana
- **Feature**: 1-2 deploy/settimana
- **Hotfix**: Deploy immediato (solo emergenze)
- **Target mensile**: 10-15 deploy (120-135 minuti vs 350+)

### Categorie Commit che NON richiedono deploy

1. **Docs**: README, markdown, commenti
2. **Tests**: Aggiunte test (se non modificano codice production)
3. **Config**: .gitignore, .editorconfig, pre-commit hooks
4. **Scripts locali**: Analisi, debug, verifiche

**Usa sempre** `[skip ci]` per questi commit!

---

## 💰 Risparmio Stimato

### Scenario Attuale (Aprile 2026)
- Deploy: ~45
- Minuti: ~360-400
- Costo: $0 (ma 70%+ utilizzo)

### Scenario Ottimizzato (Maggio 2026+)
- Deploy: ~12-15
- Minuti: ~100-120
- Costo: $0 (20-25% utilizzo)
- **Risparmio**: ~250 minuti/mese (**-70% utilizzo**)

### ROI
- **Tempo risparmiato**: Zero (deploy è automatico)
- **Soldi risparmiati**: $0-5/mese (evita addebiti extra)
- **Stabilità**: Meno deploy = meno rischio breaking changes

---

## ✅ Action Items IMMEDIATE (Oggi)

- [ ] **STEP 1**: Render Dashboard → Disabilita Auto-Deploy (**PRIORITÀ 1**)
- [ ] **STEP 2**: Testa deploy manuale con "Manual Deploy" button
- [ ] **STEP 3**: Imposta custom limit 450 minuti (safety)
- [ ] **STEP 4**: Push commit con `[skip ci]` per testare skip
- [ ] **STEP 5**: Documenta processo deploy in README

## ✅ Action Items SETTIMANA PROSSIMA

- [ ] Ottimizza `buildCommand` in render.yaml (cache pip)
- [ ] Crea workflow GitHub Actions per deploy manuale
- [ ] Disabilita Preview Environments
- [ ] Setup email alert 80% utilizzo

---

## 📚 Riferimenti

- **Render Docs**: https://render.com/docs/deploy-hooks
- **Build Minutes**: https://render.com/pricing#build-minutes
- **Skip CI**: https://render.com/docs/github-integration#skip-automatic-deploys
- **Custom Limits**: https://dashboard.render.com/billing/usage

---

**Note**: Implementare STEP 1 (disabilita auto-deploy) IMMEDIATAMENTE per evitare consumo ulteriore minuti prima di fine mese!
