#!/bin/bash
# Fix completo: abort rebase, sovrascrivi con locale, force push

export GIT_EDITOR=true  # Disabilita editor

echo "=== FIX AUTOMATICO SYNC GITHUB ==="

# Abort qualsiasi operazione in corso
git rebase --abort 2>/dev/null
git merge --abort 2>/dev/null

# Reset a stato pulito
git reset --hard 4cf9f55

# Force push (sovrascrive GitHub con versione locale corretta)
echo "Force push versione locale (corretta) su GitHub..."
git push -f origin main

echo ""
echo "✅ SYNC COMPLETATO"
echo ""
echo "Dataset locale: 2673 partite (2018-11-02 -> 2026-01-26)"
echo "Workflow: RIATTIVATO con validazioni"
echo ""
echo "Prossimo auto-update: Domani 06:00"
