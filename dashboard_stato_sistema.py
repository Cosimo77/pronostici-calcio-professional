#!/usr/bin/env python3
"""
🌐 DASHBOARD STATO SISTEMA
Dashboard web per monitoraggio in tempo reale
"""

from flask import Flask, render_template_string, jsonify
import os
import json
import joblib
import pandas as pd
from datetime import datetime
from pathlib import Path
import threading
import time

app = Flask(__name__)

class SystemMonitor:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.last_check = None
        self.status_data = {}
        
    def get_system_status(self):
        """Ottieni stato completo del sistema"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'dataset': self._check_dataset(),
            'models': self._check_models(),
            'automation': self._check_automation(),
            'overall': 'ok'
        }
        
        # Determina stato generale
        if not all([status['dataset']['ok'], status['models']['ok'], status['automation']['ok']]):
            status['overall'] = 'warning'
        
        self.status_data = status
        self.last_check = datetime.now()
        return status
    
    def _check_dataset(self):
        """Verifica stato dataset"""
        dataset_path = self.base_path / "data" / "dataset_features.csv"
        
        if not dataset_path.exists():
            return {'ok': False, 'message': 'Dataset mancante', 'details': {}}
        
        try:
            dataset_mtime = os.path.getmtime(dataset_path)
            dataset_date = datetime.fromtimestamp(dataset_mtime)
            hours_old = (datetime.now() - dataset_date).total_seconds() / 3600
            
            df = pd.read_csv(dataset_path)
            
            ok = hours_old < 72  # Accettabile se < 72h
            
            return {
                'ok': ok,
                'message': f'{"Fresco" if hours_old < 24 else "Accettabile" if ok else "Obsoleto"}',
                'details': {
                    'last_update': dataset_date.strftime('%d/%m/%Y %H:%M'),
                    'hours_old': round(hours_old, 1),
                    'total_matches': len(df),
                    'latest_match': df['Date'].max() if 'Date' in df.columns else 'N/A'
                }
            }
        except Exception as e:
            return {'ok': False, 'message': f'Errore: {str(e)}', 'details': {}}
    
    def _check_models(self):
        """Verifica stato modelli"""
        models_dir = self.base_path / "models"
        dataset_path = self.base_path / "data" / "dataset_features.csv"
        
        if not dataset_path.exists():
            return {'ok': False, 'message': 'Dataset mancante per verifica', 'details': {}}
        
        try:
            dataset_mtime = os.path.getmtime(dataset_path)
            main_models = ['randomforest_model.pkl', 'gradientboosting_model.pkl', 'logisticregression_model.pkl']
            
            models_status = {}
            synced_count = 0
            
            for model_file in main_models:
                model_path = models_dir / model_file
                if model_path.exists():
                    model_mtime = os.path.getmtime(model_path)
                    is_synced = model_mtime >= dataset_mtime
                    
                    models_status[model_file] = {
                        'synced': is_synced,
                        'last_update': datetime.fromtimestamp(model_mtime).strftime('%d/%m/%Y %H:%M')
                    }
                    
                    if is_synced:
                        synced_count += 1
                else:
                    models_status[model_file] = {'synced': False, 'last_update': 'Mancante'}
            
            # Verifica performance dai metadata
            performance = {}
            metadata_path = models_dir / "metadata.pkl"
            if metadata_path.exists():
                try:
                    metadata = joblib.load(metadata_path)
                    if 'model_performance' in metadata:
                        for model_name, perf in metadata['model_performance'].items():
                            if isinstance(perf, dict) and 'accuracy' in perf:
                                performance[model_name] = f"{perf['accuracy']:.1%}"
                except:
                    pass
            
            ok = synced_count == len(main_models)
            
            return {
                'ok': ok,
                'message': f'{synced_count}/{len(main_models)} sincronizzati',
                'details': {
                    'models': models_status,
                    'performance': performance
                }
            }
        except Exception as e:
            return {'ok': False, 'message': f'Errore: {str(e)}', 'details': {}}
    
    def _check_automation(self):
        """Verifica stato automazione"""
        config_path = self.base_path / "config" / "auto_update.json"
        
        if not config_path.exists():
            return {'ok': False, 'message': 'Configurazione mancante', 'details': {}}
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            has_schedule = 'schedule' in config
            has_sources = 'data_sources' in config
            
            active_sources = 0
            if has_sources:
                for source in config['data_sources'].values():
                    if isinstance(source, dict) and source.get('enabled', False):
                        active_sources += 1
            
            ok = has_schedule and has_sources and active_sources > 0
            
            details = {}
            if has_schedule:
                details['schedule'] = config['schedule']
            details['active_sources'] = active_sources
            
            return {
                'ok': ok,
                'message': f'{active_sources} sorgenti attive' if ok else 'Configurazione incompleta',
                'details': details
            }
        except Exception as e:
            return {'ok': False, 'message': f'Errore: {str(e)}', 'details': {}}

monitor = SystemMonitor()

# Template HTML per dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🎯 Sistema Professionale - Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.95);
            border-radius: 15px;
            padding: 30px;
            color: #333;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
        }
        .status-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .status-card { 
            background: white; 
            border-radius: 10px; 
            padding: 20px; 
            border-left: 5px solid #ddd;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .status-card:hover {
            transform: translateY(-5px);
        }
        .status-ok { border-left-color: #28a745; }
        .status-warning { border-left-color: #ffc107; }
        .status-error { border-left-color: #dc3545; }
        .status-icon { 
            font-size: 2em; 
            margin-bottom: 10px; 
        }
        .status-title { 
            font-size: 1.2em; 
            font-weight: bold; 
            margin-bottom: 10px; 
        }
        .status-message { 
            color: #666; 
            margin-bottom: 15px; 
        }
        .details { 
            font-size: 0.9em; 
            background: #f8f9fa; 
            padding: 10px; 
            border-radius: 5px; 
        }
        .refresh-btn { 
            background: #667eea; 
            color: white; 
            border: none; 
            padding: 12px 25px; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 1em;
            margin: 10px 5px;
            transition: background 0.3s ease;
        }
        .refresh-btn:hover { 
            background: #5a67d8; 
        }
        .timestamp { 
            text-align: center; 
            color: #666; 
            font-size: 0.9em; 
            margin-top: 20px; 
        }
        .overall-status {
            text-align: center;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
            font-size: 1.2em;
            font-weight: bold;
        }
        .overall-ok { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .overall-warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .auto-refresh {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 10px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="auto-refresh" id="autoRefresh">🔄 Auto-refresh: 30s</div>
    
    <div class="container">
        <div class="header">
            <h1>🎯 Sistema Professionale Pronostici</h1>
            <h2>Dashboard Stato in Tempo Reale</h2>
        </div>
        
        <div class="overall-status" id="overallStatus">
            ⏳ Caricamento stato sistema...
        </div>
        
        <div class="status-grid" id="statusGrid">
            <!-- Contenuto caricato via JavaScript -->
        </div>
        
        <div style="text-align: center;">
            <button class="refresh-btn" onclick="refreshStatus()">🔄 Aggiorna Ora</button>
            <button class="refresh-btn" onclick="toggleAutoRefresh()">⏸️ Auto-Refresh</button>
        </div>
        
        <div class="timestamp" id="timestamp"></div>
    </div>

    <script>
        let autoRefreshInterval;
        let autoRefreshEnabled = true;
        let countdown = 30;
        
        function refreshStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => updateDashboard(data))
                .catch(error => console.error('Errore:', error));
        }
        
        function updateDashboard(status) {
            // Stato generale
            const overallDiv = document.getElementById('overallStatus');
            if (status.overall === 'ok') {
                overallDiv.className = 'overall-status overall-ok';
                overallDiv.innerHTML = '🎉 SISTEMA COMPLETAMENTE OPERATIVO';
            } else {
                overallDiv.className = 'overall-status overall-warning';
                overallDiv.innerHTML = '⚠️ SISTEMA NECESSITA ATTENZIONE';
            }
            
            // Cards di stato
            const grid = document.getElementById('statusGrid');
            grid.innerHTML = `
                ${createStatusCard('📊', 'Dataset', status.dataset)}
                ${createStatusCard('🤖', 'Modelli ML', status.models)}
                ${createStatusCard('🔄', 'Automazione', status.automation)}
            `;
            
            // Timestamp
            document.getElementById('timestamp').innerHTML = 
                `Ultimo aggiornamento: ${new Date(status.timestamp).toLocaleString('it-IT')}`;
        }
        
        function createStatusCard(icon, title, statusData) {
            const statusClass = statusData.ok ? 'status-ok' : 'status-error';
            const statusIcon = statusData.ok ? '✅' : '❌';
            
            let detailsHtml = '';
            if (statusData.details && Object.keys(statusData.details).length > 0) {
                if (title === 'Dataset') {
                    detailsHtml = `
                        <div class="details">
                            <strong>Dettagli:</strong><br>
                            📅 Ultimo aggiornamento: ${statusData.details.last_update || 'N/A'}<br>
                            ⏰ Età: ${statusData.details.hours_old || 'N/A'} ore<br>
                            📊 Partite totali: ${statusData.details.total_matches || 'N/A'}<br>
                            🏆 Partita più recente: ${statusData.details.latest_match || 'N/A'}
                        </div>
                    `;
                } else if (title === 'Modelli ML') {
                    let modelsHtml = '';
                    if (statusData.details.models) {
                        for (const [model, info] of Object.entries(statusData.details.models)) {
                            const syncIcon = info.synced ? '✅' : '❌';
                            const modelName = model.replace('_model.pkl', '').replace('_', ' ');
                            modelsHtml += `${syncIcon} ${modelName}: ${info.last_update}<br>`;
                        }
                    }
                    
                    let perfHtml = '';
                    if (statusData.details.performance && Object.keys(statusData.details.performance).length > 0) {
                        perfHtml = '<br><strong>Performance:</strong><br>';
                        for (const [model, acc] of Object.entries(statusData.details.performance)) {
                            perfHtml += `🎯 ${model}: ${acc}<br>`;
                        }
                    }
                    
                    detailsHtml = `
                        <div class="details">
                            <strong>Stato modelli:</strong><br>
                            ${modelsHtml}
                            ${perfHtml}
                        </div>
                    `;
                } else if (title === 'Automazione') {
                    let scheduleHtml = '';
                    if (statusData.details.schedule) {
                        scheduleHtml = '<strong>Schedule:</strong><br>';
                        for (const [key, value] of Object.entries(statusData.details.schedule)) {
                            scheduleHtml += `⏰ ${key}: ${value}<br>`;
                        }
                    }
                    
                    detailsHtml = `
                        <div class="details">
                            📡 Sorgenti attive: ${statusData.details.active_sources || 0}<br>
                            ${scheduleHtml}
                        </div>
                    `;
                }
            }
            
            return `
                <div class="status-card ${statusClass}">
                    <div class="status-icon">${icon}</div>
                    <div class="status-title">${title} ${statusIcon}</div>
                    <div class="status-message">${statusData.message}</div>
                    ${detailsHtml}
                </div>
            `;
        }
        
        function toggleAutoRefresh() {
            autoRefreshEnabled = !autoRefreshEnabled;
            const btn = event.target;
            
            if (autoRefreshEnabled) {
                btn.innerHTML = '⏸️ Auto-Refresh';
                startAutoRefresh();
            } else {
                btn.innerHTML = '▶️ Auto-Refresh';
                clearInterval(autoRefreshInterval);
                document.getElementById('autoRefresh').innerHTML = '⏸️ Auto-refresh: PAUSED';
            }
        }
        
        function startAutoRefresh() {
            countdown = 30;
            autoRefreshInterval = setInterval(() => {
                if (autoRefreshEnabled) {
                    countdown--;
                    document.getElementById('autoRefresh').innerHTML = `🔄 Auto-refresh: ${countdown}s`;
                    
                    if (countdown <= 0) {
                        refreshStatus();
                        countdown = 30;
                    }
                }
            }, 1000);
        }
        
        // Avvio iniziale
        refreshStatus();
        startAutoRefresh();
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Pagina principale dashboard"""
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/api/status')
def api_status():
    """API endpoint per stato sistema"""
    return jsonify(monitor.get_system_status())

def run_dashboard(host='127.0.0.1', port=5001):
    """Avvia dashboard"""
    print(f"🌐 Dashboard disponibile su: http://{host}:{port}")
    print("📊 Monitoraggio in tempo reale del sistema professionale")
    app.run(host=host, port=port, debug=False)

if __name__ == "__main__":
    run_dashboard()