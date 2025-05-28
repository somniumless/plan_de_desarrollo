from flask import Flask
from app.extensiones import db, login_manager, migrate
from app.main import routes as main_routes
from app.auth.routes.usuario_routes import usuario_bp
from app.static_files import routes as static_files_routes 
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'clave-secreta-123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/proyecto_zipaquira'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'usuario_bp.login'
    login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
    login_manager.login_message_category = "info"
    migrate.init_app(app, db)

    CORS(app)

    from app.auth.models import Usuario
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(str(user_id))

    app.register_blueprint(main_routes.main_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(static_files_routes.static_files_bp) 

    with app.app_context():
        from app.auth.models import Usuario, Rol, Permiso, RolPermiso, EntidadResponsable
        from app.indicadores.models import Indicador, MetaIndicador
        from app.metas.models import Meta, Avance, MetaEntidad
        from app.notificaciones.models import Notificacion
        from app.reportes.models import Reporte
        from app.auditoria.models import Auditoria

        db.create_all()

        if Rol.query.count() == 0:
            from app.seed_db import seed_db
            seed_db()
        else:
            print("La base de datos ya contiene datos, omitiendo la siembra.")

        from .metas import init_metas
        from .indicadores import init_indicadores
        from .documentos import init_documentos 
        from .notificaciones import init_notificaciones
        from .reportes import init_reportes
        from .auditoria import init_auditoria

        init_metas(app)
        init_indicadores(app)
        init_documentos(app)
        init_notificaciones(app)
        init_reportes(app)
        init_auditoria(app)

    return app