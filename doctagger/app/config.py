# Configuration settings
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-testing'
    API_BASE_URL = os.environ.get('API_BASE_URL') or 'https://classiapi.data443.com'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.abspath('uploads')
    PROCESSED_FOLDER = os.environ.get('PROCESSED_FOLDER') or os.path.abspath('processed')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload size
    MAX_WORKERS = int(os.environ.get('MAX_WORKERS') or 5)
    TAG_NAME = os.environ.get('TAG_NAME') or 'Data Class'
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}