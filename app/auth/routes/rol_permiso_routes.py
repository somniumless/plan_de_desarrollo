from flask import Blueprint, request, jsonify
from app import db 
from app.auth.models import RolPermiso, Rol, Permiso 
from app.auditoria.utils import registrar_auditoria, ResultadoAccion
from app.auditoria.decorators import audit_action
from flask_login import current_user 

rol_permiso_bp = Blueprint('rol_permiso_bp', __name__)

def rol_permiso_to_dict(relacion):
    return {
        'rol_id': relacion.rol_id,
        'permiso_id': relacion.permiso_id,
        'fecha_asignacion': relacion.fecha_asignacion.isoformat() if relacion.fecha_asignacion else None
    }

@rol_permiso_bp.route('/rol_permiso', methods=['POST'])
@audit_action(
    accion='ASIGNAR_PERMISO_A_ROL',
    entidad_afectada_name='RolPermiso',
    include_args_in_details=['data'],
    obj_id_attr=None 
)
def crear_rol_permiso():
    data = request.get_json()
    rol_id = data.get('rol_id')
    permiso_id = data.get('permiso_id')

    if not rol_id or not permiso_id:
        return jsonify({'error': 'rol_id y permiso_id son obligatorios'}), 400

    nuevo = RolPermiso(rol_id=rol_id, permiso_id=permiso_id)
    db.session.add(nuevo)
    db.session.commit()

    return jsonify({'mensaje': 'Asociación rol-permiso creada exitosamente', 'data': rol_permiso_to_dict(nuevo)}), 201

@rol_permiso_bp.route('/rol_permiso', methods=['GET'])
def obtener_rol_permisos():
    relaciones = RolPermiso.query.all()
    return jsonify([rol_permiso_to_dict(r) for r in relaciones])

@rol_permiso_bp.route('/rol_permiso/<string:rol_id>/<string:permiso_id>', methods=['GET'])
def obtener_rol_permiso(rol_id, permiso_id):
    relacion = RolPermiso.query.get_or_404((rol_id, permiso_id))
    return jsonify(rol_permiso_to_dict(relacion))


@rol_permiso_bp.route('/rol_permiso/<string:rol_id>/<string:permiso_id>', methods=['DELETE'])
@audit_action(
    accion='REVOCAR_PERMISO_DE_ROL',
    entidad_afectada_name='RolPermiso',
    id_param_name='rol_id',
    include_args_in_details=['permiso_id']
)
def eliminar_rol_permiso(rol_id, permiso_id):
    relacion = RolPermiso.query.get_or_404((rol_id, permiso_id))
    db.session.delete(relacion)
    db.session.commit()

    return jsonify({'mensaje': 'Asociación eliminada exitosamente'}), 200