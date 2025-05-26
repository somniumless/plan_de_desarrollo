from flask import Blueprint, request, jsonify
from .models import Auditoria
from app import db

auditoria_bp = Blueprint('auditoria', __name__, url_prefix='/auditoria')

@auditoria_bp.route('/logs', methods=['GET'])
def get_logs():
    logs = Auditoria.query.order_by(Auditoria.fecha_accion.desc()).limit(100).all()
    return jsonify([{
        "accion": log.accion,
        "usuario_id": log.usuario_id,
        "fecha_accion": log.fecha_accion
    } for log in logs])