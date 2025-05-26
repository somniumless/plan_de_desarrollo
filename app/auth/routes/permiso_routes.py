from flask import Blueprint, request, jsonify
from app import db
from models import Permiso

permiso_bp = Blueprint('permiso_bp', __name__)

@permiso_bp.route('/permisos', methods=['POST'])
def crear_permiso():
    data = request.get_json()
    nuevo_permiso = Permiso(**data)
    db.session.add(nuevo_permiso)
    db.session.commit()
    return jsonify({'mensaje': 'Permiso creado exitosamente'}), 201

@permiso_bp.route('/permisos', methods=['GET'])
def obtener_permisos():
    permisos = Permiso.query.all()
    return jsonify([p.__dict__ for p in permisos])

@permiso_bp.route('/permisos/<string:permiso_id>', methods=['GET'])
def obtener_permiso(permiso_id):
    permiso = Permiso.query.get_or_404(permiso_id)
    return jsonify(permiso.__dict__)

@permiso_bp.route('/permisos/<string:permiso_id>', methods=['PUT'])
def actualizar_permiso(permiso_id):
    permiso = Permiso.query.get_or_404(permiso_id)
    data = request.get_json()
    for key, value in data.items():
        setattr(permiso, key, value)
    db.session.commit()
    return jsonify({'mensaje': 'Permiso actualizado exitosamente'})

@permiso_bp.route('/permisos/<string:permiso_id>', methods=['DELETE'])
def eliminar_permiso(permiso_id):
    permiso = Permiso.query.get_or_404(permiso_id)
    db.session.delete(permiso)
    db.session.commit()
    return jsonify({'mensaje': 'Permiso eliminado exitosamente'})