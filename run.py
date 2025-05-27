from flask import Flask
from app.auth import init_app as init_auth
from app.documentos import init_documentos
from app.indicadores import init_indicadores
from app.metas import init_metas
from app.notificaciones import init_notificaciones
from app.reportes import init_reportes
from app.auth.routes import usuario_bp
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
