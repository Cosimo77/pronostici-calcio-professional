"""
🏓 Keep-Alive Service per Render Free Tier
Previene lo sleep del server dopo 15 minuti
"""

import requests
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RENDER_URL = "https://pronostici-calcio-professional.onrender.com"
PING_INTERVAL = 600  # 10 minuti (in secondi)

def ping_server():
    """Ping server per mantenerlo attivo"""
    try:
        response = requests.get(f"{RENDER_URL}/health", timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ Server alive at {datetime.now()}")
            return True
        else:
            logger.warning(f"⚠️ Server responded with {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Ping failed: {e}")
        return False

def main():
    """Loop infinito di keep-alive"""
    logger.info(f"🏓 Keep-Alive Service started for {RENDER_URL}")
    logger.info(f"⏰ Ping interval: {PING_INTERVAL}s ({PING_INTERVAL/60:.0f} minutes)")
    
    while True:
        ping_server()
        time.sleep(PING_INTERVAL)

if __name__ == "__main__":
    main()
