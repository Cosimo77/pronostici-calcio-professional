#!/usr/bin/env python3
"""
PIANO PULIZIA WORKSPACE - Sistema Trading Professionale
Riorganizzazione file per struttura production-ready
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# === CONFIGURAZIONE PULIZIA ===

# File ESSENZIALI da tenere in root
KEEP_IN_ROOT = [
    # Entry point principale
    'run_professional_system.py',
    
    # Verifica sistema (creato oggi - utile)
    'verifica_sistema_completa.py',
    
    # Riaddestramento modelli (operativo)
    'riaddestra_modelli_rapido.py',
    
    # Script configurazione
    'setup_deploy.sh',
    'start.sh',
    'Procfile',
    'requirements.txt',
    'runtime.txt',
    'render.yaml',
    'app.json',
    'docker-compose.yml',
    'Dockerfile',
    'pyrightconfig.json',
    'config_security.py',
    'config_bankroll.json',
    'config.json',
    
    # File tracking operativi
    'tracking_giocate.csv',
]

# File da ARCHIVIARE (backups/archive/)
ARCHIVE = [
    # Backtest obsoleti (validazione FASE1/FASE2 già completata)
    'backtest_*.py',
    
    # Demo e validator vecchi
    'demo_*.py',
    'valida_*.py',
    
    # Script aggiornamento vecchi (automazione ora in background)
    'aggiornamento_dati_reali.py',
    
    # Script training vecchi
    'train_value_model.py',
    'allena_modelli_rapido.py',
    
    # Test vecchi (KEEP solo test_*.py creati oggi)
    'test_roi_calibrati.py',  # Obsoleto
]

# File da SPOSTARE in scripts/maintenance/
MOVE_TO_MAINTENANCE = [
    'aggiorna_risultati_auto.py',
    'aggiorna_tracking_fase2.py',
    'marca_giocate.py',
    'update_bet.py',
    'add_bet.py',
    'rigenera_backtest_professionale.py',
    'genera_tracking_fase2.py',
]

# File da SPOSTARE in scripts/analysis/
MOVE_TO_ANALYSIS = [
    'analizza_ev_roi.py',
    'analizza_opportunita_oggi.py',
    'analizza_quote_sweet.py',
    'analizza_tracking.py',
    'analizza_tracking_fase1.py',
    'mostra_opportunita_oggi.py',
    'mostra_partite.py',
    'check_partite_oggi.py',
    'check_roma.py',
    'calcola_exact_scores.py',
    'simula_risultati.py',
]

# File da SPOSTARE in scripts/monitoring/
MOVE_TO_MONITORING = [
    'dashboard_monitoring.py',
    'monitor_system.py',
]

# File da SPOSTARE in scripts/testing/
MOVE_TO_TESTING = [
    'test_server_api.py',
    'test_predizioni_endtoend.py',
    'test_automazione.sh',
    'check_github_actions.sh',
    'check_render_status.sh',
]

# Script shell da ORGANIZZARE
SHELL_SCRIPTS = [
    'aggiorna_risultati.sh',
    'apri_dashboard.sh',
    'emergency_fix_render.sh',
    'fix_sync.sh',
    'monitora_oggi.sh',
    'monitora_tracking.sh',
    'start_tracking_fase2.sh',
]

# File TEMPORANEI da ELIMINARE
DELETE_TEMP = [
    'betting_journal.py',  # Duplicato - funzionalità in diario web
    'fix_markdown_lint.py',  # Utility one-off
    '*_backup_*.csv',  # Backup CSV temporanei
    '*.pyc',
    '__pycache__',
]

def create_directory_structure():
    """Crea struttura directory organizzata"""
    dirs = [
        'backups/archive',
        'scripts/maintenance',
        'scripts/analysis',
        'scripts/monitoring',
        'scripts/testing',
        'scripts/shell',
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {dir_path}")

def archive_files(pattern_list):
    """Sposta file in archivio con timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d')
    archive_dir = f'backups/archive/{timestamp}'
    Path(archive_dir).mkdir(parents=True, exist_ok=True)
    
    count = 0
    for pattern in pattern_list:
        if '*' in pattern:
            import glob
            files = glob.glob(pattern)
        else:
            files = [pattern] if os.path.exists(pattern) else []
        
        for file in files:
            if os.path.exists(file):
                shutil.move(file, os.path.join(archive_dir, os.path.basename(file)))
                count += 1
                print(f"  📦 Archived: {file}")
    
    return count

def move_files(file_list, destination):
    """Sposta file in directory destinazione"""
    Path(destination).mkdir(parents=True, exist_ok=True)
    
    count = 0
    for file in file_list:
        if os.path.exists(file):
            dest_path = os.path.join(destination, os.path.basename(file))
            if os.path.exists(dest_path):
                print(f"  ⚠️  Skip duplicate: {file}")
            else:
                shutil.move(file, dest_path)
                count += 1
                print(f"  ➡️  Moved: {file} → {destination}")
    
    return count

def delete_temp_files():
    """Elimina file temporanei"""
    import glob
    count = 0
    
    for pattern in DELETE_TEMP:
        if '*' in pattern:
            files = glob.glob(pattern, recursive=True)
        else:
            files = [pattern] if os.path.exists(pattern) else []
        
        for file in files:
            if os.path.isfile(file):
                os.remove(file)
                count += 1
                print(f"  🗑️  Deleted: {file}")
            elif os.path.isdir(file):
                shutil.rmtree(file)
                count += 1
                print(f"  🗑️  Deleted dir: {file}")
    
    return count

def generate_summary():
    """Genera summary finale struttura"""
    print("\n" + "="*70)
    print("📊 STRUTTURA FINALE WORKSPACE")
    print("="*70)
    
    print("\n📁 ROOT (File essenziali):")
    root_py = [f for f in os.listdir('.') if f.endswith('.py')]
    print(f"  Python files: {len(root_py)}")
    for f in sorted(root_py)[:10]:
        print(f"    - {f}")
    if len(root_py) > 10:
        print(f"    ... e altri {len(root_py)-10}")
    
    print("\n📂 SCRIPTS/:")
    for subdir in ['maintenance', 'analysis', 'monitoring', 'testing', 'shell']:
        path = f'scripts/{subdir}'
        if os.path.exists(path):
            files = os.listdir(path)
            print(f"  {subdir}/: {len(files)} file")
    
    print("\n📦 BACKUPS/ARCHIVE/:")
    if os.path.exists('backups/archive'):
        archives = os.listdir('backups/archive')
        print(f"  {len(archives)} timestamp directories")
    
    print("\n✅ PULIZIA COMPLETATA")

def main():
    """Esegue pulizia workspace"""
    print("="*70)
    print("🧹 PULIZIA E RIORGANIZZAZIONE WORKSPACE")
    print("="*70)
    print()
    
    # Step 1: Crea struttura directory
    print("1️⃣ Creazione struttura directory...")
    create_directory_structure()
    print()
    
    # Step 2: Archivia file obsoleti
    print("2️⃣ Archiviazione file obsoleti...")
    archived = archive_files(ARCHIVE)
    print(f"  ✅ Archiviati: {archived} file\n")
    
    # Step 3: Organizza script maintenance
    print("3️⃣ Organizzazione script maintenance...")
    moved = move_files(MOVE_TO_MAINTENANCE, 'scripts/maintenance')
    print(f"  ✅ Spostati: {moved} file\n")
    
    # Step 4: Organizza script analysis
    print("4️⃣ Organizzazione script analysis...")
    moved = move_files(MOVE_TO_ANALYSIS, 'scripts/analysis')
    print(f"  ✅ Spostati: {moved} file\n")
    
    # Step 5: Organizza script monitoring
    print("5️⃣ Organizzazione script monitoring...")
    moved = move_files(MOVE_TO_MONITORING, 'scripts/monitoring')
    print(f"  ✅ Spostati: {moved} file\n")
    
    # Step 6: Organizza script testing
    print("6️⃣ Organizzazione script testing...")
    moved = move_files(MOVE_TO_TESTING, 'scripts/testing')
    print(f"  ✅ Spostati: {moved} file\n")
    
    # Step 7: Organizza shell scripts
    print("7️⃣ Organizzazione shell scripts...")
    moved = move_files(SHELL_SCRIPTS, 'scripts/shell')
    print(f"  ✅ Spostati: {moved} file\n")
    
    # Step 8: Elimina file temporanei
    print("8️⃣ Eliminazione file temporanei...")
    deleted = delete_temp_files()
    print(f"  ✅ Eliminati: {deleted} file/dir\n")
    
    # Step 9: Summary finale
    generate_summary()
    print()

if __name__ == '__main__':
    # Backup pre-pulizia
    print("⚠️  ATTENZIONE: Questa operazione riorganizzerà il workspace")
    print("📦 Un backup completo verrà creato in backups/archive/")
    print()
    
    response = input("Procedere con la pulizia? (yes/no): ")
    if response.lower() in ['yes', 'y', 'si', 's']:
        main()
    else:
        print("Pulizia annullata.")
