"""
Configurazione Sicurezza Enterprise
Modulo per gestire configurazioni di sicurezza avanzate
"""

import os
from datetime import timedelta

class SecurityConfig:
    """Configurazioni di sicurezza enterprise"""
    
    # Secret key sicura
    SECRET_KEY = os.environ.get('SECRET_KEY', 'professional_calcio_system_2025_secure')
    
    # Content Security Policy
    CSP_CONFIG = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net",
        'style-src': "'self' 'unsafe-inline' https://fonts.googleapis.com",
        'font-src': "'self' https://fonts.gstatic.com",
        'img-src': "'self' data: https:",
        'connect-src': "'self'",
        'frame-ancestors': "'none'",
        'base-uri': "'self'",
        'form-action': "'self'"
    }
    
    # Rate limiting configurations
    RATE_LIMITS = {
        'default': "1000 per hour, 100 per minute",
        'predict_enterprise': "30 per minute",
        'api_endpoints': "60 per minute", 
        'health_check': "120 per minute",
        'metrics': "30 per minute"
    }
    
    # Security headers
    SECURITY_HEADERS = {
        'force_https': False,  # Per sviluppo locale
        'strict_transport_security': True,
        'strict_transport_security_max_age': 31536000,
        'content_security_policy': CSP_CONFIG,
        'referrer_policy': 'strict-origin-when-cross-origin',
        'x_content_type_options': True,
        'x_frame_options': 'DENY',
        'x_xss_protection': True
    }
    
    # Configurazione sessioni
    SESSION_CONFIG = {
        'permanent_session_lifetime': timedelta(hours=24),
        'session_cookie_secure': True,  # Solo HTTPS in produzione
        'session_cookie_httponly': True,
        'session_cookie_samesite': 'Lax'
    }

class MonitoringConfig:
    """Configurazioni per monitoring e metriche"""
    
    # Metriche da tracciare
    METRICS_CONFIG = {
        'enable_prometheus': True,
        'enable_structured_logging': True,
        'log_format': 'json',
        'log_level': 'INFO'
    }
    
    # Health check endpoints
    HEALTH_ENDPOINTS = [
        '/api/health',
        '/api/metrics', 
        '/health'  # Endpoint semplificato per load balancer
    ]