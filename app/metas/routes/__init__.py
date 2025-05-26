from .metas_routes import metas_bp
from .avance_routes import avances_bp
from .entidad_responsable_routes import entidades_bp
from .meta_entidad_routes import meta_entidad_bp


blueprints = [
    metas_bp,
    avances_bp,
    entidades_bp,
    meta_entidad_bp
]
