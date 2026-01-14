# config.py
"""Конфігурація додатку"""
import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Базова конфігурація"""
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        if os.getenv('FLASK_ENV') == 'production':
            raise RuntimeError("SECRET_KEY must be set in production!")
        else:
            SECRET_KEY = secrets.token_hex(32)
    
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    
    MONGODB_URI = os.getenv('MONGODB_URI')
    if not MONGODB_URI:
        raise RuntimeError("MONGODB_URI must be set!")
    
    APP_VERSION = os.getenv('APP_VERSION', '1.5.0')
    DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'


def get_config():
    """Отримати поточну конфігурацію"""
    return Config
