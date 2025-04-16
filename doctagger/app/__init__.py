# Main app initialization
from flask import Flask
from .config import config

app = None

def create_app(config_name='default'):
    global app
    app = Flask(__name__, template_folder='web/templates', static_folder='../static')
    app.config.from_object(config[config_name])
    
    # Register blueprints
    from .web.routes import web_bp
    app.register_blueprint(web_bp)
    
    return app