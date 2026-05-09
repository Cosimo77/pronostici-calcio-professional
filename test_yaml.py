#!/usr/bin/env python3
import yaml

try:
    with open(".github/workflows/weekly-retrain.yml") as f:
        yaml.safe_load(f)
    print("✅ YAML weekly-retrain.yml ORA VALIDO!")
except yaml.scanner.ScannerError as e:
    print(f"❌ Ancora errore YAML alla linea {e.problem_mark.line + 1}")
    print(f"Problema: {e.problem}")
except Exception as e:
    print(f"❌ Errore: {e}")
