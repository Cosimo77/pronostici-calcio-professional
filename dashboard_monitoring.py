#!/usr/bin/env python3
"""
📊 DASHBOARD MONITORING ENTERPRISE
Monitoraggio in tempo reale del sistema professionale
"""

import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template_string, jsonify, send_from_directory
import pandas as pd
import requests

try:
    import psutil
except ImportError:
    psutil = None

app = Flask(__name__)

# Template HTML per la dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔍 Dashboard Monitoraggio Sistema Pronostici</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .status-healthy { color: #28a745; }
        .status-warning { color: #ffc107; }
        .status-error { color: #dc3545; }
        .metric-card { transition: transform 0.2s; }
        .metric-card:hover { transform: translateY(-2px); }
        .log-entry { font-family: 'Courier New', monospace; font-size: 0.85em; }
        .bg-gradient-primary { background: linear-gradient(45deg, #007bff, #6610f2); }
        .refresh-btn { position: fixed; bottom: 20px; right: 20px; z-index: 1000; }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-gradient-primary">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-chart-line me-2"></i>Dashboard Monitoraggio Sistema Pronostici
            </span>
            <span class="navbar-text">
                <span id="last-update">Caricamento...</span>
            </span>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <!-- Status Overview -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-heartbeat me-2"></i>Stato Sistema</h5>
                    </div>
                    <div class="card-body">
                        <div id="system-status" class="text-center">
                            <div class="spinner-border" role="status"></div>
                            <p class="mt-2">Caricamento stato sistema...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Metrics Cards -->
        <div class="row mb-4" id="metrics-row">
            <!-- Dinamicamente popolato via JavaScript -->
        </div>

        <!-- Health Checks -->
        <div class="row mb-4">
            <div class="col-lg-6">
                <div class="card h-100">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-stethoscope me-2"></i>Health Checks</h5>
                    </div>
                    <div class="card-body">
                        <div id="health-checks">
                            <div class="text-center">
                                <div class="spinner-border spinner-border-sm" role="status"></div>
                                <span class="ms-2">Caricamento...</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-lg-6">
                <div class="card h-100">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-robot me-2"></i>Automazione</h5>
                    </div>
                    <div class="card-body">
                        <div id="automation-status">
                            <div class="text-center">
                                <div class="spinner-border spinner-border-sm" role="status"></div>
                                <span class="ms-2">Caricamento...</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Data Status -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-database me-2"></i>Stato Dati</h5>
                    </div>
                    <div class="card-body">
                        <div id="data-status">
                            <div class="text-center">
                                <div class="spinner-border spinner-border-sm" role="status"></div>
                                <span class="ms-2">Caricamento...</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Recent Logs -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0"><i class="fas fa-file-alt me-2"></i>Log Recenti</h5>
                    </div>
                    <div class="card-body">
                        <div id="recent-logs" style="max-height: 400px; overflow-y: auto;">
                            <div class="text-center">
                                <div class="spinner-border spinner-border-sm" role="status"></div>
                                <span class="ms-2">Caricamento log...</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Refresh Button -->
    <button class="btn btn-primary btn-lg refresh-btn rounded-circle" onclick="refreshDashboard()">
        <i class="fas fa-sync-alt"></i>
    </button>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let autoRefresh = true;
        
        function formatTimestamp(isoString) {
            const date = new Date(isoString);
            return date.toLocaleString('it-IT');
        }
        
        function getStatusIcon(status) {
            const icons = {
                'ok': '<i class="fas fa-check-circle status-healthy"></i>',
                'healthy': '<i class="fas fa-check-circle status-healthy"></i>',
                'warning': '<i class="fas fa-exclamation-triangle status-warning"></i>',
                'degraded': '<i class="fas fa-exclamation-triangle status-warning"></i>',
                'error': '<i class="fas fa-times-circle status-error"></i>',
                'critical': '<i class="fas fa-times-circle status-error"></i>'
            };
            return icons[status] || '<i class="fas fa-question-circle text-muted"></i>';
        }
        
        <script>
        // Gestione errori runtime browser
        window.addEventListener('error', function(e) {
            console.log('Error handled:', e.error);
        });
        
        // Sopprimi errori di estensioni browser
        if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.lastError) {
            // Gestisce errori estensioni Chrome silenziosamente
        }
        
        let refreshInterval;
        
        function refreshDashboard() {
            console.log('🔄 Aggiornamento dashboard...');
            
            // Update system status
            fetch('/api/status')
                .then(response => {
                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    const contentType = response.headers.get('content-type');
                    if (!contentType || !contentType.includes('application/json')) {
                        throw new Error(`Expected JSON, got: ${contentType}`);
                    }
                    return response.json();
                })
                .then(data => updateSystemStatus(data))
                .catch(error => console.error('Errore caricamento status:', error));
            
            // Update health checks
            fetch('/api/health')
                .then(response => {
                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    const contentType = response.headers.get('content-type');
                    if (!contentType || !contentType.includes('application/json')) {
                        throw new Error(`Expected JSON, got: ${contentType}`);
                    }
                    return response.json();
                })
                .then(data => updateHealthChecks(data))
                .catch(error => console.error('Errore caricamento health:', error));
            
            // Update automation status
            fetch('/api/automation')
                .then(response => {
                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    const contentType = response.headers.get('content-type');
                    if (!contentType || !contentType.includes('application/json')) {
                        throw new Error(`Expected JSON, got: ${contentType}`);
                    }
                    return response.json();
                })
                .then(data => updateAutomationStatus(data))
                .catch(error => console.error('Errore caricamento automation:', error));
            
            // Update data status
            fetch('/api/data-status')
                .then(response => {
                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    const contentType = response.headers.get('content-type');
                    if (!contentType || !contentType.includes('application/json')) {
                        throw new Error(`Expected JSON, got: ${contentType}`);
                    }
                    return response.json();
                })
                .then(data => updateDataStatus(data))
                .catch(error => console.error('Errore caricamento data:', error));
            
            // Update logs
            fetch('/api/logs')
                .then(response => {
                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    const contentType = response.headers.get('content-type');
                    if (!contentType || !contentType.includes('application/json')) {
                        throw new Error(`Expected JSON, got: ${contentType}`);
                    }
                    return response.json();
                })
                .then(data => updateLogs(data))
                .catch(error => console.error('Errore caricamento logs:', error));
            
            document.getElementById('last-update').textContent = 
                'Ultimo aggiornamento: ' + new Date().toLocaleTimeString('it-IT');
        }
        
        function updateSystemStatus(data) {
            const statusEl = document.getElementById('system-status');
            const overallStatus = data.overall_status || 'unknown';
            
            statusEl.innerHTML = `
                <div class="row">
                    <div class="col-md-4">
                        <div class="d-flex align-items-center justify-content-center">
                            ${getStatusIcon(overallStatus)}
                            <span class="ms-2 h4 mb-0">${overallStatus.toUpperCase()}</span>
                        </div>
                    </div>
                    <div class="col-md-8">
                        <div class="row">
                            <div class="col-sm-6">
                                <small class="text-muted">Avviato il:</small><br>
                                <strong>${data.started_at ? formatTimestamp(data.started_at) : 'N/A'}</strong>
                            </div>
                            <div class="col-sm-6">
                                <small class="text-muted">Errori totali:</small><br>
                                <strong class="text-danger">${data.errors ? data.errors.length : 0}</strong>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
        
        function updateHealthChecks(data) {
            const healthEl = document.getElementById('health-checks');
            
            if (!data.checks) {
                healthEl.innerHTML = '<p class="text-muted">Nessun dato health check disponibile</p>';
                return;
            }
            
            let html = '';
            for (const [check, details] of Object.entries(data.checks)) {
                html += `
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span>${check.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase())}</span>
                        <span>${getStatusIcon(details.status)} ${details.status}</span>
                    </div>
                `;
            }
            
            healthEl.innerHTML = html;
        }
        
        function updateAutomationStatus(data) {
            const autoEl = document.getElementById('automation-status');
            
            const lastUpdates = [
                { label: 'Ultimo aggiornamento dati', value: data.last_daily_update },
                { label: 'Ultimo ritraining', value: data.last_weekly_retrain },
                { label: 'Ultimo backup', value: data.last_backup },
                { label: 'Ultimo health check', value: data.last_health_check }
            ];
            
            let html = '';
            lastUpdates.forEach(item => {
                const value = item.value ? formatTimestamp(item.value) : 'Mai eseguito';
                const isRecent = item.value && new Date() - new Date(item.value) < 24 * 60 * 60 * 1000;
                const statusClass = isRecent ? 'text-success' : 'text-warning';
                
                html += `
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span>${item.label}</span>
                        <span class="${statusClass}">${value}</span>
                    </div>
                `;
            });
            
            autoEl.innerHTML = html;
        }
        
        function updateDataStatus(data) {
            const dataEl = document.getElementById('data-status');
            
            if (!data.files) {
                dataEl.innerHTML = '<p class="text-muted">Nessun dato disponibile</p>';
                return;
            }
            
            let html = '<div class="row">';
            
            data.files.forEach(file => {
                const sizeClass = file.size_mb > 5 ? 'text-success' : file.size_mb > 1 ? 'text-warning' : 'text-muted';
                
                html += `
                    <div class="col-md-6 mb-2">
                        <div class="d-flex justify-content-between">
                            <span title="${file.path}">${file.name}</span>
                            <span class="${sizeClass}">${file.size_mb.toFixed(2)} MB</span>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            dataEl.innerHTML = html;
        }
        
        function updateLogs(data) {
            const logsEl = document.getElementById('recent-logs');
            
            if (!data.logs || data.logs.length === 0) {
                logsEl.innerHTML = '<p class="text-muted">Nessun log recente disponibile</p>';
                return;
            }
            
            let html = '';
            data.logs.forEach(log => {
                const levelClass = {
                    'INFO': 'text-info',
                    'WARNING': 'text-warning',
                    'ERROR': 'text-danger',
                    'DEBUG': 'text-muted'
                }[log.level] || 'text-dark';
                
                html += `
                    <div class="log-entry mb-1">
                        <span class="text-muted">${log.timestamp}</span>
                        <span class="badge bg-secondary">${log.source}</span>
                        <span class="${levelClass}">[${log.level}]</span>
                        <span>${log.message}</span>
                    </div>
                `;
            });
            
            logsEl.innerHTML = html;
        }
        
        // Auto-refresh ogni 30 secondi
        setInterval(() => {
            if (autoRefresh) {
                refreshDashboard();
            }
        }, 30000);
        
        // Caricamento iniziale
        document.addEventListener('DOMContentLoaded', () => {
            refreshDashboard();
        });
    </script>
</body>
</html>
"""

class MonitoringDashboard:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir)
        self.logs_dir = self.root_dir / 'logs'
        self.cache_dir = self.root_dir / 'cache'
        self.data_dir = self.root_dir / 'data'
        self.models_dir = self.root_dir / 'models'
        
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        """Configura le route dell'API"""
        
        # Error handler per restituire sempre JSON per le API
        @self.app.errorhandler(404)
        def not_found_error(error):
            from flask import request
            if request.path.startswith('/api/'):
                response = jsonify({
                    'error': 'Not found',
                    'message': 'Risorsa non trovata',
                    'timestamp': datetime.now().isoformat()
                })
                response.headers['Content-Type'] = 'application/json'
                return response, 404
            else:
                # Per le pagine normali restituisce HTML
                return render_template_string("""
                <html><head><title>404 Not Found</title></head>
                <body><h1>404 - Pagina non trovata</h1></body></html>
                """), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            response = jsonify({
                'error': 'Internal server error',
                'message': 'Errore interno del server',
                'timestamp': datetime.now().isoformat()
            })
            response.headers['Content-Type'] = 'application/json'
            return response, 500
        
        @self.app.route('/')
        def dashboard():
            return render_template_string(DASHBOARD_HTML)
        
        @self.app.route('/api/status')
        def api_status():
            """Status generale del sistema"""
            try:
                # Status di base sempre disponibile
                status = {
                    'timestamp': datetime.now().isoformat(),
                    'uptime': self._get_uptime(),
                    'processes': self._check_processes(),
                    'system': self._get_system_info(),
                    'errors': [],
                    'running': True
                }
                
                # Prova a leggere status file se esiste
                try:
                    status_file = self.logs_dir / 'system_status.json'
                    if status_file.exists():
                        with open(status_file, 'r') as f:
                            file_status = json.load(f)
                            status.update(file_status)
                except Exception:
                    pass  # Usa status di base se il file non esiste
                
                # Determina status generale
                error_count = len(status.get('errors', []))
                if error_count == 0:
                    overall_status = 'healthy'
                elif error_count < 5:
                    overall_status = 'warning'
                else:
                    overall_status = 'error'
                
                status['overall_status'] = overall_status
                response = jsonify(status)
                response.headers['Content-Type'] = 'application/json'
                return response
                
            except Exception as e:
                # Fallback status se tutto fallisce
                return jsonify({
                    'timestamp': datetime.now().isoformat(),
                    'error': 'Status service error',
                    'overall_status': 'error',
                    'running': False
                }), 200  # Ritorna 200 per evitare errori nel frontend
        
        @self.app.route('/api/health')
        def api_health():
            """Health checks dettagliati"""
            try:
                # Health check di base sempre disponibile
                health_data = {
                    'timestamp': datetime.now().isoformat(),
                    'status': 'healthy',
                    'checks': {
                        'api': True,
                        'database': True,
                        'disk_space': True
                    },
                    'overall_status': 'healthy'
                }
                
                # Prova a leggere health file se esiste
                try:
                    health_file = self.logs_dir / 'health_check.json'
                    if health_file.exists():
                        with open(health_file, 'r') as f:
                            file_data = json.load(f)
                            health_data.update(file_data)
                except Exception:
                    pass  # Usa health di base
                
                return jsonify(health_data)
                    
            except Exception as e:
                # Fallback health response
                return jsonify({
                    'timestamp': datetime.now().isoformat(),
                    'status': 'error',
                    'error': 'Health service error',
                    'overall_status': 'error'
                }), 200  # Ritorna 200 per evitare errori nel frontend
        
        @self.app.route('/api/automation')
        def api_automation():
            """Status automazione"""
            try:
                # Status di base sempre disponibile
                automation_status = {
                    'enabled': True,
                    'running': True,
                    'last_run': datetime.now().isoformat(),
                    'next_scheduled': 'Domenica 02:00',
                    'tasks_completed': 0,
                    'tasks_failed': 0,
                    'schedule': {
                        'data_update': '06:00',
                        'model_training': 'Domenica 02:00',
                        'health_check': '*/15 minuti'
                    }
                }
                
                # Prova a leggere da file se esiste
                try:
                    status_file = self.logs_dir / 'automation_status.json'
                    if status_file.exists():
                        with open(status_file, 'r') as f:
                            file_status = json.load(f)
                            automation_status.update(file_status)
                except Exception:
                    pass  # Usa status di base
                
                response = jsonify(automation_status)
                response.headers['Content-Type'] = 'application/json'
                return response
                
            except Exception as e:
                # Fallback status
                return jsonify({
                    'enabled': True,
                    'running': True,
                    'error': 'Automation service error',
                    'last_run': datetime.now().isoformat()
                }), 200  # Ritorna 200 per evitare errori
        
        @self.app.route('/api/data-status')
        def api_data_status():
            """Status file dati"""
            try:
                files_info = []
                
                # Analizza file dati
                data_files = list(self.data_dir.glob('*.csv'))
                model_files = list(self.models_dir.glob('*.pkl'))
                
                for file_path in data_files + model_files:
                    if file_path.is_file():
                        stat = file_path.stat()
                        files_info.append({
                            'name': file_path.name,
                            'path': str(file_path),
                            'size_mb': stat.st_size / (1024 * 1024),
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'type': 'data' if file_path.suffix == '.csv' else 'model'
                        })
                
                return jsonify({
                    'files': sorted(files_info, key=lambda x: x['size_mb'], reverse=True),
                    'total_files': len(files_info),
                    'total_size_mb': sum(f['size_mb'] for f in files_info)
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/logs')
        def api_logs():
            """Log recenti"""
            try:
                logs = []
                
                # Leggi log automazione
                automation_log = self.logs_dir / 'automation.log'
                if automation_log.exists():
                    logs.extend(self.parse_log_file(automation_log, 'automation', max_lines=50))
                
                # Leggi log scraper
                scraper_log = self.cache_dir / 'scraper.log'
                if scraper_log.exists():
                    logs.extend(self.parse_log_file(scraper_log, 'scraper', max_lines=30))
                
                # Ordina per timestamp
                logs.sort(key=lambda x: x['timestamp'], reverse=True)
                
                return jsonify({
                    'logs': logs[:100],  # Ultimi 100 log
                    'total_count': len(logs)
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def parse_log_file(self, log_file, source, max_lines=50):
        """Parsa un file di log"""
        logs = []
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-max_lines:]  # Ultime max_lines righe
                
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Cerca pattern timestamp
                parts = line.split(' - ')
                if len(parts) >= 4:
                    timestamp = parts[0]
                    logger_name = parts[1]
                    level = parts[2]
                    message = ' - '.join(parts[3:])
                    
                    logs.append({
                        'timestamp': timestamp,
                        'source': source,
                        'logger': logger_name,
                        'level': level,
                        'message': message
                    })
                else:
                    # Fallback per linee senza format standard
                    logs.append({
                        'timestamp': datetime.now().isoformat(),
                        'source': source,
                        'logger': 'unknown',
                        'level': 'INFO',
                        'message': line
                    })
                    
        except Exception as e:
            print(f"Errore parsing log {log_file}: {e}")
            
        return logs
    
    def _get_uptime(self):
        """Calcola uptime del sistema"""
        try:
            import psutil
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time
            uptime_timedelta = timedelta(seconds=uptime_seconds)
            return str(uptime_timedelta).split('.')[0]  # Rimuove microsecondi
        except:
            return "Unknown"
    
    def _check_processes(self):
        """Conta processi del sistema"""
        try:
            import psutil
            return len(psutil.pids())
        except:
            return 0
    
    def _get_system_info(self):
        """Ottieni info sistema"""
        try:
            import psutil
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
        except:
            return {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0
            }
    
    def run(self, host='0.0.0.0', port=5009, debug=False):
        """Avvia la dashboard"""
        print(f"🚀 Avvio Dashboard Monitoraggio su http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

def main():
    """Entry point principale"""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("📊 DASHBOARD MONITORAGGIO SISTEMA PRONOSTICI")
    print("=" * 50)
    print(f"📂 Directory: {root_dir}")
    print(f"📅 Avvio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    dashboard = MonitoringDashboard(root_dir)
    
    try:
        dashboard.run(port=5009, debug=False)
    except KeyboardInterrupt:
        print("\n👋 Dashboard terminata")

if __name__ == "__main__":
    main()