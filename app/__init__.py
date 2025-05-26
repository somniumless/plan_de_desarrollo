from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'clave-secreta-123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///seguimiento.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)

    from .auth.routes import auth as auth_blueprint
    from .metas.routes import metas as metas_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(metas_blueprint)

    return app
