#!/usr/bin/env python3
"""
🧹 PULIZIA FILE OBSOLETI - Sistema Pronostici
Script per rimuovere file non necessari e mantenere solo quelli essenziali
"""

import os
import glob
import shutil
from datetime import datetime

def print_header():
    print("🧹 PULIZIA FILE OBSOLETI")
    print("=" * 50)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()

def analyze_files():
    """Analizza e categorizza i file da rimuovere"""
    
    # File di test obsoleti (specifici per debug passati)
    test_files_obsoleti = [
        "test_atalanta_*.py",      # Test specifici Atalanta (risolti)
        "test_api_fix.py",         # Fix API (completato)
        "test_correzioni_mercati.py", # Correzioni mercati (completato)
        "test_debug_*.py",         # Debug specifici (non più necessari)
        "test_finale_*.py",        # Test finale (completato)
        "test_frontend_debug.py",  # Debug frontend (risolto)
        "test_forma_*.py",         # Test forma squadra (risolto)
        "test_goal_nogoal.py",     # Test specifico (completato)
        "test_grafici_debug.py",   # Debug grafici (risolto)
        "test_javascript.py",      # Test JS (risolto)
        "test_mercati_enhanced.py", # Test mercati vecchi (sostituito)
        "test_mercati_multipli.py", # Test mercati vecchi (sostituito)
        "test_mercati_quick.py",   # Test veloce (sostituito)
        "test_mercati_standalone.py", # Test standalone (sostituito)
        "test_mercati_veloce.py",  # Test veloce (sostituito)
        "test_pisa_final.py",      # Test specifico Pisa (risolto)
        "test_server_*.py",        # Test server (funzionante)
        "test_web_*.py",           # Test web (funzionante)
    ]
    
    # File HTML di test/debug
    html_files_obsoleti = [
        "test_*.html",             # Tutti i file HTML di test
        "index.html",              # HTML nella root (web/templates/index.html è quello vero)
    ]
    
    # File JSON di debug temporanei
    json_files_obsoleti = [
        "debug_mercati_ou.json",   # Debug mercati (temporaneo)
        "test_*.json",             # JSON di test
        "analisi_architettura.json", # Analisi architettura (completata)
    ]
    
    # File Python di demo/setup obsoleti
    demo_files_obsoleti = [
        "demo_*.py",               # File demo (sostituiti da sistema completo)
        "setup_sistema_completo.py", # Setup iniziale (completato)
        "launcher.py",             # Launcher vecchio (sostituito da aggiorna_*)
        "main.py",                 # Main vecchio (sostituito da web/app.py)
        "data_updater_auto.py",    # Updater vecchio (sostituito da automation_master)
        "allena_veloce.py",        # Allenamento vecchio (sostituito da allena_modelli_rapido)
    ]
    
    # File di validazione completati
    validazione_files_obsoleti = [
        "validatore_completo.py",  # Validazione completata
        "verifica_sistema.py",     # Verifica completata  
        "quick_check.py",          # Check veloce (sostituito da altri)
        "analizza_architettura.py", # Analisi completata
    ]
    
    return {
        "test_files": test_files_obsoleti,
        "html_files": html_files_obsoleti, 
        "json_files": json_files_obsoleti,
        "demo_files": demo_files_obsoleti,
        "validazione_files": validazione_files_obsoleti
    }

def get_files_to_remove(patterns):
    """Ottiene lista file che corrispondono ai pattern"""
    files_to_remove = []
    for pattern in patterns:
        matched_files = glob.glob(pattern)
        files_to_remove.extend(matched_files)
    return files_to_remove

def safe_remove_files(files_list, category_name):
    """Rimuove file in modo sicuro con conferma"""
    if not files_list:
        print(f"✅ {category_name}: Nessun file da rimuovere")
        return 0
    
    print(f"\n📂 {category_name}:")
    print("-" * 40)
    for file in files_list:
        print(f"  📄 {file}")
    
    if len(files_list) == 0:
        return 0
        
    confirm = input(f"\n❓ Rimuovere {len(files_list)} file di {category_name}? (y/N): ").lower().strip()
    
    if confirm == 'y':
        removed_count = 0
        for file in files_list:
            try:
                if os.path.isfile(file):
                    os.remove(file)
                    print(f"🗑️  Rimosso: {file}")
                    removed_count += 1
                elif os.path.isdir(file):
                    shutil.rmtree(file)
                    print(f"🗑️  Cartella rimossa: {file}")
                    removed_count += 1
            except Exception as e:
                print(f"⚠️  Errore rimozione {file}: {e}")
        
        print(f"✅ {category_name}: {removed_count} file rimossi")
        return removed_count
    else:
        print(f"⏭️  Saltato: {category_name}")
        return 0

def main():
    print_header()
    
    # Verifica directory corretta
    if not os.path.exists("web/app.py"):
        print("❌ Errore: Esegui dalla directory principale del progetto")
        return
    
    file_categories = analyze_files()
    
    total_removed = 0
    
    # Processa ogni categoria
    for category, patterns in file_categories.items():
        files_to_remove = get_files_to_remove(patterns)
        removed = safe_remove_files(files_to_remove, category.replace('_', ' ').title())
        total_removed += removed
    
    # Pulizia cache aggiuntiva
    print(f"\n🧹 PULIZIA CACHE AGGIUNTIVA:")
    print("-" * 40)
    
    cache_patterns = [
        "cache/*.log",
        "cache/*_debug.json", 
        "*.log",
        "__pycache__/*",
        ".DS_Store"
    ]
    
    cache_files = get_files_to_remove(cache_patterns)
    cache_removed = safe_remove_files(cache_files, "Cache e Log")
    total_removed += cache_removed
    
    # Riepilogo finale
    print(f"\n{'='*50}")
    print("📊 RIEPILOGO PULIZIA")
    print(f"{'='*50}")
    print(f"🗑️  File totali rimossi: {total_removed}")
    print(f"📁 Sistema pulito e ottimizzato!")
    print(f"💡 Spazio liberato e codice più pulito")
    
    if total_removed > 0:
        print(f"\n🎉 Pulizia completata con successo!")
    else:
        print(f"\n✨ Sistema già pulito!")

if __name__ == "__main__":
    main()