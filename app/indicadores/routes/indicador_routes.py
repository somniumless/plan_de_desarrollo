from flask import Blueprint, request, jsonify
from app import db
from indicadores.models import MetaIndicador

# Definición del blueprint para meta indicadores
meta_indicador_bp = Blueprint('meta_indicador_bp', __name__)

# Función para convertir MetaIndicador a diccionario JSON serializable
def meta_indicador_to_dict(meta):
    return {
        'meta_id': meta.meta_id,
        'indicador_id': meta.indicador_id,
        'valor_actual': float(meta.valor_actual) if meta.valor_actual is not None else None,
        'meta': float(meta.meta) if meta.meta is not None else None,
        'fecha_calculo': meta.fecha_calculo.isoformat() if meta.fecha_calculo else None,
        'calculado_por': meta.calculado_por
    }

@meta_indicador_bp.route('/meta_indicadores', methods=['POST'])
def crear_meta_indicador():
    data = request.get_json()
    nuevo = MetaIndicador(**data)
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({'mensaje': 'MetaIndicador creado exitosamente'}), 201

@meta_indicador_bp.route('/meta_indicadores', methods=['GET'])
def obtener_meta_indicadores():
    metas = MetaIndicador.query.all()
    return jsonify([meta_indicador_to_dict(m) for m in metas])

@meta_indicador_bp.route('/meta_indicadores/<string:meta_id>/<string:indicador_id>', methods=['GET'])
def obtener_meta_indicador(meta_id, indicador_id):
    meta = MetaIndicador.query.get_or_404((meta_id, indicador_id))
    return jsonify(meta_indicador_to_dict(meta))

@meta_indicador_bp.route('/meta_indicadores/<string:meta_id>/<string:indicador_id>', methods=['PUT'])
def actualizar_meta_indicador(meta_id, indicador_id):
    meta = MetaIndicador.query.get_or_404((meta_id, indicador_id))
    data = request.get_json()
    for key, value in data.items():
        setattr(meta, key, value)
    db.session.commit()
    return jsonify({'mensaje': 'MetaIndicador actualizado exitosamente'})

@meta_indicador_bp.route('/meta_indicadores/<string:meta_id>/<string:indicador_id>', methods=['DELETE'])
def eliminar_meta_indicador(meta_id, indicador_id):
    meta = MetaIndicador.query.get_or_404((meta_id, indicador_id))
    db.session.delete(meta)
    db.session.commit()
    return jsonify({'mensaje': 'MetaIndicador eliminado exitosamente'})
