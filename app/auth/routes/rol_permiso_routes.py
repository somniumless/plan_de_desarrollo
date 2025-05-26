from flask import Blueprint, request, jsonify
from app import db
from models import RolPermiso

rol_permiso_bp = Blueprint('rol_permiso_bp', __name__)

@rol_permiso_bp.route('/rol_permiso', methods=['POST'])
def crear_rol_permiso():
    data = request.get_json()
    nuevo = RolPermiso(**data)
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({'mensaje': 'Asociación rol-permiso creada exitosamente'})

@rol_permiso_bp.route('/rol_permiso/<string:rol_id>/<string:permiso_id>', methods=['DELETE'])
def eliminar_rol_permiso(rol_id, permiso_id):
    relacion = RolPermiso.query.get_or_404((rol_id, permiso_id))
    db.session.delete(relacion)
    db.session.commit()
    return jsonify({'mensaje': 'Asociación eliminada exitosamente'})