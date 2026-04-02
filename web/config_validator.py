"""
ENV Configuration Validator

Valida variabili d'ambiente richieste al startup dell'applicazione.
Fail-fast se config critiche mancanti.

Usage:
    from web.config_validator import validate_config
    
    if __name__ == '__main__':
        validate_config()  # Fail se config errata
        app.run()
"""

import os
import sys
from typing import Dict, List, Tuple
import structlog

logger = structlog.get_logger(__name__)


def validate_config() -> Tuple[bool, List[str], List[str]]:
    """
    Valida configurazione environment variables.
    
    Returns:
        Tuple[bool, List[str], List[str]]: (is_valid, errors, warnings)
    """
    
    # === REQUIRED VARIABLES ===
    # Se mancanti, app NON può partire
    required_vars: Dict[str, str] = {
        'FLASK_ENV': 'Environment (production/development)',
        'ODDS_API_KEY': 'The Odds API key per quote reali',
    }
    
    # === OPTIONAL VARIABLES ===
    # Se mancanti, sistema usa fallback (warning only)
    optional_vars: Dict[str, str] = {
        'DATABASE_URL': 'PostgreSQL connection (fallback: CSV tracking)',
        'REDIS_URL': 'Redis cache (fallback: memory cache)',
        'SECRET_KEY': 'Flask secret key (fallback: random)',
        'PORT': 'Server port (fallback: 5000)',
    }
    
    # === VALIDATION ===
    errors: List[str] = []
    warnings: List[str] = []
    
    # Check required vars
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            errors.append(f"❌ {var} MANCANTE: {description}")
            logger.error(f"Required env var missing: {var}", description=description)
        else:
            # Validazione valore
            if var == 'ODDS_API_KEY' and len(value) < 20:
                errors.append(f"❌ {var} INVALIDA: troppo corta (min 20 chars)")
                logger.error(f"Invalid env var: {var}", length=len(value))
            else:
                logger.info(f"✅ {var} configurata", value_length=len(value))
    
    # Check optional vars
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if not value:
            warnings.append(f"⚠️  {var} non configurata - {description}")
            logger.warning(f"Optional env var missing: {var}", fallback=description)
        else:
            logger.info(f"✅ {var} configurata", value_present=True)
    
    # === ENVIRONMENT CHECKS ===
    flask_env = os.getenv('FLASK_ENV', 'development')
    if flask_env == 'production':
        # Production-specific checks
        if not os.getenv('DATABASE_URL'):
            warnings.append("⚠️  Production senza DATABASE_URL - tracking limitato a CSV")
        
        if not os.getenv('SECRET_KEY'):
            warnings.append("⚠️  Production senza SECRET_KEY - sessions non sicure")
    
    # === RESULT ===
    is_valid = len(errors) == 0
    
    if errors:
        logger.error("❌ Config validation FAILED", error_count=len(errors))
        for error in errors:
            print(error, file=sys.stderr)
    
    if warnings:
        logger.warning(f"⚠️  Config warnings: {len(warnings)}", warning_count=len(warnings))
        for warning in warnings:
            print(warning)
    
    if is_valid and not warnings:
        logger.info("✅ Config validation passed - all required vars set")
    elif is_valid:
        logger.info("✅ Config validation passed with warnings", warning_count=len(warnings))
    
    return is_valid, errors, warnings


def validate_or_exit():
    """
    Valida config e exit se fallisce.
    Usare in startup per fail-fast behavior.
    """
    is_valid, errors, warnings = validate_config()
    
    if not is_valid:
        print("\n╔════════════════════════════════════════╗", file=sys.stderr)
        print("║  ❌ CONFIG VALIDATION FAILED          ║", file=sys.stderr)
        print("╚════════════════════════════════════════╝", file=sys.stderr)
        print("\nFix configuration prima di avviare l'app:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        print("\nExample .env file:", file=sys.stderr)
        print("  FLASK_ENV=production", file=sys.stderr)
        print("  ODDS_API_KEY=your_api_key_here", file=sys.stderr)
        print("  DATABASE_URL=postgresql://...", file=sys.stderr)
        print("  REDIS_URL=redis://localhost:6379/0", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    # Test validation
    print("🔍 Testing config validation...\n")
    is_valid, errors, warnings = validate_config()
    
    print(f"\n{'='*50}")
    print(f"Result: {'✅ PASS' if is_valid else '❌ FAIL'}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    print(f"{'='*50}")
