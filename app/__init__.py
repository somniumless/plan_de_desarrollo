from flask import Flask
from app.extensiones import db, login_manager, migrate

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'clave-secreta-123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/proyecto_zipaquira'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa extensiones
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    migrate.init_app(app, db)

    # Importa y registra blueprints
    with app.app_context():
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

        # Importa modelos después de inicializar db
        from app.auth.models import Usuario, Rol, Permiso, RolPermiso
        from app.indicadores.models import Indicador, MetaIndicador
        from app.metas.models import Meta, Avance, EntidadResponsable, MetaEntidad

        # Crea tablas si no existen
        db.create_all()

    return app