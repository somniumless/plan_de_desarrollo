from flask import Blueprint
from .indicador_meta_routes import meta_indicador_bp
from .indicador_routes import indicador_bp

blueprints = [
    meta_indicador_bp, 
    indicador_bp
]
