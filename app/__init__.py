from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from app.extensiones import db  # ✅ Importas la instancia ya creada

login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'clave-secreta-123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/proyecto_zipaquira'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)  # ✅ Conecta la instancia a la app
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)

    # Importar y registrar Blueprints desde funciones init_*
    from .auth import init_app as init_auth 
    from .metas import init_metas
    from .indicadores import init_indicadores
    from .documentos import init_documentos
    from .notificaciones import init_notificaciones
    from .reportes import init_reportes
    from .auditoria import init_auditoria

    init_auth(app)
    init_metas(app)
    init_indicadores(app)
    init_documentos(app)
    init_notificaciones(app)
    init_reportes(app) 
    init_auditoria(app)

    return app
