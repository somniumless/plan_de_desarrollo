from flask import Flask
from app.auth import init_app as init_auth
from app.documentos import init_app as init_documentos
from app.indicadores import init_indicadores
from app.metas import init_metas
from app.notificaciones import init_notificaciones
from app.reportes import init_reportes
from app import create_app

app = Flask(__name__)  

app = create_app()
init_auth(app)
init_documentos(app)
init_indicadores(app)
init_metas(app)
init_notificaciones(app)
init_reportes(app)

if __name__ == '__main__':
    app.run(debug=True)
