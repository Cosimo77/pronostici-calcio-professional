# Branch Protection Rules - Configurazione Ottimale

## Configurazione Consigliata per `main` branch

### ⚠️ Nota Importante
Il repository è **privato** → le regole NON vengono enforce fino a upgrade GitHub Team/Enterprise.
**Soluzione**: Configura comunque (prepara infrastruktur per futuro) o rendi repository **pubblico**.

---

## 🔧 Configurazione Step-by-Step

### 1. Branch name pattern
```
main
```

### 2. Protect matching branches
✅ **ATTIVA** - Abilita protezione

---

### 3. Require a pull request before merging
❌ **DISATTIVA** (per progetti personali/solo)

**Motivo**:
- Solo developer → overhead inutile
- Se lavori con team → ✅ ATTIVA + "Require 1 approval"

---

### 4. ✅ Require status checks to pass before merging
✅ **ATTIVA** - CRITICO per CI/CD

**Configurazione**:
- ✅ Require branches to be up to date before merging
- **Select status checks** (dopo primo workflow run):
  - `test / Run Tests`
  - `lint / Code Quality`
  - `security / Security Scan`

**Beneficio**: Blocca merge se test/linting/security falliscono

---

### 5. Require conversation resolution before merging
❌ **DISATTIVA** (per progetti solo/personali)

Se team → ✅ ATTIVA

---

### 6. Require signed commits
❌ **DISATTIVA** (opzionale)

**Motivo**: Setup GPG key aggiuntivo, overhead per piccoli team

---

### 7. Require linear history
❌ **DISATTIVA** (permetti merge commits)

**Motivo**: Flessibilità, merge commits utili per tracking

---

### 8. Require deployments to succeed
❌ **DISATTIVA** (non configurato)

**Motivo**: Non abbiamo environment deploy su GitHub (usiamo Render)

---

### 9. Lock branch
❌ **DISATTIVA**

**Motivo**: Devi poter pushare su main

---

### 10. Do not allow bypassing the above settings
✅ **ATTIVA** - Apply to administrators

**Beneficio**: Anche tu devi seguire regole (best practice)

---

### 11. Allow force pushes
❌ **DISATTIVA** - IMPORTANTE

**Motivo**: Previene `git push --force` che rompe history

---

### 12. Allow deletions
❌ **DISATTIVA**

**Motivo**: Previene cancellazione accidentale branch main

---

## 📋 Configurazione Finale Consigliata

```
Branch name pattern: main

✅ Protect matching branches
❌ Require pull request (solo-dev, altrimenti ✅)
✅ Require status checks (CRITICO)
   ✅ Require branches up to date
   ✅ test / Run Tests
   ✅ lint / Code Quality
   ✅ security / Security Scan
❌ Require conversation resolution
❌ Require signed commits
❌ Require linear history
❌ Require deployments
❌ Lock branch
✅ Do not allow bypassing (include administrators)
❌ Allow force pushes
❌ Allow deletions
```

---

## 🚨 Problema Repository Privato

**Issue**: Regole non enforce su repository privato senza GitHub Team

**Opzioni**:

### Opzione A: Rendi Repository Pubblico
```bash
# Su GitHub UI:
Settings → General → Danger Zone → Change visibility → Make public
```

**Pro**:
- ✅ Branch protection funziona
- ✅ Badge README visibili
- ✅ CI/CD completamente funzionale
- ✅ Codecov free tier

**Contro**:
- Codice pubblico (non problematico per progetti open-source)

### Opzione B: Mantieni Privato
**Pro**:
- Privacy codice

**Contro**:
- ❌ Branch protection NON enforceable
- ❌ Badge GitHub Actions non visibili pubblicamente
- ❌ Configurazione inutile fino a upgrade Team

### Opzione C: Upgrade GitHub Team
**Costo**: $4/user/month
**Beneficio**: Branch protection + advanced features

---

## 🎯 Raccomandazione

**Per progetto personale/portfolio**: **Opzione A (Pubblico)**
- Sistema è production-ready, nessun rischio esposizione
- Mostra competenze CI/CD su portfolio
- Badge funzionanti su README
- Branch protection attivo

**Se hai dati sensibili**: **Opzione B (Privato)**
- Mantieni configurazione per futuro
- Usa disciplina personale per seguire workflow

---

## ✅ Quick Setup Commands

Dopo configurazione GitHub UI, verifica:

```bash
# Test locale che rispetta branch protection
git checkout -b feature/test-branch
# ... fai modifiche ...
git push origin feature/test-branch

# Su GitHub: crea PR (se enabled)
# Verifica: CI checks devono essere green prima merge
```

---

## 📊 Verifica Configurazione

Dopo save, verifica:

1. **Status checks visibili**: Dopo primo push/PR, vedi checks nella lista
2. **Merge bloccato**: Se test falliscono, merge disabilitato
3. **Badge README**: Verde se tutto OK

---

## 💡 Best Practice Aggiuntiva

Anche se branch protection NON è enforceable (repo privato), configura comunque:

**Benefici**:
1. Preparazione infrastruktur per futuro pubblico/team
2. Reminder visivo seguire workflow
3. Quick switch se rendi pubblico
4. Documentation best practices

---

**Next Action**: Decidi Opzione A/B/C, poi configura su GitHub UI
