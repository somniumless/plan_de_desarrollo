from flask import Blueprint
from .routes.routes import auditoria_bp 

def init_auditoria(app):
    app.register_blueprint(auditoria_bp)
    
    print("Módulo de Auditoría inicializado.")