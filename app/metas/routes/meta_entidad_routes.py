# app/metas/routes/meta_entidad_routes.py

from flask import Blueprint, request, jsonify
from app import db 
from app.metas.models import MetaEntidad, Meta, EntidadResponsable 
from app.auditoria.utils import registrar_auditoria, ResultadoAccion
from app.auditoria.decorators import audit_action
from flask_login import current_user 

meta_entidad_bp = Blueprint('meta_entidad_bp', __name__, url_prefix='/meta_entidades') 

def meta_entidad_to_dict(me):
    return {
        'meta_id': me.meta_id,
        'entidad_id': me.entidad_id,
        'fecha_asignacion': me.fecha_asignacion.isoformat() if me.fecha_asignacion else None,
    }

@meta_entidad_bp.route('/', methods=['POST'])
@audit_action(
    accion='ASIGNAR_ENTIDAD_A_META',
    entidad_afectada_name='MetaEntidad',
    include_args_in_details=['data'], 
    obj_id_attr=None 
)
def crear_meta_entidad():
    data = request.get_json()
    meta_id = data.get('meta_id')
    entidad_id = data.get('entidad_id')

    if not meta_id or not entidad_id:
        return jsonify({'error': 'meta_id y entidad_id son obligatorios'}), 400

    me = MetaEntidad(meta_id=meta_id, entidad_id=entidad_id)
    db.session.add(me)
    db.session.commit()
    return jsonify({'mensaje': 'MetaEntidad creada exitosamente', 'data': meta_entidad_to_dict(me)}), 201

@meta_entidad_bp.route('/', methods=['GET'])
def listar_meta_entidades():
    relaciones = MetaEntidad.query.all()
    return jsonify([meta_entidad_to_dict(r) for r in relaciones])

@meta_entidad_bp.route('/<string:meta_id>/<string:entidad_id>', methods=['GET'])
def obtener_meta_entidad(meta_id, entidad_id):
    me = MetaEntidad.query.get_or_404((meta_id, entidad_id))
    return jsonify(meta_entidad_to_dict(me))

@meta_entidad_bp.route('/<string:meta_id>/<string:entidad_id>', methods=['DELETE'])
@audit_action(
    accion='ELIMINAR_ASIGNACION_ENTIDAD_A_META',
    entidad_afectada_name='MetaEntidad',
    id_param_name='meta_id', 
    include_args_in_details=['entidad_id'] 
)
def eliminar_meta_entidad(meta_id, entidad_id):
    me = MetaEntidad.query.get_or_404((meta_id, entidad_id))
    db.session.delete(me)
    db.session.commit()
    return jsonify({'mensaje': 'MetaEntidad eliminada exitosamente'}), 200