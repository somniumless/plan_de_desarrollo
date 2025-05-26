from flask import Blueprint, request, jsonify
from app import db
from models import Rol

rol_bp = Blueprint('rol_bp', __name__)

@rol_bp.route('/roles', methods=['POST'])
def crear_rol():
    data = request.get_json()
    nuevo_rol = Rol(**data)
    db.session.add(nuevo_rol)
    db.session.commit()
    return jsonify({'mensaje': 'Rol creado exitosamente'}), 201

@rol_bp.route('/roles', methods=['GET'])
def obtener_roles():
    roles = Rol.query.all()
    return jsonify([r.__dict__ for r in roles])

@rol_bp.route('/roles/<string:rol_id>', methods=['GET'])
def obtener_rol(rol_id):
    rol = Rol.query.get_or_404(rol_id)
    return jsonify(rol.__dict__)

@rol_bp.route('/roles/<string:rol_id>', methods=['PUT'])
def actualizar_rol(rol_id):
    rol = Rol.query.get_or_404(rol_id)
    data = request.get_json()
    for key, value in data.items():
        setattr(rol, key, value)
    db.session.commit()
    return jsonify({'mensaje': 'Rol actualizado exitosamente'})

@rol_bp.route('/roles/<string:rol_id>', methods=['DELETE'])
def eliminar_rol(rol_id):
    rol = Rol.query.get_or_404(rol_id)
    db.session.delete(rol)
    db.session.commit()
    return jsonify({'mensaje': 'Rol eliminado exitosamente'})