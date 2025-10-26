#!/usr/bin/env python3
"""
Web Interface per Sistema Pronostici Calcistici Serie A
Interfaccia web moderna e interattiva per predizioni calcistiche
"""

import sys
import os

# Aggiungi il percorso della directory principale al path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
scripts_dir = os.path.join(parent_dir, 'scripts')
sys.path.insert(0, parent_dir)
sys.path.insert(0, scripts_dir)

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
from datetime import datetime, timedelta
import threading
import time
import logging

# Import del sistema enhanced
try:
    from scripts.predittore_enhanced import PredittoreEnhanced
    ENHANCED_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Sistema enhanced non disponibile: {e}")
    ENHANCED_AVAILABLE = False

# Import del sistema mercati multipli
try:
    from scripts.mercati_multipli import MercatiMultipli
    MERCATI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Sistema mercati multipli non disponibile: {e}")
    MERCATI_AVAILABLE = False

# Classe demo sempre disponibile
class PronosticiCalculatorDemo:
    def __init__(self):
        self.squadre = ['Atalanta', 'Bologna', 'Cagliari', 'Como', 'Cremonese', 'Fiorentina',
                      'Genoa', 'Inter', 'Juventus', 'Lazio', 'Lecce', 'Milan', 'Napoli',
                      'Parma', 'Pisa', 'Roma', 'Sassuolo', 'Torino', 'Udinese', 'Verona']
        
    def predici_partita(self, casa, ospite):
        import random
        
        # Genera probabilità
        prob = {
            'H': random.uniform(0.2, 0.6),
            'D': random.uniform(0.1, 0.4),
            'A': random.uniform(0.2, 0.6)
        }
        # Normalizza probabilità
        total = sum(prob.values())
        prob = {k: v/total for k, v in prob.items()}
        
        # La predizione DEVE essere quella con probabilità più alta per coerenza
        pred = max(prob.keys(), key=lambda k: prob[k])
        confidence = prob[pred]  # La confidenza è la probabilità della predizione
        
        # Debug: mostra i valori generati
        print(f"🎲 Debug demo - Predizione: {pred}, Prob: {prob}, Conf: {confidence:.3f}")
        
        return pred, prob, confidence

# Import del sistema di pronostici
from typing import Optional, Type, Any, Dict, Union

PronosticiCalculatorML: Optional[Type[Any]] = None
FeatureEngineerClass: Optional[Type[Any]] = None  # Rinominato per evitare conflitti
MODULES_LOADED = False

try:
    # Prova import esplicito con path
    import sys
    import os
    scripts_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts')
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    
    # Import effettivi
    import modelli_predittivi
    import feature_engineering
    
    PronosticiCalculatorML = modelli_predittivi.PronosticiCalculator  # type: ignore
    FeatureEngineerClass = feature_engineering.FeatureEngineer  # type: ignore
    
    MODULES_LOADED = True
    print("✓ Moduli ML caricati correttamente")
    
except ImportError as e:
    print(f"⚠ Errore importazione moduli ML: {e}")
    print("Utilizzo modalità demo...")
    MODULES_LOADED = False
    PronosticiCalculatorML = None
    
    # Classe FeatureEngineer mock
    class FeatureEngineer:
        def __init__(self):
            pass

# Configurazione Flask con directory statiche corrette
app = Flask(__name__, 
           static_folder='static',
           static_url_path='/static',
           template_folder='templates')
app.config['SECRET_KEY'] = 'serie_a_predictions_2025'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

# Configurazione SocketIO ottimizzata per stabilità
socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   ping_timeout=60,
                   ping_interval=25,
                   logger=False,
                   engineio_logger=False,
                   async_mode='threading')

# Configurazione logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Variabili globali
calculator: Optional[Union[Any, PronosticiCalculatorDemo]] = None
df_features: Optional[pd.DataFrame] = None
squadre_disponibili: list[str] = []

# Inizializzazione automatica al caricamento del modulo
def _init_on_import():
    global squadre_disponibili
    try:
        import pandas as pd
        df = pd.read_csv(os.path.join(parent_dir, 'data/dataset_pulito.csv'))
        df['Date'] = pd.to_datetime(df['Date'])
        df_corrente = df[df['Date'] >= '2025-08-01']
        if len(df_corrente) > 0:
            squadre = set(df_corrente['HomeTeam'].unique()).union(set(df_corrente['AwayTeam'].unique()))
            squadre_disponibili = sorted(list(squadre))
            print(f"🚀 Inizializzazione rapida: {len(squadre_disponibili)} squadre Serie A 2025-26")
        else:
            squadre_disponibili = ['Atalanta', 'Bologna', 'Cagliari', 'Como', 'Cremonese', 'Fiorentina', 'Genoa', 'Inter', 'Juventus', 'Lazio', 'Lecce', 'Milan', 'Napoli', 'Parma', 'Pisa', 'Roma', 'Sassuolo', 'Torino', 'Udinese', 'Verona']
            print("⚠️ Fallback: squadre hardcoded")
    except Exception as e:
        print(f"⚠️ Errore init rapido: {e}")
        squadre_disponibili = ['Atalanta', 'Bologna', 'Cagliari', 'Como', 'Cremonese', 'Fiorentina', 'Genoa', 'Inter', 'Juventus', 'Lazio', 'Lecce', 'Milan', 'Napoli', 'Parma', 'Pisa', 'Roma', 'Sassuolo', 'Torino', 'Udinese', 'Verona']

_init_on_import()
cache_predizioni: Dict[str, Any] = {}  # Cache pulita per test
sistema_inizializzato = False
sistema_predizioni = None
enhanced_predittore = None
mercati_sistema = None  # Sistema mercati multipli

def inizializza_sistema():
    """Inizializza il sistema di predizioni"""
    global sistema_predizioni, enhanced_predittore, df_features, squadre_disponibili, sistema_inizializzato, calculator
    
    try:
        # Carica i dati CSV per le statistiche
        try:
            df_features = pd.read_csv(os.path.join(parent_dir, 'data/dataset_features.csv'))
            df_features['Date'] = pd.to_datetime(df_features['Date'])
            
            if len(df_features) > 0:
                # Usa squadre della stagione corrente 2025-26 dal dataset pulito
                try:
                    df_pulito = pd.read_csv(os.path.join(parent_dir, 'data/dataset_pulito.csv'))
                    df_pulito['Date'] = pd.to_datetime(df_pulito['Date'])
                    
                    # Filtra per stagione 2025-26 (da agosto 2025)
                    df_corrente = df_pulito[df_pulito['Date'] >= '2025-08-01']
                    
                    if len(df_corrente) > 0:
                        squadre_casa = set(df_corrente['HomeTeam'].unique())
                        squadre_trasferta = set(df_corrente['AwayTeam'].unique())
                        squadre_disponibili = sorted(list(squadre_casa.union(squadre_trasferta)))
                        print(f"✅ Squadre Serie A 2025-26: {len(squadre_disponibili)} squadre dalla stagione corrente")
                    else:
                        # Fallback: usa tutte le squadre features + Pisa
                        squadre_casa = set(df_features['HomeTeam'].unique())
                        squadre_trasferta = set(df_features['AwayTeam'].unique())
                        squadre_disponibili = sorted(list(squadre_casa.union(squadre_trasferta)))
                        if 'Pisa' not in squadre_disponibili:
                            squadre_disponibili.append('Pisa')
                            squadre_disponibili = sorted(squadre_disponibili)
                        print(f"⚠️ Fallback: {len(squadre_disponibili)} squadre (con Pisa aggiunto)")
                        
                except Exception as e:
                    print(f"⚠️ Errore caricamento squadre correnti: {e}")
                    # Fallback originale
                    squadre_casa = set(df_features['HomeTeam'].unique())
                    squadre_trasferta = set(df_features['AwayTeam'].unique())
                    squadre_disponibili = sorted(list(squadre_casa.union(squadre_trasferta)))
                    if 'Pisa' not in squadre_disponibili:
                        squadre_disponibili.append('Pisa')
                        squadre_disponibili = sorted(squadre_disponibili)
                    print(f"⚠️ Fallback errore: {len(squadre_disponibili)} squadre")
                
                print(f"✅ Dati caricati: {len(df_features)} partite, {len(squadre_disponibili)} squadre disponibili")
            
        except Exception as e:
            print(f"⚠️ Errore caricamento dati CSV: {e}")
            # Fallback con squadre predefinite
            squadre_disponibili = ['Juventus', 'Inter', 'AC Milan', 'Napoli', 'Roma', 'Lazio', 
                                 'Atalanta', 'Fiorentina', 'Bologna', 'Torino', 'Sassuolo', 
                                 'Udinese', 'Sampdoria', 'Genoa', 'Cagliari', 'Spezia', 
                                 'Venezia', 'Salernitana', 'Empoli', 'Verona']
            df_features = None
        
        # Prova a caricare il sistema principale
        try:
            from scripts.modelli_predittivi import PronosticiCalculator
            sistema_predizioni = PronosticiCalculator()
            calculator = sistema_predizioni  # Allinea le due variabili
            try:
                # Prova a caricare i modelli salvati
                sistema_predizioni.carica_modelli()
                print("✅ Modelli caricati con successo!")
            except:
                print("⚠️ Modelli non trovati, usando sistema demo")
                sistema_predizioni = PronosticiCalculatorDemo()
                calculator = sistema_predizioni
        except ImportError:
            print("⚠️ Moduli di predizione non trovati, usando sistema demo")
            sistema_predizioni = PronosticiCalculatorDemo()
            calculator = sistema_predizioni
        
        # Inizializza sistema enhanced se disponibile
        if ENHANCED_AVAILABLE:
            try:
                enhanced_predittore = PredittoreEnhanced()
                print("✅ Sistema Enhanced inizializzato!")
            except Exception as e:
                print(f"⚠️ Errore inizializzazione enhanced: {e}")
                enhanced_predittore = None
        else:
            enhanced_predittore = None
        
        # Inizializza sistema mercati multipli se disponibile
        global mercati_sistema
        if MERCATI_AVAILABLE:
            try:
                mercati_sistema = MercatiMultipli()
                print("✅ Sistema Mercati Multipli inizializzato!")
            except Exception as e:
                print(f"⚠️ Errore inizializzazione mercati: {e}")
                mercati_sistema = None
        else:
            mercati_sistema = None
        
        sistema_inizializzato = True
        return True
        
    except Exception as e:
        print(f"❌ Errore inizializzazione: {e}")
        return False

def crea_grafici_statistiche():
    """Crea grafici delle statistiche generali - Versione Robusta"""
    try:
        print("🔍 Debug: Inizio crea_grafici_statistiche")
        
        # Verifica prerequisiti
        if not sistema_inizializzato:
            print("❌ Debug: Sistema non inizializzato")
            return None, None, None
            
        if df_features is None:
            print("❌ Debug: df_features è None")
            return None, None, None
        
        print(f"✅ Debug: df_features disponibile con {len(df_features)} righe")
        
        # Crea copia sicura del DataFrame
        df_temp = df_features.copy()
        
        # Verifica colonne necessarie
        required_cols = ['FTR', 'Date', 'FTHG', 'FTAG', 'HomeTeam']
        missing_cols = [col for col in required_cols if col not in df_temp.columns]
        if missing_cols:
            print(f"❌ Debug: Colonne mancanti: {missing_cols}")
            return None, None, None
        
        print("✅ Debug: Tutte le colonne necessarie presenti")
        
        # Grafico 1: Distribuzione Risultati
        print("🔍 Debug: Creazione grafico risultati...")
        try:
            risultati = df_temp['FTR'].value_counts()
            risultati_labels = {'H': 'Vittoria Casa', 'A': 'Vittoria Trasferta', 'D': 'Pareggio'}
            
            fig_risultati = px.pie(
                values=risultati.values, 
                names=[risultati_labels.get(x, x) for x in risultati.index],
                title="Distribuzione Risultati Serie A",
                color_discrete_sequence=['#28a745', '#dc3545', '#ffc107']
            )
            fig_risultati.update_layout(
                font=dict(size=14),
                title_font_size=20,
                showlegend=True
            )
            
            grafico_risultati = json.dumps(fig_risultati, cls=PlotlyJSONEncoder)
            print("✅ Debug: Grafico risultati creato")
        except Exception as e:
            print(f"❌ Debug: Errore grafico risultati: {e}")
            grafico_risultati = None
        
        # Grafico 2: Gol per stagione
        print("🔍 Debug: Creazione grafico gol...")
        try:
            df_temp['Anno'] = df_temp['Date'].dt.year
            df_temp['GolTotali'] = df_temp['FTHG'] + df_temp['FTAG']
            gol_per_anno = df_temp.groupby('Anno')['GolTotali'].mean().round(2)
            
            if len(gol_per_anno) == 0:
                print("❌ Debug: Nessun dato gol disponibile")
                grafico_gol = None
            else:
                fig_gol = px.bar(
                    x=gol_per_anno.index,
                    y=gol_per_anno.values,
                    title="Media Gol per Partita per Stagione",
                    labels={'x': 'Anno', 'y': 'Media Gol'},
                    color=gol_per_anno.values,
                    color_continuous_scale='viridis'
                )
                fig_gol.update_layout(
                    font=dict(size=14),
                    title_font_size=20,
                    showlegend=False
                )
                
                grafico_gol = json.dumps(fig_gol, cls=PlotlyJSONEncoder)
                print("✅ Debug: Grafico gol creato")
        except Exception as e:
            print(f"❌ Debug: Errore grafico gol: {e}")
            grafico_gol = None
        
        # Grafico 3: Top squadre casa
        print("🔍 Debug: Creazione grafico squadre...")
        try:
            vittorie_casa = df_temp[df_temp['FTR'] == 'H']['HomeTeam'].value_counts().head(10)
            
            if len(vittorie_casa) == 0:
                print("❌ Debug: Nessuna vittoria casa trovata")
                grafico_squadre = None
            else:
                fig_squadre = px.bar(
                    x=vittorie_casa.values,
                    y=vittorie_casa.index,
                    orientation='h',
                    title="Top 10 Squadre - Vittorie in Casa",
                    labels={'x': 'Vittorie', 'y': 'Squadra'},
                    color=vittorie_casa.values,
                    color_continuous_scale='blues'
                )
                fig_squadre.update_layout(
                    font=dict(size=14),
                    title_font_size=20,
                    height=400
                )
                
                grafico_squadre = json.dumps(fig_squadre, cls=PlotlyJSONEncoder)
                print("✅ Debug: Grafico squadre creato")
        except Exception as e:
            print(f"❌ Debug: Errore grafico squadre: {e}")
            grafico_squadre = None
        
        print("✅ Debug: crea_grafici_statistiche completata")
        return grafico_risultati, grafico_gol, grafico_squadre
        
    except Exception as e:
        print(f"❌ Debug: Errore generale crea_grafici_statistiche: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

def crea_statistiche_semplici():
    """Crea statistiche con grafici CSS semplici e affidabili"""
    try:
        print("🔍 [STATS] Generazione statistiche semplici...")
        
        if df_features is None:
            print("❌ [STATS] df_features non disponibile")
            return {'risultati': None, 'gol': None, 'squadre': None, 'count': 0}
            
        df_temp = df_features.copy()
        results = {'risultati': None, 'gol': None, 'squadre': None, 'count': 0}
        
        # 1. Distribuzione Risultati (Grafico CSS a barre)
        try:
            risultati = df_temp['FTR'].value_counts()
            totale = risultati.sum()
            
            vittorie_casa = int(risultati.get('H', 0))
            vittorie_trasferta = int(risultati.get('A', 0)) 
            pareggi = int(risultati.get('D', 0))
            totale = int(totale)
            
            results['risultati'] = {
                'type': 'bar_chart',
                'title': 'Distribuzione Risultati Serie A',
                'data': [
                    {'label': 'Vittorie Casa', 'value': vittorie_casa, 'percentage': round(vittorie_casa/totale*100, 1), 'color': '#28a745'},
                    {'label': 'Vittorie Trasferta', 'value': vittorie_trasferta, 'percentage': round(vittorie_trasferta/totale*100, 1), 'color': '#dc3545'},
                    {'label': 'Pareggi', 'value': pareggi, 'percentage': round(pareggi/totale*100, 1), 'color': '#ffc107'}
                ]
            }
            results['count'] += 1
            print("✅ [STATS] Distribuzione risultati creata")
            
        except Exception as e:
            print(f"❌ [STATS] Errore distribuzione risultati: {e}")
            results['risultati'] = None
        
        # 2. Gol per stagione (Grafico CSS a linee)
        try:
            df_temp['Anno'] = df_temp['Date'].dt.year
            df_temp['GolTotali'] = df_temp['FTHG'] + df_temp['FTAG']
            gol_per_anno = df_temp.groupby('Anno')['GolTotali'].mean().round(2)
            
            if len(gol_per_anno) > 0:
                max_gol = gol_per_anno.max()
                
                results['gol'] = {
                    'type': 'line_chart',
                    'title': 'Media Gol per Partita per Stagione',
                    'data': [
                        {'label': str(int(anno)), 'value': float(media), 'percentage': round(float(media)/float(max_gol)*100, 1)}
                        for anno, media in gol_per_anno.items()
                        if isinstance(anno, (int, float)) and isinstance(media, (int, float))
                    ]
                }
                results['count'] += 1
                print("✅ [STATS] Gol per stagione creato")
            else:
                results['gol'] = None
                
        except Exception as e:
            print(f"❌ [STATS] Errore gol per stagione: {e}")
            results['gol'] = None
        
        # 3. Top squadre casa (Grafico CSS orizzontale)
        try:
            vittorie_casa = df_temp[df_temp['FTR'] == 'H']['HomeTeam'].value_counts().head(10)
            
            if len(vittorie_casa) > 0:
                max_vittorie = vittorie_casa.max()
                
                results['squadre'] = {
                    'type': 'horizontal_bar',
                    'title': 'Top 10 Squadre - Vittorie in Casa',
                    'data': [
                        {'label': str(squadra), 'value': int(vittorie), 'percentage': round(float(vittorie)/float(max_vittorie)*100, 1)}
                        for squadra, vittorie in vittorie_casa.items()
                    ]
                }
                results['count'] += 1
                print("✅ [STATS] Top squadre casa creato")
            else:
                results['squadre'] = None
                
        except Exception as e:
            print(f"❌ [STATS] Errore top squadre casa: {e}")
            results['squadre'] = None
        
        print(f"🎯 [STATS] Completato: {results['count']}/3 grafici CSS creati")
        return results
        
    except Exception as e:
        print(f"💥 [STATS] Errore generale: {e}")
        return {'risultati': None, 'gol': None, 'squadre': None, 'count': 0}

@app.route('/')
def index():
    """Pagina principale"""
    if not sistema_inizializzato:
        inizializza_sistema()
    
    return render_template('index.html', 
                         squadre=squadre_disponibili,
                         sistema_ready=sistema_inizializzato)

@app.route('/enhanced')
def enhanced():
    """Interfaccia Enhanced con scraper"""
    return render_template('enhanced.html')

@app.route('/test_finale.html')
def test_finale():
    """Pagina di test finale"""
    return send_from_directory('..', 'test_finale.html')

@app.route('/test_debug_raccomandazioni.html')
def test_debug_raccomandazioni():
    """Pagina di test debug raccomandazioni"""
    return send_from_directory('..', 'test_debug_raccomandazioni.html')

@app.route('/test_over_under')
def test_over_under():
    """Pagina di test per verificare la visualizzazione Over/Under"""
    return render_template('test_over_under.html')

@app.route('/debug_over_under')
def debug_over_under():
    """Pagina di debug per verificare cosa succede realmente con Over/Under"""
    return render_template('debug_over_under.html')

@app.route('/web/templates/<path:filename>')
def serve_templates(filename):
    """Serve i file template"""
    return send_from_directory('templates', filename)

@app.route('/web/static/<path:filename>')
def serve_static(filename):
    """Serve i file statici"""
    return send_from_directory('static', filename)

@app.route('/static/css/<filename>')
def serve_css(filename):
    """Serve i file CSS"""
    return send_from_directory('static/css', filename)

@app.route('/static/js/<filename>')
def serve_js(filename):
    """Serve i file JS"""
    return send_from_directory('static/js', filename)

@app.route('/css/<filename>')
def serve_css_alt(filename):
    """Serve i file CSS (path alternativo)"""
    return send_from_directory('static/css', filename)

@app.route('/js/<filename>')
def serve_js_alt(filename):
    """Serve i file JS (path alternativo)"""
    return send_from_directory('static/js', filename)

@app.route('/favicon.ico')
def favicon():
    """Gestisce il favicon per evitare errori 404"""
    try:
        return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    except:
        # Se il favicon non esiste, restituisce una risposta vuota invece di un errore
        from flask import Response
        return Response(status=204)

@app.route('/predict_enhanced', methods=['POST'])
def predict_enhanced():
    """Endpoint per predizioni enhanced"""
    try:
        data = request.get_json()
        home_team = data.get('home_team')
        away_team = data.get('away_team')
        
        if not home_team or not away_team:
            return jsonify({'error': 'Squadre mancanti'}), 400
        
        if home_team == away_team:
            return jsonify({'error': 'Le squadre devono essere diverse'}), 400
        
        if enhanced_predittore is None:
            return jsonify({'error': 'Sistema enhanced non disponibile'}), 503
        
        # Esegui predizione enhanced
        risultato = enhanced_predittore.predici_con_enhancement(home_team, away_team)
        
        return jsonify(risultato)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/squadre')
def api_squadre():
    """API per ottenere lista squadre"""
    return jsonify({'squadre': squadre_disponibili})

@app.route('/api/predici', methods=['POST'])
def api_predici():
    """API per predizioni"""
    global enhanced_predittore  # Dichiarazione global per poter modificare la variabile
    
    if not sistema_inizializzato:
        return jsonify({'error': 'Sistema non inizializzato'}), 500
    
    try:
        data = request.json
        print(f"🔍 Debug - Dati ricevuti: {data}")
        
        if not data:
            return jsonify({'error': 'Nessun dato ricevuto'}), 400
            
        squadra_casa = data.get('squadra_casa')
        squadra_ospite = data.get('squadra_ospite')  # Era squadra_trasferta
        
        print(f"🔍 Debug - Casa: {squadra_casa}, Ospite: {squadra_ospite}")
        
        if not squadra_casa or not squadra_ospite:
            return jsonify({'error': 'Squadre mancanti'}), 400
        
        if squadra_casa == squadra_ospite:
            return jsonify({'error': 'Le squadre devono essere diverse'}), 400
        
        # Cache key
        cache_key = f"{squadra_casa}_vs_{squadra_ospite}"
        
        if cache_key in cache_predizioni:
            print(f"📦 Predizione da cache: {cache_key}")
            return jsonify(cache_predizioni[cache_key])
        
        # Usa sistema enhanced se disponibile, altrimenti fallback su calculator standard
        enhanced_usato = False
        
        if enhanced_predittore is not None:
            print(f"🚀 Predizione enhanced con scraper: {squadra_casa} vs {squadra_ospite}")
            
            try:
                risultato_enhanced = enhanced_predittore.predici_con_enhancement(squadra_casa, squadra_ospite)
                
                # Estrai dati dal risultato enhanced
                pred_text = risultato_enhanced['predizione_enhanced']
                if 'Vittoria ' + squadra_casa in pred_text:
                    pred = 'H'
                elif 'Vittoria ' + squadra_ospite in pred_text:
                    pred = 'A'
                else:
                    pred = 'D'
                
                # Converte probabilità enhanced in formato compatibile
                prob_enhanced = risultato_enhanced['probabilita_enhanced']
                prob = {
                    'H': prob_enhanced['vittoria_casa'] / 100,
                    'A': prob_enhanced['vittoria_trasferta'] / 100, 
                    'D': prob_enhanced['pareggio'] / 100
                }
                confidenza = risultato_enhanced['confidenza_enhanced'] / 100
                enhanced_usato = True
                
                print(f"✅ Enhanced: pred={pred}, conf={confidenza:.3f}, con scraper integrati")
                
            except Exception as e:
                print(f"⚠️ Errore enhanced, fallback su calculator: {e}")
                enhanced_usato = False
        
        if not enhanced_usato:
            print(f"🔮 Predizione standard: {squadra_casa} vs {squadra_ospite}")
            
            # Usa il metodo appropriato per il tipo di calculator
            if calculator is None:
                print("❌ Calculator è None, provo a reinizializzare...")
                inizializza_sistema()
                if calculator is None:
                    return jsonify({'error': 'Calculator non disponibile'}), 500
                
            # Se è il calculator ML, passa df_features
            if hasattr(calculator, 'models') and df_features is not None:
                print("🔍 Usando calculator ML con df_features")
                pred, prob = calculator.predici_partita(squadra_casa, squadra_ospite, df_features)  # type: ignore
                confidenza = max(prob.values()) if isinstance(prob, dict) else 0.5
            else:
                # Calculator demo con 2 parametri
                print("🔍 Usando calculator demo")
                pred, prob, confidenza = calculator.predici_partita(squadra_casa, squadra_ospite)  # type: ignore
        
        print(f"🔍 Debug predizione - Pred: {pred}, Conf: {confidenza}, Prob: {prob}")
        print(f"🔍 Debug tipo prob: {type(prob)}, content: {prob}")
        
        if pred is None:
            return jsonify({'error': 'Dati insufficienti per la predizione'}), 400
        
        # Mappa risultati
        risultato_map = {
            'H': f'Vittoria {squadra_casa}',
            'A': f'Vittoria {squadra_ospite}',
            'D': 'Pareggio'
        }
        
        # La confidenza è già corretta dalla classe demo
        # Non serve ricalcolarla, è già quella della predizione
        if confidenza >= 0.6:
            livello_confidenza = 'alta'
            colore_confidenza = 'success'
            consiglio = 'Consigliato scommettere'
        elif confidenza >= 0.45:
            livello_confidenza = 'media'
            colore_confidenza = 'warning'
            consiglio = 'Scommessa con cautela'
        else:
            livello_confidenza = 'bassa'
            colore_confidenza = 'danger'
            consiglio = 'Sconsigliato scommettere'
        
        # Aggiungi info se enhanced è stato usato
        modalita = 'enhanced' if enhanced_usato else 'standard'
        
        risultato = {
            'predizione': pred,
            'squadra_casa': squadra_casa,
            'squadra_ospite': squadra_ospite,
            'confidenza': float(confidenza),
            'modalita': modalita,
            'scraper_integrati': enhanced_usato,
            'probabilita': {
                'H': float(prob.get('H', 0.33)) if isinstance(prob, dict) else 0.33,  # Casa
                'A': float(prob.get('A', 0.33)) if isinstance(prob, dict) else 0.33,  # Trasferta
                'D': float(prob.get('D', 0.33)) if isinstance(prob, dict) else 0.33   # Pareggio
            }
        }
        
        # Salva in cache
        cache_predizioni[cache_key] = risultato
        
        return jsonify(risultato)
        
    except Exception as e:
        print(f"❌ Errore predizione: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/forma/<squadra>')
def api_forma_squadra(squadra):
    """API per forma recente squadra - Versione semplificata e robusta"""
    if not sistema_inizializzato:
        return jsonify({'error': 'Sistema non inizializzato'}), 500
    
    try:
        print(f"🔍 Richiesta forma per squadra: {squadra}")
        
        # Carica dataset direttamente - prova prima dataset_pulito che è più completo
        try:
            df_work = pd.read_csv(os.path.join(parent_dir, 'data/dataset_pulito.csv'))
            print(f"📊 Dataset pulito caricato con {len(df_work)} righe")
        except Exception as e:
            print(f"⚠️ Errore caricamento dataset_pulito: {e}")
            try:
                df_work = pd.read_csv(os.path.join(parent_dir, 'data/dataset_features.csv'))
                print(f"📊 Fallback su dataset_features con {len(df_work)} righe")
            except Exception as e2:
                print(f"❌ Errore caricamento entrambi i dataset: {e2}")
                return jsonify({'error': 'Impossibile caricare i dati'}), 500
        
        # Converti Date in datetime
        df_work['Date'] = pd.to_datetime(df_work['Date'], errors='coerce')
        
        # Filtra partite della squadra
        partite_squadra = df_work[
            (df_work['HomeTeam'] == squadra) | 
            (df_work['AwayTeam'] == squadra)
        ].copy()
        
        # Prima prova con stagione corrente 2025-26 (da agosto 2025 in poi)
        stagione_corrente = partite_squadra[
            partite_squadra['Date'] >= '2025-08-01'
        ].sort_values('Date').copy()
        
        # NUOVA STRATEGIA: Mostra SOLO le partite della stagione corrente
        # Non usare fallback a stagioni precedenti
        partite_recenti = stagione_corrente.copy()
        
        if len(partite_recenti) > 0:
            print(f"🏟️ Usando {len(partite_recenti)} partite stagione corrente 2025-26 per {squadra}")
        else:
            print(f"⚠️ Nessuna partita trovata per {squadra} nella stagione corrente 2025-26")
        
        if len(partite_recenti) == 0:
            print(f"❌ Nessuna partita trovata per {squadra}")
            return jsonify({
                'squadra': squadra,
                'partite': [],
                'partite_analizzate': 0,
                'vittorie': 0,
                'pareggi': 0,
                'sconfitte': 0,
                'gol_fatti': 0,
                'gol_subiti': 0,
                'media_gol_fatti': 0.0,
                'media_gol_subiti': 0.0,
                'forma': 'N/A',
                'statistiche': {
                    'vittorie': 0,
                    'pareggi': 0,
                    'sconfitte': 0,
                    'gol_fatti': 0,
                    'gol_subiti': 0,
                    'punti': 0,
                    'forma': 'N/A'
                }
            })
        
        # Elabora le partite
        vittorie = pareggi = sconfitte = 0
        gol_fatti = gol_subiti = 0
        partite = []
        
        for _, row in partite_recenti.iterrows():
            try:
                is_home = row['HomeTeam'] == squadra
                
                if is_home:
                    gol_squadra = int(row['FTHG'])
                    gol_avversario = int(row['FTAG'])
                    avversario = row['AwayTeam']
                else:
                    gol_squadra = int(row['FTAG'])
                    gol_avversario = int(row['FTHG'])
                    avversario = row['HomeTeam']
                
                gol_fatti += gol_squadra
                gol_subiti += gol_avversario
                
                if gol_squadra > gol_avversario:
                    vittorie += 1
                    risultato = 'V'
                elif gol_squadra == gol_avversario:
                    pareggi += 1
                    risultato = 'P'
                else:
                    sconfitte += 1
                    risultato = 'S'
                
                partite.append({
                    'data': row['Date'].strftime('%d/%m/%Y') if pd.notna(row['Date']) else 'N/A',
                    'avversario': str(avversario),
                    'casa': is_home,
                    'risultato': f"{gol_squadra}-{gol_avversario}",
                    'esito': risultato
                })
                
            except Exception as e:
                print(f"⚠️ Errore elaborazione partita: {e}")
                continue
        
        punti = vittorie * 3 + pareggi
        forma = ''.join([p['esito'] for p in partite[-5:]])  # Ultimi 5 risultati
        
        print(f"✅ Statistiche per {squadra}: {vittorie}V {pareggi}P {sconfitte}S - {punti} punti")
        
        # Calcola medie
        num_partite = len(partite)
        media_gol_fatti = round(gol_fatti / num_partite, 2) if num_partite > 0 else 0
        media_gol_subiti = round(gol_subiti / num_partite, 2) if num_partite > 0 else 0
        
        return jsonify({
            'squadra': squadra,
            'partite': partite,  # Tutte le partite ordinate cronologicamente
            'partite_analizzate': num_partite,  # Campo necessario per il frontend
            'vittorie': vittorie,  # Anche a livello principale per compatibilità
            'pareggi': pareggi,
            'sconfitte': sconfitte,
            'gol_fatti': gol_fatti,
            'gol_subiti': gol_subiti,
            'media_gol_fatti': media_gol_fatti,  # Campo necessario per il frontend
            'media_gol_subiti': media_gol_subiti,
            'forma': forma,  # Anche a livello principale per compatibilità
            'statistiche': {
                'vittorie': vittorie,
                'pareggi': pareggi,
                'sconfitte': sconfitte,
                'gol_fatti': gol_fatti,
                'gol_subiti': gol_subiti,
                'punti': punti,
                'forma': forma
            }
        })
        
    except Exception as e:
        print(f"❌ Errore endpoint forma squadra: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Errore interno: {str(e)}'}), 500

@app.route('/api/statistiche')
def api_statistiche():
    """API per statistiche generali"""
    try:
        print("🔍 [STATS] Richiesta statistiche ricevuta")
        
        if df_features is None:
            print("⚠️ [STATS] df_features è None, modalità demo")
            return jsonify({
                'successo': True,
                'demo_mode': True,
                'stats_generali': {
                    'totale_partite': 380,
                    'squadre_totali': len(squadre_disponibili),
                    'periodo': "2021-2025 (Demo)",
                    'media_gol_partita': 2.8
                },
                'grafico_risultati': None,
                'grafico_gol': None,
                'grafico_squadre': None
            })
        
        print("✅ [STATS] df_features disponibile, creando stats...")
        
        # Genera statistiche semplici e affidabili
        print("🔍 [STATS] Generando statistiche CSS semplici...")
        grafici_results = crea_statistiche_semplici()
        print(f"✅ [STATS] Statistiche processate: {grafici_results.get('count', 0)}/3")
        
        # Calcola statistiche di base
        df_temp = df_features.copy()
        df_temp['GolTotali'] = df_temp['FTHG'] + df_temp['FTAG']
        
        response_data = {
            'successo': True,
            'demo_mode': False,
            'grafico_risultati': grafici_results.get('risultati'),
            'grafico_gol': grafici_results.get('gol'),
            'grafico_squadre': grafici_results.get('squadre'),
            'grafici_creati': grafici_results.get('count', 0),
            'stats_generali': {
                'totale_partite': int(len(df_features)),
                'squadre_totali': int(len(squadre_disponibili)),
                'periodo': f"{df_features['Date'].min().strftime('%d/%m/%Y')} - {df_features['Date'].max().strftime('%d/%m/%Y')}",
                'media_gol_partita': float(round(df_temp['GolTotali'].mean(), 2))
            }
        }
        
        print(f"✅ [STATS] Response preparata - {grafici_results.get('count', 0)}/3 grafici")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ [STATS] Errore statistiche: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'successo': False, 
            'error': str(e), 
            'demo_mode': True
        }), 500

@app.route('/api/mercati', methods=['POST'])
def api_mercati_multipli():
    """API per predizione mercati multipli"""
    global mercati_sistema
    
    if not sistema_inizializzato:
        return jsonify({'error': 'Sistema non inizializzato'}), 500
    
    if not MERCATI_AVAILABLE or mercati_sistema is None:
        return jsonify({'error': 'Sistema mercati multipli non disponibile'}), 503
    
    try:
        data = request.json
        print(f"🎲 Debug - Richiesta mercati: {data}")
        
        if not data:
            return jsonify({'error': 'Nessun dato ricevuto'}), 400
            
        squadra_casa = data.get('squadra_casa')
        squadra_ospite = data.get('squadra_ospite', data.get('squadra_trasferta'))  # Supporta entrambi
        
        print(f"🎲 Debug - Mercati Casa: {squadra_casa}, Ospite: {squadra_ospite}")
        
        if not squadra_casa or not squadra_ospite:
            return jsonify({'error': 'Squadre mancanti'}), 400
        
        if squadra_casa == squadra_ospite:
            return jsonify({'error': 'Le squadre devono essere diverse'}), 400
        
        # Cache key per mercati
        cache_key = f"mercati_{squadra_casa}_vs_{squadra_ospite}"
        
        # Controllo cache per mercati - SEMPRE RIGENERA PER TESTARE CORREZIONI
        if cache_key in cache_predizioni:
            print(f"🧹 Rimuovo cache vecchia: {cache_key}")
            del cache_predizioni[cache_key]
        
        print(f"🔮 Predizione mercati multipli: {squadra_casa} vs {squadra_ospite}")
        
        # Chiamata al sistema mercati multipli
        risultati_mercati = mercati_sistema.predici_tutti_mercati(squadra_casa, squadra_ospite)
        
        if 'errore' in risultati_mercati:
            return jsonify({'error': risultati_mercati['errore']}), 400
        
        # Conta i mercati (escludi metadata)
        mercati_count = len([k for k in risultati_mercati.keys() if k != 'metadata'])
        print(f"✅ Mercati completati: {mercati_count} mercati analizzati")
        
        # Prepara la risposta nel formato atteso dal frontend
        response_data = {
            'partita': f"{squadra_casa} vs {squadra_ospite}",
            'timestamp': datetime.now().isoformat(),
            'mercati': risultati_mercati,
            'confidence_generale': 0.75,  # Calcolo medio delle confidenze
            'raccomandazioni': risultati_mercati.get('raccomandazioni', [])
        }
        
        # Salva in cache
        cache_predizioni[cache_key] = response_data
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Errore mercati multipli: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/aggiorna-sistema', methods=['POST'])
def api_aggiorna_sistema():
    """API per aggiornare il sistema dal web"""
    try:
        print("🚀 Richiesta aggiornamento sistema dal web")
        
        # Verifica che non ci sia già un aggiornamento in corso
        status_file = 'cache/aggiornamento_in_corso.json'
        if os.path.exists(status_file):
            return jsonify({
                'error': 'Aggiornamento già in corso',
                'status': 'busy'
            }), 409
        
        # Crea file di stato
        with open(status_file, 'w') as f:
            json.dump({
                'started_at': datetime.now().isoformat(),
                'status': 'running'
            }, f)
        
        try:
            # Esegui aggiornamento rapido in background
            import threading
            
            def run_update():
                try:
                    import subprocess
                    result = subprocess.run([
                        sys.executable, 'aggiorna_rapido.py'
                    ], capture_output=True, text=True, timeout=600)  # 10 minuti timeout
                    
                    # Aggiorna file di stato
                    with open(status_file, 'w') as f:
                        json.dump({
                            'completed_at': datetime.now().isoformat(),
                            'status': 'completed' if result.returncode == 0 else 'error',
                            'output': result.stdout,
                            'error': result.stderr if result.returncode != 0 else None
                        }, f)
                        
                except Exception as e:
                    with open(status_file, 'w') as f:
                        json.dump({
                            'completed_at': datetime.now().isoformat(),
                            'status': 'error',
                            'error': str(e)
                        }, f)
            
            # Avvia aggiornamento in thread separato
            thread = threading.Thread(target=run_update)
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'message': 'Aggiornamento avviato',
                'status': 'started',
                'estimated_time': '3-5 minuti'
            })
            
        except Exception as e:
            # Rimuovi file di stato in caso di errore
            if os.path.exists(status_file):
                os.remove(status_file)
            raise e
            
    except Exception as e:
        print(f"❌ Errore avvio aggiornamento: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status-aggiornamento')
def api_status_aggiornamento():
    """API per controllare lo stato dell'aggiornamento"""
    try:
        status_file = 'cache/aggiornamento_in_corso.json'
        
        if not os.path.exists(status_file):
            return jsonify({
                'status': 'idle',
                'message': 'Nessun aggiornamento in corso'
            })
        
        with open(status_file, 'r') as f:
            status_data = json.load(f)
        
        # Se completato, rimuovi il file di stato
        if status_data.get('status') in ['completed', 'error']:
            try:
                os.remove(status_file)
            except:
                pass
        
        return jsonify(status_data)
        
    except Exception as e:
        print(f"❌ Errore controllo status: {e}")
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    try:
        print('👤 Client connesso')
        emit('status', {'message': 'Connesso al server', 'sistema_ready': sistema_inizializzato})
    except Exception as e:
        logger.error(f'Errore connessione SocketIO: {e}')

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    try:
        print('👤 Client disconnesso')
    except Exception as e:
        logger.error(f'Errore disconnessione SocketIO: {e}')

@socketio.on('predizione_request')
def handle_predizione_socket(data):
    """Handle predizione via WebSocket per real-time updates"""
    try:
        if not data:
            emit('predizione_error', {'error': 'Dati non validi'})
            return
            
        squadra_casa = data.get('squadra_casa')
        squadra_ospite = data.get('squadra_ospite', data.get('squadra_trasferta'))  # Supporta entrambi i nomi
        
        if not squadra_casa or not squadra_ospite:
            emit('predizione_error', {'error': 'Squadre non specificate'})
            return
            
        emit('predizione_progress', {'step': 'Inizializzazione...', 'progress': 10})
        
        # Simula progresso
        steps = [
            ('Caricamento dati...', 25),
            ('Calcolo features...', 50),
            ('Applicazione modelli...', 75),
            ('Ensemble predizione...', 90),
            ('Completato!', 100)
        ]
        
        for step, progress in steps:
            emit('predizione_progress', {'step': step, 'progress': progress})
            time.sleep(0.3)  # Simula processing time
        
        # Effettua predizione reale
        if calculator is None:
            emit('predizione_error', {'error': 'Calculator non inizializzato'})
            return
        
        # Gestisci diversi tipi di calculator
        if hasattr(calculator, 'models') and df_features is not None:
            result = calculator.predici_partita(squadra_casa, squadra_ospite, df_features)  # type: ignore
            if len(result) == 2:
                pred, prob = result
                confidenza = max(prob.values()) if isinstance(prob, dict) else 0.5
            else:
                pred, prob, confidenza = result
        else:
            pred, prob, confidenza = calculator.predici_partita(squadra_casa, squadra_ospite)  # type: ignore
        
        if pred:
            risultato_map = {
                'H': f'Vittoria {squadra_casa}',
                'A': f'Vittoria {squadra_ospite}',
                'D': 'Pareggio'
            }
            
            # Gestisci output diversi per tipi di probabilità
            if isinstance(prob, dict):
                prob_casa = prob.get('H', 0.33)
                prob_trasferta = prob.get('A', 0.33)
                prob_pareggio = prob.get('D', 0.33)
                max_prob = max(prob.values())
            else:
                # Assumiamo sia una lista o array numpy
                prob_casa = float(prob[0]) if len(prob) > 0 else 0.33
                prob_trasferta = float(prob[1]) if len(prob) > 1 else 0.33
                prob_pareggio = float(prob[2]) if len(prob) > 2 else 0.33
                max_prob = float(confidenza)
                
            emit('predizione_result', {
                'predizione': risultato_map[pred],
                'confidenza': float(max_prob),
                'probabilita': {
                    'casa': prob_casa,
                    'trasferta': prob_trasferta,
                    'pareggio': prob_pareggio
                }
            })
        else:
            emit('predizione_error', {'error': 'Impossibile effettuare la predizione'})
            
    except Exception as e:
        emit('predizione_error', {'error': str(e)})

# Error handler per SocketIO
@socketio.on_error()
def error_handler(e):
    """Gestisce errori SocketIO per prevenire runtime errors"""
    logger.error(f'Errore SocketIO: {e}')

@socketio.on_error_default
def default_error_handler(e):
    """Error handler di default per SocketIO"""
    logger.error(f'Errore SocketIO non gestito: {e}')

# Error handlers globali per migliorare la stabilità
@app.errorhandler(404)
def not_found_error(error):
    """Gestisce errori 404"""
    return jsonify({'error': 'Risorsa non trovata'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Gestisce errori interni del server"""
    return jsonify({'error': 'Errore interno del server'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Gestisce tutte le eccezioni non catturate"""
    logger.error(f"Eccezione non gestita: {str(e)}")
    return jsonify({'error': 'Si è verificato un errore imprevisto'}), 500

if __name__ == '__main__':
    import os
    print("🌐 Avvio server web Sistema Pronostici Serie A...")
    
    # Inizializza sistema
    if inizializza_sistema():
        port = int(os.environ.get('PORT', 5001))
        print("🚀 Sistema inizializzato con successo!")
        print(f"🌐 Server disponibile su: http://localhost:{port}")
        socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
    else:
        print("❌ Impossibile inizializzare il sistema")
        print("Assicurati di aver eseguito prima il training dei modelli")