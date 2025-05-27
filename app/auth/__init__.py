# app/auth/__init__.py

def init_app(app):
    from . import models 
    
    from .routes import blueprints
    for bp in blueprints:
        app.register_blueprint(bp)