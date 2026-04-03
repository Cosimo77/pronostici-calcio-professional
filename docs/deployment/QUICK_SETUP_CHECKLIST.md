# Quick Reference - Branch Protection Setup

## 🔗 URL Rapidi

1. **Rendi Pubblico**: https://github.com/Cosimo77/pronostici-calcio-professional/settings
2. **Branch Protection**: https://github.com/Cosimo77/pronostici-calcio-professional/settings/branches
3. **GitHub Actions**: https://github.com/Cosimo77/pronostici-calcio-professional/actions
4. **Codecov Signup**: https://about.codecov.io/sign-up/
5. **GitHub Secrets**: https://github.com/Cosimo77/pronostici-calcio-professional/settings/secrets/actions

---

## ✅ Checklist Configurazione

### Step 1: Repository Pubblico
- [ ] Settings → Danger Zone → Change visibility → Make public
- [ ] Conferma con nome repository

### Step 2: Branch Protection
- [ ] Settings → Branches → Add rule
- [ ] Pattern: `main`
- [ ] ✅ Require status checks
- [ ] ✅ Require branches up to date
- [ ] ✅ Do not allow bypassing
- [ ] ❌ Allow force pushes (DISATTIVATO)
- [ ] ❌ Allow deletions (DISATTIVATO)
- [ ] Click Create

### Step 3: Verifica Workflows
- [ ] Actions tab → Verifica 2 workflows running
- [ ] Attendi 3-5 min completamento
- [ ] Badge README verdi

### Step 4: Codecov (Opzionale)
- [ ] Signup su codecov.io
- [ ] Autorizza repository
- [ ] Copia CODECOV_TOKEN
- [ ] Aggiungi secret su GitHub
- [ ] Verifica coverage report

---

## 🎯 Configurazione Branch Protection

```yaml
Branch name pattern: main

✅ Require status checks to pass before merging
   ✅ Require branches to be up to date before merging
   Status checks (seleziona dopo primo run):
   - test / Run Tests
   - lint / Code Quality
   - security / Security Scan

✅ Do not allow bypassing the above settings

❌ Allow force pushes
❌ Allow deletions
```

---

## 🧪 Test Configurazione

Dopo setup, verifica:

```bash
# Crea feature branch
git checkout -b test/branch-protection
echo "test" >> README.md
git add README.md
git commit -m "test: verify branch protection"
git push origin test/branch-protection

# Su GitHub:
# 1. Crea Pull Request
# 2. Verifica CI checks running
# 3. Merge dovrebbe essere bloccato se checks falliscono
# 4. Merge abilitato solo se checks passano (green)
```

---

## 📊 Verifica Finale

Controlla che tutto funzioni:

1. **README Badge**: Tutti verdi
2. **Actions Tab**: Workflows completati
3. **Branch Protection**: Settings → Branches → vedi regola attiva
4. **Test Merge**: Crea PR, verifica blocco se test falliscono

---

## 🆘 Troubleshooting

**Status checks non visibili nella lista?**
- Attendi primo workflow run completo (~5 min)
- Refresh pagina branch protection
- Checks appaiono automaticamente dopo primo successo

**Codecov token non funziona?**
- Verifica secret name esatto: `CODECOV_TOKEN` (case-sensitive)
- Re-trigger workflow: Actions → Re-run all jobs

**Badge rossi su README?**
- Normale se workflows in esecuzione
- Diventano verdi dopo completamento (~5 min)
- Verifica logs: Actions → Click workflow → View logs

---

## ✨ Risultato Atteso

Dopo configurazione completa:

- ✅ Repository pubblico su GitHub
- ✅ Branch protection attivo
- ✅ CI/CD automatico su ogni push
- ✅ Merge bloccato se test falliscono
- ✅ Badge README tutti verdi
- ✅ Coverage tracking su Codecov
- ✅ Sistema rating **10.0/10** ⭐⭐⭐⭐⭐

Sistema production-grade enterprise-ready completo!
