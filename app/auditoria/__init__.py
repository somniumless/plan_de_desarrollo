def init_auditoria(app):
    from routes import auditoria_bp 
    app.register_blueprint(auditoria_bp )

