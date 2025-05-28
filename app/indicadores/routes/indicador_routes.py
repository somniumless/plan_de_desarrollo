from flask import Blueprint, request, jsonify
from app import db 
from app.indicadores.models import Indicador, FrecuenciaCalculo 
from app.auditoria.utils import registrar_auditoria, ResultadoAccion
from app.auditoria.decorators import audit_action
from flask_login import current_user 
from datetime import datetime 

indicador_bp = Blueprint('indicador_bp', __name__, url_prefix='/indicadores') 

def indicador_to_dict(indicador):
    return {
        'indicador_id': indicador.indicador_id,
        'nombre': indicador.nombre,
        'formula': indicador.formula,
        'descripcion': indicador.descripcion,
        'unidad_medida': indicador.unidad_medida,
        'frecuencia_calculo': indicador.frecuencia_calculo.value if indicador.frecuencia_calculo else None, # Accede al valor del Enum
        'es_critico': indicador.es_critico,
        'fecha_creacion': indicador.fecha_creacion.isoformat() if indicador.fecha_creacion else None,
    }

@indicador_bp.route('/', methods=['POST']) 
@audit_action(
    accion='CREAR_INDICADOR',
    entidad_afectada_name='Indicador',
    include_args_in_details=['data'], 
    obj_id_attr='indicador_id' 
)
def crear_indicador():
    data = request.get_json()
    
    frecuencia_str = data.get('frecuencia_calculo')
    if frecuencia_str:
        try:
            data['frecuencia_calculo'] = FrecuenciaCalculo[frecuencia_str.upper()]
        except KeyError:
            return jsonify({'error': f'Frecuencia de cálculo inválida: {frecuencia_str}. Valores permitidos: {", ".join([e.value for e in FrecuenciaCalculo])}.'}), 400

    nuevo = Indicador(**data)
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({'mensaje': 'Indicador creado exitosamente', 'indicador_id': nuevo.indicador_id}), 201

@indicador_bp.route('/', methods=['GET']) 
def obtener_indicadores():
    indicadores = Indicador.query.all()
    return jsonify([indicador_to_dict(i) for i in indicadores])

@indicador_bp.route('/<string:indicador_id>', methods=['GET'])
def obtener_indicador(indicador_id):
    indicador = Indicador.query.get_or_404(indicador_id)
    return jsonify(indicador_to_dict(indicador))

@indicador_bp.route('/<string:indicador_id>', methods=['PUT'])
@audit_action(
    accion='ACTUALIZAR_INDICADOR',
    entidad_afectada_name='Indicador',
    id_param_name='indicador_id', 
    include_args_in_details=['data']
)
def actualizar_indicador(indicador_id):
    indicador = Indicador.query.get_or_404(indicador_id)
    data = request.get_json()
    for key, value in data.items():
        if key == 'frecuencia_calculo' and value is not None:
            try:
                setattr(indicador, key, FrecuenciaCalculo[value.upper()])
            except KeyError:
                return jsonify({'error': f'Frecuencia de cálculo inválida para {key}: {value}. Valores permitidos: {", ".join([e.value for e in FrecuenciaCalculo])}.'}), 400
        else:
            setattr(indicador, key, value)
    db.session.commit()
    return jsonify({'mensaje': 'Indicador actualizado exitosamente'})

@indicador_bp.route('/<string:indicador_id>', methods=['DELETE'])
@audit_action(
    accion='ELIMINAR_INDICADOR',
    entidad_afectada_name='Indicador',
    id_param_name='indicador_id', 
    include_obj_attrs_in_details=['nombre', 'unidad_medida'] 
)
def eliminar_indicador(indicador_id):
    indicador = Indicador.query.get_or_404(indicador_id)
    db.session.delete(indicador)
    db.session.commit()
    return jsonify({'mensaje': 'Indicador eliminado exitosamente'})