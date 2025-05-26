from flask import Blueprint, request, jsonify
from .models import Notificacion
from app import db

notificaciones_bp = Blueprint('notificaciones', __name__, url_prefix='/notificaciones')

@notificaciones_bp.route('/user/<usuario_id>', methods=['GET'])
def get_notifications(usuario_id):
    notificaciones = Notificacion.query.filter_by(usuario_id=usuario_id).all()
    return jsonify([{
        "titulo": n.titulo,
        "mensaje": n.mensaje,
        "leida": n.leida
    } for n in notificaciones])