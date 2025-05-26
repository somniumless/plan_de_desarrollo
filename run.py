from flask import Flask
from app.auth import init_app as init_auth
from app.documentos import init_app as init_documentos

app = Flask(__name__)  # Esto debe ir primero

# Inicializas auth y documentos
init_auth(app)
init_documentos(app)

if __name__ == '__main__':
    app.run(debug=True)
