# app/indicadores/routes/indicador_meta_routes.py

from flask import Blueprint, request, jsonify
from app import db 
from app.indicadores.models import Indicador, MetaIndicador
from app.metas.models import Meta 
from app.auth.models import Usuario 
from app.auditoria.utils import registrar_auditoria, ResultadoAccion
from app.auditoria.decorators import audit_action
from flask_login import current_user 
from datetime import datetime 

meta_indicador_bp = Blueprint('meta_indicador_bp', __name__, url_prefix='/meta_indicadores')

def meta_indicador_to_dict(mi):
    return {
        'meta_id': mi.meta_id,
        'indicador_id': mi.indicador_id,
        'valor_actual': float(mi.valor_actual) if mi.valor_actual is not None else None,
        'meta': float(mi.meta) if mi.meta is not None else None,
        'fecha_calculo': mi.fecha_calculo.isoformat() if mi.fecha_calculo else None,
        'calculado_por': mi.calculado_por,
    }

@meta_indicador_bp.route('/', methods=['POST'])
@audit_action(
    accion='CREAR_META_INDICADOR',
    entidad_afectada_name='MetaIndicador',
    include_args_in_details=['data'], 
    obj_id_attr=None 
)
def crear_meta_indicador():
    data = request.get_json()
    meta_id = data.get('meta_id')
    indicador_id = data.get('indicador_id')

    if not meta_id or not indicador_id:
        return jsonify({'error': 'meta_id e indicador_id son obligatorios'}), 400

    if not Meta.query.get(meta_id):
        return jsonify({'error': f'Meta con ID {meta_id} no encontrada.'}), 404
    if not Indicador.query.get(indicador_id):
        return jsonify({'error': f'Indicador con ID {indicador_id} no encontrado.'}), 404

    if 'calculado_por' not in data and current_user.is_authenticated:
        data['calculado_por'] = current_user.usuario_id
    
    if 'fecha_calculo' in data and isinstance(data['fecha_calculo'], str):
        try:
            data['fecha_calculo'] = datetime.fromisoformat(data['fecha_calculo'])
        except ValueError:
            return jsonify({'error': 'Formato de fecha_calculo inválido. Use ISO 8601.'}), 400
    
    for key in ['valor_actual', 'meta']:
        if key in data and isinstance(data[key], str):
            try:
                data[key] = float(data[key])
            except ValueError:
                return jsonify({'error': f'{key} debe ser un número válido.'}), 400

    mi = MetaIndicador(**data)
    db.session.add(mi)
    db.session.commit()
    return jsonify({'mensaje': 'Asociación Meta-Indicador creada exitosamente', 'data': meta_indicador_to_dict(mi)}), 201

@meta_indicador_bp.route('/', methods=['GET'])
def listar_meta_indicadores():
    relaciones = MetaIndicador.query.all()
    return jsonify([meta_indicador_to_dict(r) for r in relaciones])

@meta_indicador_bp.route('/<string:meta_id>/<string:indicador_id>', methods=['GET'])
def obtener_meta_indicador(meta_id, indicador_id):
    mi = MetaIndicador.query.get_or_404((meta_id, indicador_id))
    return jsonify(meta_indicador_to_dict(mi))

@meta_indicador_bp.route('/<string:meta_id>/<string:indicador_id>', methods=['PUT'])
@audit_action(
    accion='ACTUALIZAR_META_INDICADOR',
    entidad_afectada_name='MetaIndicador',
    id_param_name='meta_id', 
    include_args_in_details=['indicador_id', 'data'] 
)
def actualizar_meta_indicador(meta_id, indicador_id):
    mi = MetaIndicador.query.get_or_404((meta_id, indicador_id))
    data = request.get_json()

    if 'fecha_calculo' in data and isinstance(data['fecha_calculo'], str):
        try:
            data['fecha_calculo'] = datetime.fromisoformat(data['fecha_calculo'])
        except ValueError:
            return jsonify({'error': 'Formato de fecha_calculo inválido. Use ISO 8601.'}), 400
    
    for key, value in data.items():
        if key in ['valor_actual', 'meta'] and isinstance(value, str):
            try:
                setattr(mi, key, float(value))
            except ValueError:
                return jsonify({'error': f'{key} debe ser un número válido.'}), 400
        else:
            setattr(mi, key, value)
    
    db.session.commit()
    return jsonify({'mensaje': 'Asociación Meta-Indicador actualizada exitosamente'})

@meta_indicador_bp.route('/<string:meta_id>/<string:indicador_id>', methods=['DELETE'])
@audit_action(
    accion='ELIMINAR_META_INDICADOR',
    entidad_afectada_name='MetaIndicador',
    id_param_name='meta_id', 
    include_args_in_details=['indicador_id'] 
)
def eliminar_meta_indicador(meta_id, indicador_id):
    mi = MetaIndicador.query.get_or_404((meta_id, indicador_id))
    db.session.delete(mi)
    db.session.commit()
    return jsonify({'mensaje': 'Asociación Meta-Indicador eliminada exitosamente'})