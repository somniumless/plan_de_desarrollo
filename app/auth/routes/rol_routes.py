from flask import Blueprint, request, jsonify
from app import db 
from app.auth.models import Rol
from app.auditoria.utils import registrar_auditoria, ResultadoAccion
from app.auditoria.decorators import audit_action

rol_bp = Blueprint('rol_bp', __name__)

def rol_to_dict(rol):
    return {
        'rol_id': rol.rol_id,
        'nombre': rol.nombre,
        'descripcion': rol.descripcion,
        'fecha_creacion': rol.fecha_creacion.isoformat() if rol.fecha_creacion else None,
        'fecha_actualizacion': rol.fecha_actualizacion.isoformat() if rol.fecha_actualizacion else None
    }

@rol_bp.route('/roles', methods=['POST'])
@audit_action(
    accion='CREAR_ROL',
    entidad_afectada_name='Rol',
    include_args_in_details=['data'], 
    obj_id_attr='rol_id' 
)
def crear_rol():
    data = request.get_json()
    nuevo_rol = Rol(**data)
    db.session.add(nuevo_rol)
    db.session.commit()
    return jsonify({'mensaje': 'Rol creado exitosamente', 'rol_id': nuevo_rol.rol_id}), 201

@rol_bp.route('/roles', methods=['GET'])
def obtener_roles():
    roles = Rol.query.all()
    return jsonify([rol_to_dict(r) for r in roles])

@rol_bp.route('/roles/<string:rol_id>', methods=['GET'])
def obtener_rol(rol_id):
    rol = Rol.query.get_or_404(rol_id)
    return jsonify(rol_to_dict(rol))

@rol_bp.route('/roles/<string:rol_id>', methods=['PUT'])
@audit_action(
    accion='ACTUALIZAR_ROL',
    entidad_afectada_name='Rol',
    id_param_name='rol_id', 
    include_args_in_details=['data']
)
def actualizar_rol(rol_id):
    rol = Rol.query.get_or_404(rol_id)
    data = request.get_json()
    for key, value in data.items():
        setattr(rol, key, value)
    db.session.commit()
    return jsonify({'mensaje': 'Rol actualizado exitosamente'})

@rol_bp.route('/roles/<string:rol_id>', methods=['DELETE'])
@audit_action(
    accion='ELIMINAR_ROL',
    entidad_afectada_name='Rol',
    id_param_name='rol_id', 
    include_obj_attrs_in_details=['nombre'] 
)
def eliminar_rol(rol_id):
    rol = Rol.query.get_or_404(rol_id)
    db.session.delete(rol)
    db.session.commit()
    return jsonify({'mensaje': 'Rol eliminado exitosamente'})