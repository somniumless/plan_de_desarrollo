def init_app(app):
    from .routes import blueprints
    for bp in blueprints:
        app.register_blueprint(bp)
