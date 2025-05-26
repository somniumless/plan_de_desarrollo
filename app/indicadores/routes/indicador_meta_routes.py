from flask import Blueprint, request, jsonify
from app import db
from models import Indicador

indicador_bp = Blueprint('indicador_bp', __name__)

# Función para convertir Indicador a dict
def indicador_to_dict(indicador):
    return {
        'indicador_id': indicador.indicador_id,
        'nombre': indicador.nombre,
        'formula': indicador.formula,
        'descripcion': indicador.descripcion,
        'unidad_medida': indicador.unidad_medida,
        'frecuencia_calculo': indicador.frecuencia_calculo.name if indicador.frecuencia_calculo else None,
        'es_critico': indicador.es_critico,
        'fecha_creacion': indicador.fecha_creacion.isoformat() if indicador.fecha_creacion else None,
    }

# Función para convertir MetaIndicador a dict
def meta_indicador_to_dict(meta_indicador):
    return {
        'meta_id': meta_indicador.meta_id,
        'indicador_id': meta_indicador.indicador_id,
        'valor_actual': float(meta_indicador.valor_actual) if meta_indicador.valor_actual is not None else None,
        'meta': float(meta_indicador.meta) if meta_indicador.meta is not None else None,
        'fecha_calculo': meta_indicador.fecha_calculo.isoformat() if meta_indicador.fecha_calculo else None,
        'calculado_por': meta_indicador.calculado_por,
    }

# CRUD para Indicador

@indicador_bp.route('/indicadores', methods=['POST'])
def crear_indicador():
    data = request.get_json()
    nuevo = Indicador(**data)
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({'mensaje': 'Indicador creado exitosamente'}), 201

@indicador_bp.route('/indicadores', methods=['GET'])
def obtener_indicadores():
    indicadores = Indicador.query.all()
    return jsonify([indicador_to_dict(i) for i in indicadores])

@indicador_bp.route('/indicadores/<string:indicador_id>', methods=['GET'])
def obtener_indicador(indicador_id):
    indicador = Indicador.query.get_or_404(indicador_id)
    return jsonify(indicador_to_dict(indicador))

@indicador_bp.route('/indicadores/<string:indicador_id>', methods=['PUT'])
def actualizar_indicador(indicador_id):
    indicador = Indicador.query.get_or_404(indicador_id)
    data = request.get_json()
    for key, value in data.items():
        if key == 'frecuencia_calculo' and value is not None:
            from models import FrecuenciaCalculo
            setattr(indicador, key, FrecuenciaCalculo[value])
        else:
            setattr(indicador, key, value)
    db.session.commit()
    return jsonify({'mensaje': 'Indicador actualizado exitosamente'})

@indicador_bp.route('/indicadores/<string:indicador_id>', methods=['DELETE'])
def eliminar_indicador(indicador_id):
    indicador = Indicador.query.get_or_404(indicador_id)
    db.session.delete(indicador)
    db.session.commit()
    return jsonify({'mensaje': 'Indicador eliminado exitosamente'})