
from flask import Blueprint, request, jsonify
from app import db
from metas.models import MetaEntidad

meta_entidad_bp = Blueprint('meta_entidad', __name__, url_prefix='/meta_entidades')

def meta_entidad_to_dict(me):
    return {
        'meta_id': me.meta_id,
        'entidad_id': me.entidad_id,
    }

@meta_entidad_bp.route('/', methods=['POST'])
def crear_meta_entidad():
    data = request.get_json()
    me = MetaEntidad(**data)
    db.session.add(me)
    db.session.commit()
    return jsonify({'mensaje': 'MetaEntidad creada exitosamente'}), 201

@meta_entidad_bp.route('/', methods=['GET'])
def listar_meta_entidades():
    relaciones = MetaEntidad.query.all()
    return jsonify([meta_entidad_to_dict(r) for r in relaciones])

@meta_entidad_bp.route('/<string:meta_id>/<string:entidad_id>', methods=['GET'])
def obtener_meta_entidad(meta_id, entidad_id):
    me = MetaEntidad.query.get_or_404((meta_id, entidad_id))
    return jsonify(meta_entidad_to_dict(me))

@meta_entidad_bp.route('/<string:meta_id>/<string:entidad_id>', methods=['DELETE'])
def eliminar_meta_entidad(meta_id, entidad_id):
    me = MetaEntidad.query.get_or_404((meta_id, entidad_id))
    db.session.delete(me)
    db.session.commit()
    return jsonify({'mensaje': 'MetaEntidad eliminada exitosamente'})
