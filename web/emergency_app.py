#!/usr/bin/env python3
"""
🚨 APP DI EMERGENZA - Test rapido Render
App Flask minima per verificare che il deployment funzioni
"""

from flask import Flask, jsonify, render_template_string
import os
import sys
from datetime import datetime

# App Flask semplificata
app = Flask(__name__)

# Configurazione base
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'emergency-key-12345')

@app.route('/')
def home():
    """Homepage di emergenza"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚨 Sistema di Emergenza</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                text-align: center; 
                padding: 50px;
            }
            .container { 
                max-width: 600px; 
                margin: 0 auto; 
                background: rgba(255,255,255,0.1);
                padding: 30px;
                border-radius: 15px;
            }
            .status { 
                background: #4CAF50; 
                padding: 20px; 
                border-radius: 10px; 
                margin: 20px 0;
            }
            .button {
                background: #2196F3;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                margin: 10px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚨 Sistema di Emergenza</h1>
            <div class="status">
                ✅ RENDER FUNZIONA CORRETTAMENTE!
            </div>
            <p><strong>Timestamp:</strong> {{ timestamp }}</p>
            <p><strong>Environment:</strong> {{ env }}</p>
            
            <h3>🧪 Test API:</h3>
            <a href="/api/health" class="button">🔗 Test /api/health</a>
            <a href="/emergency-monitoring" class="button">📊 Monitoraggio Emergenza</a>
            
            <h3>📋 Status:</h3>
            <p>✅ Flask: Operativo</p>
            <p>✅ Render: Deployment riuscito</p>
            <p>✅ WSGI: Configurato</p>
            
            <p><em>L'app principale si sta inizializzando...</em></p>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, 
                                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                env=os.environ.get('RENDER', 'development'))

@app.route('/api/health')
def emergency_health():
    """API di health di emergenza"""
    return jsonify({
        'status': 'emergency_operational',
        'message': '🚨 Sistema di emergenza attivo',
        'timestamp': datetime.now().isoformat(),
        'environment': os.environ.get('RENDER', 'development'),
        'flask_working': True,
        'render_working': True,
        'note': 'App principale in inizializzazione'
    })

@app.route('/emergency-monitoring')
def emergency_monitoring():
    """Dashboard di monitoraggio di emergenza"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>📊 Monitoraggio di Emergenza</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white; 
                padding: 20px;
            }
            .container { max-width: 800px; margin: 0 auto; }
            .card { 
                background: rgba(255,255,255,0.1);
                padding: 20px;
                border-radius: 10px;
                margin: 15px 0;
            }
            .status-ok { color: #4CAF50; }
            .status-warning { color: #FF9800; }
            .button {
                background: #4CAF50;
                color: white;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                margin: 5px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Monitoraggio di Emergenza</h1>
            
            <div class="card">
                <h3>🟢 Status Sistema</h3>
                <p class="status-ok">✅ Render Deployment: Operativo</p>
                <p class="status-ok">✅ Flask App: Funzionante</p>
                <p class="status-ok">✅ WSGI Server: Attivo</p>
                <p class="status-warning">⚠️ App Principale: Inizializzazione in corso</p>
            </div>
            
            <div class="card">
                <h3>🔗 Test API</h3>
                <button class="button" onclick="testHealth()">Test Health</button>
                <button class="button" onclick="testMain()">Test App Principale</button>
                <div id="test-results" style="margin-top: 15px;"></div>
            </div>
            
            <div class="card">
                <h3>📅 Informazioni</h3>
                <p><strong>Deployment Time:</strong> {{ timestamp }}</p>
                <p><strong>Environment:</strong> {{ env }}</p>
                <p><strong>Status:</strong> Emergency Mode Active</p>
            </div>
        </div>
        
        <script>
        function testHealth() {
            fetch('/api/health')
            .then(response => response.json())
            .then(data => {
                document.getElementById('test-results').innerHTML = 
                    '<div style="background: #4CAF50; padding: 10px; border-radius: 5px;">' +
                    '✅ Health OK: ' + JSON.stringify(data, null, 2) + '</div>';
            })
            .catch(error => {
                document.getElementById('test-results').innerHTML = 
                    '<div style="background: #F44336; padding: 10px; border-radius: 5px;">' +
                    '❌ Error: ' + error + '</div>';
            });
        }
        
        function testMain() {
            fetch('/api/metrics_summary')
            .then(response => response.json())
            .then(data => {
                document.getElementById('test-results').innerHTML = 
                    '<div style="background: #4CAF50; padding: 10px; border-radius: 5px;">' +
                    '✅ App Principale OK!</div>';
            })
            .catch(error => {
                document.getElementById('test-results').innerHTML = 
                    '<div style="background: #FF9800; padding: 10px; border-radius: 5px;">' +
                    '⚠️ App principale ancora in inizializzazione</div>';
            });
        }
        </script>
    </body>
    </html>
    """
    return render_template_string(html,
                                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                env=os.environ.get('RENDER', 'development'))

# Configurazione per deployment
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# Per WSGI
application = app