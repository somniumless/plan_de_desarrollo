def init_metas(app):
    from .routes import blueprints
    for bp in blueprints:
        app.register_blueprint(bp)