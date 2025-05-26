
from .models import Indicador, MetaIndicador

def init_indicadores(app):
    from .routes import blueprints

    for bp in blueprints:
        app.register_blueprint(bp)

