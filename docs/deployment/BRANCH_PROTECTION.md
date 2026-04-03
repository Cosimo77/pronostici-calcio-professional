# Branch Protection Configuration

Configurazione da applicare manualmente su GitHub per il branch `main`:

## Settings → Branches → Branch Protection Rules

### Rule: Protect main branch

**Branch name pattern**: `main`

#### Required Status Checks
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging

**Status checks required**:
- `test / Run Tests`
- `lint / Code Quality`
- `security / Security Scan`

#### Merge Requirements
- ✅ Require a pull request before merging
- Require approvals: `1` (opzionale per progetti personali)
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require review from Code Owners (opzionale)

#### Additional Settings
- ✅ Require conversation resolution before merging
- ✅ Include administrators (enforce rules on admins)
- ✅ Allow force pushes: ❌ (disabled)
- ✅ Allow deletions: ❌ (disabled)

---

## Quick Setup Steps

1. Vai su: https://github.com/Cosimo77/pronostici-calcio-professional/settings/branches
2. Click "Add branch protection rule"
3. Branch name pattern: `main`
4. Attiva:
   - ✅ Require status checks to pass before merging
   - Seleziona: `test / Run Tests`, `lint / Code Quality`, `security / Security Scan`
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators
5. Click "Create" o "Save changes"

---

## Verifica Configurazione

Dopo commit + push, verifica che:
- GitHub Actions si avviano automaticamente (tab Actions)
- Badge nel README mostrano status green
- Branch protection impedisce merge se test falliscono

---

## Coverage Gate Configuration

Il workflow `test.yml` include:
```yaml
--cov-fail-under=30
```

Questo fallisce la CI se coverage < 30%. Modifica valore se necessario.
