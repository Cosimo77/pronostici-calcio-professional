#!/bin/bash
# Emergency fix: force Render to deploy correct dataset

echo "=== EMERGENCY FIX RENDER ==="
echo ""
echo "Dataset locale: CORRETTO (2663 partite, 2026-01-19)"
echo "Dataset GitHub: CORRETTO (2663 partite, commit aca0989)"  
echo "Dataset Render: CORROTTO (3243 partite)"
echo ""
echo "Questo significa che Render ha deployato un commit VECCHIO (925971e)"
echo "con dataset corrotto dal workflow auto-update del 24/01/2026"
echo ""
echo "SOLUZIONE:"
echo "1. Disattivare workflow (FATTO)"
echo "2. Push vuoto per triggerare re-deploy"
echo ""

# Crea commit vuoto per forzare deploy
git commit --allow-empty -m "FORCE DEPLOY: Fix Render con dataset corretto

Render sta usando commit 925971e (24 Gen) con 3243 partite corrotte.
Questo commit forza re-deploy con dataset corretto:
- 2663 partite reali
- Range: 2018-11-02 -> 2026-01-19
- Workflow auto-update DISABILITATO

Fix definitivo per issue dataset corrotto"

echo ""
echo "Commit creato. Faccio push..."
git push origin main

echo ""
echo "Push completato!"
echo ""
echo "Aspetta 5-7 minuti per il deploy Render, poi verifica:"
echo "./check_render_status.sh"
