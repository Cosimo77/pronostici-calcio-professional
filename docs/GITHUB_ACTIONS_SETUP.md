# 🤖 Automazione GitHub Actions - Setup Completo

## Overview

Sistema di automazione **100% gratuito** su GitHub Actions per mantenere l'app sempre aggiornata senza intervento manuale.

---

## 🎯 Cosa Fa

### **1. Aggiornamento Giornaliero** (`daily-update.yml`)
**Schedule**: Ogni giorno alle 06:00 UTC (07:00 CET)

**Azioni**:
- ✅ Scarica nuove partite Serie A da football-data.co.uk
- ✅ Rigenera `dataset_pulito.csv` con tutte le stagioni
- ✅ Calcola features ML (`dataset_features.csv`)
- ✅ Backup database diario (se configurato)
- ✅ Commit automatico modifiche
- ✅ Push → Trigger auto-deploy Render

**Output**: Dataset sempre aggiornato, Render deploy automatico

---

### **2. Manutenzione Settimanale** (`weekly-maintenance.yml`)
**Schedule**: Ogni domenica alle 03:00 UTC

**Azioni**:
- 🗑️ Rimuove backup >30 giorni
- 🗜️ Comprimi log >7 giorni
- 🧪 Verifica integrità dataset (duplicati, date mancanti)
- 📊 Report statistiche repository

---

## ⚙️ Setup Iniziale

### **Step 1: Configurare Secrets GitHub**

1. Vai su **GitHub Repository** → `Settings` → `Secrets and variables` → `Actions`

2. Clicca **"New repository secret"**

3. Aggiungi questi secrets:

   **DATABASE_URL** (opzionale per backup):
   ```
   Name: DATABASE_URL
   Value: postgresql://pronostici_calcio_production_9s31_user:jpjqFKpFehy0Ue9Rdw4dfkkBUQ9g5hjx@dpg-d7vlqo50lvsc7380k250-a.frankfurt-postgres.render.com/pronostici_calcio_production_9s31
   ```

   ⚠️ **Nota**: DATABASE_URL è opzionale. Se non configurato, backup viene skippato (normale).

---

### **Step 2: Abilitare GitHub Actions**

1. Vai su **Repository** → `Settings` → `Actions` → `General`

2. Verifica che sia selezionato:
   - ✅ **"Allow all actions and reusable workflows"**

3. In **"Workflow permissions"**, seleziona:
   - ✅ **"Read and write permissions"**
   - ✅ **"Allow GitHub Actions to create and approve pull requests"**

4. Clicca **Save**

---

### **Step 3: Test Workflow Manualmente**

Prima di affidarti allo schedule automatico, testa:

1. Vai su **Repository** → `Actions` tab

2. Seleziona workflow **"🔄 Aggiornamento Automatico Giornaliero"**

3. Clicca **"Run workflow"** → `Run workflow` (branch main)

4. Aspetta 2-3 minuti e controlla risultato:
   - ✅ Verde = Success
   - ❌ Rosso = Errore (clicca per vedere log)

5. Verifica commit automatico su repository

6. Controlla Render dashboard: Deploy automatico dopo ~2 min

---

## 📊 Monitoring

### **Visualizza Esecuzioni**

- **Actions tab**: Tutte le esecuzioni passate/future
- **Badge status**: Aggiungi al README.md:
  ```markdown
  ![Daily Update](https://github.com/Cosimo77/pronostici-calcio-professional/actions/workflows/daily-update.yml/badge.svg)
  ```

### **Notifiche Email**

GitHub invia email automaticamente se workflow fallisce.

Configura in: `Settings` → `Notifications` → `Actions`

---

## 🚨 Troubleshooting

### ❌ "Error: Process completed with exit code 1"

**Causa**: Script Python fallito

**Fix**:
1. Clicca su run fallito → Espandi step rosso
2. Leggi errore Python
3. Fixa codice → Commit → Workflow riprova

---

### ⚠️ "Backup database fallito"

**Normale!** GitHub Actions non può accedere a Render PostgreSQL (firewall).

Backup funziona solo in locale o su Render stesso.

Il workflow continua comunque (`continue-on-error: true`).

---

### 🔴 "Nothing to commit"

**Normale!** Significa nessun dato nuovo disponibile.

Workflow termina senza commit (atteso).

---

### 📅 "Workflow non si esegue alle 06:00"

**Causa**: GitHub Actions schedule ha ritardi fino a 10-15 minuti (normale nei picchi).

**Non è un problema** per aggiornamento giornaliero.

---

## 🎛️ Configurazione Avanzata

### Cambia Orario Schedule

Modifica `.github/workflows/daily-update.yml`:

```yaml
schedule:
  - cron: '0 6 * * *'  # 06:00 UTC
  # Sintassi: minuto ora giorno mese giorno_settimana
  # Es: '30 8 * * *' = 08:30 UTC ogni giorno
```

**Tool utile**: https://crontab.guru

---

### Disabilita Workflow

Temporaneamente:
- `Actions` → Workflow → `...` → `Disable workflow`

Permanentemente:
- Cancella file `.github/workflows/daily-update.yml`

---

### Aggiungi Notifiche Slack/Discord

Aggiungi step finale:

```yaml
- name: 📢 Notifica Slack
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "⚠️ Workflow fallito: ${{ github.workflow }}"
      }
```

---

## 💰 Costi

**GitHub Actions Free Tier**:
- ✅ 2000 minuti/mese (privato) o illimitati (pubblico)
- ✅ Workflow dura ~2 minuti → 60 esecuzioni/mese = **120 minuti/mese**
- ✅ **Ampiamente dentro il free tier**

**Render**:
- ✅ Auto-deploy gratuito su Git push
- ✅ Nessun costo aggiuntivo

**Totale**: **€0/mese** ✅

---

## 📈 Quota Monitor

Controlla usage:
- `Settings` → `Billing and plans` → `Plans and usage`
- Sezione "Actions" mostra minuti usati

---

## ✅ Checklist Finale

Prima di andare in produzione:

- [ ] Secrets configurati su GitHub (DATABASE_URL opzionale)
- [ ] Workflow permissions "Read and write" abilitati
- [ ] Test manuale workflow eseguito con successo
- [ ] Verificato commit automatico su repository
- [ ] Verificato auto-deploy su Render dopo commit
- [ ] Email notifications configurate per failure

**Tutto OK?** → Sistema è **100% automatico e gratuito!** 🎉

---

## 🆘 Supporto

**Problemi?**
1. Check Actions tab per log dettagliati
2. Verifica secrets configurati correttamente
3. Test workflow manualmente prima di affidarti allo schedule
4. GitHub Actions docs: https://docs.github.com/en/actions

**Sistema funziona?** Non servono più modifiche! Tutto automatico. 🚀
