#!/usr/bin/env python3
"""Confronto stato locale vs Render"""

print("\n" + "="*70)
print("CONFRONTO LOCALE vs RENDER - 14 Gennaio 2026")
print("="*70 + "\n")

print("DATASET:")
print(f"  Locale:  2846 partite (ultima: 2026-01-08)")
print(f"  Render:  2815 partite")
print(f"  Delta:   +31 partite NON SINCRONIZZATE")

print("\nMODELLI:")
print(f"  Locale:  8 file .pkl (RandomForest, LightGBM, XGBoost)")
print(f"  Render:  0 caricati (usa ProfessionalCalculator)")
print(f"  Status:  NORMALE - sistema non richiede .pkl esterni")

print("\nAGGIORNAMENTI:")
print(f"  Ultimo update Render:   11/01/2026 17:27")
print(f"  Ultima partita locale:  08/01/2026")
print(f"  Giorni da update:       3 giorni")

print("\n" + "="*70)
print("AZIONE NECESSARIA")
print("="*70)

print("\nDataset locale ha 31 partite in piu di Render")
print("Push necessario per sincronizzare:\n")
print("  git status")
print("  git add data/dataset_pulito.csv")
print("  git commit -m 'Update dataset 8 gennaio 2026'")
print("  git push origin main")
print("\nRender ricarichera automaticamente dopo il push.\n")

print("="*70 + "\n")
