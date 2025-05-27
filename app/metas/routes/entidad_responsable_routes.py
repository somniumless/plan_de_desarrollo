# app/metas/routes/entidad_responsable_routes.py

from flask import Blueprint, request, jsonify
from app import db 
from app.metas.models import EntidadResponsable, TipoEntidad 
from app.auditoria.utils import registrar_auditoria, ResultadoAccion
from app.auditoria.decorators import audit_action
from flask_login import current_user 

entidades_bp = Blueprint('entidades_bp', __name__, url_prefix='/entidades') 

def entidad_to_dict(entidad):
    return {
        'entidad_id': entidad.entidad_id,
        'nombre': entidad.nombre,
        'tipo_entidad': entidad.tipo_entidad.value if entidad.tipo_entidad else None,
    }

@entidades_bp.route('/', methods=['POST'])
@audit_action(
    accion='CREAR_ENTIDAD_RESPONSABLE',
    entidad_afectada_name='EntidadResponsable',
    include_args_in_details=['data'], 
    obj_id_attr='entidad_id' 
)
def crear_entidad():
    data = request.get_json()
    
    tipo_str = data.get('tipo_entidad')
    if not tipo_str:
        return jsonify({'error': 'El tipo de entidad es obligatorio.'}), 400
    try:
        data['tipo_entidad'] = TipoEntidad[tipo_str.upper()] 
    except KeyError:
        return jsonify({'error': f'Tipo de entidad inválido: {tipo_str}. Valores permitidos: {", ".join([e.value for e in TipoEntidad])}.'}), 400
    
    entidad = EntidadResponsable(**data)
    db.session.add(entidad)
    db.session.commit()
    return jsonify({'mensaje': 'Entidad responsable creada exitosamente', 'entidad_id': entidad.entidad_id}), 201

@entidades_bp.route('/', methods=['GET'])
def listar_entidades():
    entidades = EntidadResponsable.query.all()
    return jsonify([entidad_to_dict(e) for e in entidades])

@entidades_bp.route('/<string:entidad_id>', methods=['GET'])
def obtener_entidad(entidad_id):
    entidad = EntidadResponsable.query.get_or_404(entidad_id)
    return jsonify(entidad_to_dict(entidad))

@entidades_bp.route('/<string:entidad_id>', methods=['PUT'])
@audit_action(
    accion='ACTUALIZAR_ENTIDAD_RESPONSABLE',
    entidad_afectada_name='EntidadResponsable',
    id_param_name='entidad_id', 
    include_args_in_details=['data'] 
)
def actualizar_entidad(entidad_id):
    entidad = EntidadResponsable.query.get_or_404(entidad_id)
    data = request.get_json()
    for key, value in data.items():
        if key == 'tipo_entidad' and value:
            try:
                setattr(entidad, key, TipoEntidad[value.upper()]) 
            except KeyError:
                return jsonify({'error': f'Tipo de entidad inválido para {key}: {value}. Valores permitidos: {", ".join([e.value for e in TipoEntidad])}.'}), 400
        else:
            setattr(entidad, key, value)
    db.session.commit()
    return jsonify({'mensaje': 'Entidad responsable actualizada exitosamente'})

@entidades_bp.route('/<string:entidad_id>', methods=['DELETE'])
@audit_action(
    accion='ELIMINAR_ENTIDAD_RESPONSABLE',
    entidad_afectada_name='EntidadResponsable',
    id_param_name='entidad_id', 
    include_obj_attrs_in_details=['nombre', 'tipo_entidad'] 
)
def eliminar_entidad(entidad_id):
    entidad = EntidadResponsable.query.get_or_404(entidad_id)
    db.session.delete(entidad)
    db.session.commit()
    return jsonify({'mensaje': 'Entidad responsable eliminada exitosamente'})