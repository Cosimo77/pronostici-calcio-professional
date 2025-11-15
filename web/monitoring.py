#!/usr/bin/env python3
"""
Sistema di Monitoring Leggero per Production
Alternativa a Prometheus/Grafana per quick deploy
"""

import logging
import json
import time
from datetime import datetime
from functools import wraps
from typing import Dict, Any, Optional, Callable
import traceback
from pathlib import Path


class StructuredLogger:
    """Logger con output JSON strutturato per production"""
    
    def __init__(self, name: str = 'pronostici_app'):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Rimuovi handler esistenti
        self.logger.handlers.clear()
        
        # Console handler per development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler per production (JSON)
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        file_handler = logging.FileHandler(log_dir / 'app_structured.log')
        file_handler.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
    
    def _log_json(self, level: str, message: str, **kwargs):
        """Log messaggio in formato JSON"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'message': message,
            **kwargs
        }
        
        # Log su file come JSON
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.stream.write(json.dumps(log_entry) + '\n')
                handler.stream.flush()
        
        # Log su console human-readable
        self.logger.log(
            getattr(logging, level.upper()),
            f"{message} {json.dumps(kwargs) if kwargs else ''}"
        )
    
    def info(self, message: str, **kwargs):
        """Log INFO level"""
        self._log_json('info', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log WARNING level"""
        self._log_json('warning', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log ERROR level"""
        self._log_json('error', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log CRITICAL level"""
        self._log_json('critical', message, **kwargs)


class PerformanceMonitor:
    """Monitor performance delle route Flask"""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {}
        self.logger = StructuredLogger('performance')
    
    def record(self, endpoint: str, duration: float, status_code: int):
        """Registra metrica performance"""
        if endpoint not in self.metrics:
            self.metrics[endpoint] = []
        
        self.metrics[endpoint].append({
            'duration': duration,
            'status_code': status_code,
            'timestamp': time.time()
        })
        
        # Mantieni solo ultimi 1000 record per endpoint
        if len(self.metrics[endpoint]) > 1000:
            self.metrics[endpoint] = self.metrics[endpoint][-1000:]
        
        # Log se troppo lento (>2s)
        if duration > 2.0:
            self.logger.warning(
                'Slow endpoint detected',
                endpoint=endpoint,
                duration_seconds=round(duration, 3),
                status_code=status_code
            )
    
    def get_stats(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Ottieni statistiche performance"""
        if endpoint:
            return self._stats_for_endpoint(endpoint)
        
        # Stats per tutti gli endpoint
        all_stats = {}
        for ep in self.metrics.keys():
            all_stats[ep] = self._stats_for_endpoint(ep)
        
        return all_stats
    
    def _stats_for_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Statistiche per singolo endpoint"""
        if endpoint not in self.metrics or not self.metrics[endpoint]:
            return {
                'count': 0,
                'avg_duration': 0,
                'min_duration': 0,
                'max_duration': 0,
                'p95_duration': 0,
                'p99_duration': 0,
                'error_rate': 0
            }
        
        records = self.metrics[endpoint]
        durations = [r['duration'] for r in records]
        errors = [r for r in records if r['status_code'] >= 400]
        
        durations_sorted = sorted(durations)
        n = len(durations_sorted)
        
        return {
            'count': n,
            'avg_duration': round(sum(durations) / n, 3),
            'min_duration': round(min(durations), 3),
            'max_duration': round(max(durations), 3),
            'p95_duration': round(durations_sorted[int(n * 0.95)] if n > 0 else 0, 3),
            'p99_duration': round(durations_sorted[int(n * 0.99)] if n > 0 else 0, 3),
            'error_rate': round(len(errors) / n * 100, 2) if n > 0 else 0
        }


class ErrorTracker:
    """Traccia errori applicazione"""
    
    def __init__(self):
        self.errors: list = []
        self.logger = StructuredLogger('errors')
    
    def record_error(self, error: Exception, context: Optional[Dict] = None):
        """Registra errore"""
        error_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }
        
        self.errors.append(error_data)
        
        # Mantieni solo ultimi 500 errori
        if len(self.errors) > 500:
            self.errors = self.errors[-500:]
        
        # Log su file
        self.logger.error(
            'Application error occurred',
            error_type=error_data['error_type'],
            error_message=error_data['error_message'],
            context=error_data['context']
        )
    
    def get_recent_errors(self, limit: int = 50) -> list:
        """Ottieni errori recenti"""
        return self.errors[-limit:]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Riassunto errori"""
        if not self.errors:
            return {
                'total_errors': 0,
                'error_types': {},
                'last_error': None
            }
        
        error_types = {}
        for error in self.errors:
            error_type = error['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            'total_errors': len(self.errors),
            'error_types': error_types,
            'last_error': self.errors[-1] if self.errors else None
        }


# Singleton instances
_logger = StructuredLogger()
_performance_monitor = PerformanceMonitor()
_error_tracker = ErrorTracker()


def get_logger() -> StructuredLogger:
    """Get global logger instance"""
    return _logger


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor"""
    return _performance_monitor


def get_error_tracker() -> ErrorTracker:
    """Get global error tracker"""
    return _error_tracker


def monitor_performance(endpoint_name: Optional[str] = None):
    """Decorator per monitorare performance route"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 200
            
            try:
                result = func(*args, **kwargs)
                
                # Estrai status code se presente
                if isinstance(result, tuple) and len(result) > 1:
                    status_code = result[1]
                
                return result
            
            except Exception as e:
                status_code = 500
                _error_tracker.record_error(e, {
                    'endpoint': endpoint_name or func.__name__
                })
                raise
            
            finally:
                duration = time.time() - start_time
                endpoint = endpoint_name or func.__name__
                _performance_monitor.record(endpoint, duration, status_code)
        
        return wrapper
    return decorator


def log_request(request_data: Dict[str, Any]):
    """Log HTTP request"""
    _logger.info(
        'HTTP request received',
        method=request_data.get('method'),
        path=request_data.get('path'),
        remote_addr=request_data.get('remote_addr'),
        user_agent=request_data.get('user_agent')
    )


def log_cache_hit(key: str, hit: bool):
    """Log cache hit/miss"""
    _logger.info(
        'Cache access',
        key=key,
        hit=hit,
        action='hit' if hit else 'miss'
    )


def log_api_call(api_name: str, success: bool, duration: float):
    """Log external API call"""
    _logger.info(
        'External API call',
        api_name=api_name,
        success=success,
        duration_seconds=round(duration, 3)
    )
