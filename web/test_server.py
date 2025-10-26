#!/usr/bin/env python3
"""
Server di test minimo per debug
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({'status': 'Server di test attivo', 'message': 'OK'})

@app.route('/api/test', methods=['POST'])
def test_api():
    try:
        data = request.json
        print(f"🔍 Dati ricevuti: {data}")
        
        # Test semplice
        result = {
            'predizione': 'H',
            'confidenza': 0.75,
            'probabilita': {
                'H': 0.75,
                'D': 0.15,
                'A': 0.10
            },
            'test': True
        }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Errore test: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    print("🚀 Avvio server di test...")
    app.run(debug=False, host="0.0.0.0", port=5002)