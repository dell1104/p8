# production_config.py - Configuración segura para producción

import os
from config import Config

class SecureProductionConfig(Config):
    """Configuración de producción con máxima seguridad"""
    
    # Configuración de base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/database.db'
    
    # Configuración de seguridad crítica
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
    
    # Configuración de sesiones seguras
    SESSION_COOKIE_SECURE = True  # Solo HTTPS
    SESSION_COOKIE_HTTPONLY = True  # No acceso via JavaScript
    SESSION_COOKIE_SAMESITE = 'Strict'  # Máxima protección CSRF
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutos
    
    # Configuración de archivos
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB máximo
    
    # Configuración de logging
    LOG_LEVEL = 'WARNING'
    LOG_FILE = 'logs/application.log'
    
    # Configuración de rate limiting más estricta
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_DEFAULT = "100 per hour, 20 per minute"
    
    # Configuración de CORS restrictiva
    CORS_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '').split(',')
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    
    # Configuración de archivos permitidos más restrictiva
    ALLOWED_EXTENSIONS = {
        'audio': {'mp3', 'wav', 'm4a'},
        'video': {'mp4', 'avi', 'mov'},
        'image': {'jpg', 'jpeg', 'png'},
        'document': {'pdf', 'doc', 'docx', 'txt'}
    }
    
    # Configuración de seguridad adicional
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 1800  # 30 minutos
    
    # Configuración de headers de seguridad
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
        'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'",
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
    }

# Configuración de logging para producción
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'security': {
            'format': '%(asctime)s [SECURITY] %(levelname)s: %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'WARNING',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/application.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
        'security_file': {
            'level': 'INFO',
            'formatter': 'security',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/security.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
        }
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': False
        },
        'security': {
            'handlers': ['security_file'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

# Variables de entorno requeridas para producción
REQUIRED_ENV_VARS = [
    'SECRET_KEY',
    'DATABASE_URL',
    'ALLOWED_ORIGINS'
]

def validate_production_config():
    """Validar configuración de producción"""
    missing_vars = []
    
    for var in REQUIRED_ENV_VARS:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Variables de entorno faltantes: {', '.join(missing_vars)}")
    
    return True
