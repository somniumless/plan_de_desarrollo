# app/auth/routes/__init__.py
from .usuario_routes import usuario_bp
from .rol_routes import rol_bp
from .permiso_routes import permiso_bp
from .rol_permiso_routes import rol_permiso_bp

blueprints = [
    usuario_bp,
    rol_bp,
    permiso_bp,
    rol_permiso_bp,
]