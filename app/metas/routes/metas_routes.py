from flask import Blueprint, request, jsonify
from app import db
from metas.models import Meta

meta_bp = Blueprint('meta', __name__, url_prefix='/metas')

def meta_to_dict(meta):
    return {
        'meta_id': meta.meta_id,
        'nombre': meta.nombre,
        'meta_resultado': meta.meta_resultado,
        'descripcion_resultado': meta.descripcion_resultado,
        'unidad_medida': meta.unidad_medida,
        'estado': meta.estado,
        'fecha_inicio': meta.fecha_inicio.isoformat() if meta.fecha_inicio else None,
        'fecha_fin': meta.fecha_fin.isoformat() if meta.fecha_fin else None,
        'fecha_registro': meta.fecha_registro.isoformat() if meta.fecha_registro else None,
    }

@meta_bp.route('/', methods=['POST'])
def crear_meta():
    data = request.get_json()
    meta = Meta(**data)
    db.session.add(meta)
    db.session.commit()
    return jsonify({'mensaje': 'Meta creada exitosamente'}), 201

@meta_bp.route('/', methods=['GET'])
def listar_metas():
    metas = Meta.query.all()
    return jsonify([meta_to_dict(m) for m in metas])

@meta_bp.route('/<string:meta_id>', methods=['GET'])
def obtener_meta(meta_id):
    meta = Meta.query.get_or_404(meta_id)
    return jsonify(meta_to_dict(meta))

@meta_bp.route('/<string:meta_id>', methods=['PUT'])
def actualizar_meta(meta_id):
    meta = Meta.query.get_or_404(meta_id)
    data = request.get_json()
    for key, value in data.items():
        setattr(meta, key, value)
    db.session.commit()
    return jsonify({'mensaje': 'Meta actualizada exitosamente'})

@meta_bp.route('/<string:meta_id>', methods=['DELETE'])
def eliminar_meta(meta_id):
    meta = Meta.query.get_or_404(meta_id)
    db.session.delete(meta)
    db.session.commit()
    return jsonify({'mensaje': 'Meta eliminada exitosamente'})