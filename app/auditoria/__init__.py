from .routes import auditoria_bp
from flask import Flask

def create_app():
    app = Flask(__name__)
    # ... otras configuraciones ...

    app.register_blueprint(auditoria_bp)

    return app
