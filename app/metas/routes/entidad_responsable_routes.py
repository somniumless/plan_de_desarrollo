# entidades/routes/entidad_responsable_routes.py
from flask import Blueprint, request, jsonify
from app import db
from metas.models import EntidadResponsable, TipoEntidad

entidad_bp = Blueprint('entidad_responsable', __name__, url_prefix='/entidades')

def entidad_to_dict(entidad):
    return {
        'entidad_id': entidad.entidad_id,
        'nombre': entidad.nombre,
        'tipo_entidad': entidad.tipo_entidad.value if entidad.tipo_entidad else None,
    }

@entidad_bp.route('/', methods=['POST'])
def crear_entidad():
    data = request.get_json()
    # Asegúrate de validar o transformar tipo_entidad a enum
    tipo = data.get('tipo_entidad')
    if tipo not in TipoEntidad._member_names_:
        return jsonify({'error': 'Tipo de entidad inválido'}), 400
    data['tipo_entidad'] = TipoEntidad[tipo]
    entidad = EntidadResponsable(**data)
    db.session.add(entidad)
    db.session.commit()
    return jsonify({'mensaje': 'Entidad responsable creada exitosamente'}), 201

@entidad_bp.route('/', methods=['GET'])
def listar_entidades():
    entidades = EntidadResponsable.query.all()
    return jsonify([entidad_to_dict(e) for e in entidades])

@entidad_bp.route('/<string:entidad_id>', methods=['GET'])
def obtener_entidad(entidad_id):
    entidad = EntidadResponsable.query.get_or_404(entidad_id)
    return jsonify(entidad_to_dict(entidad))

@entidad_bp.route('/<string:entidad_id>', methods=['PUT'])
def actualizar_entidad(entidad_id):
    entidad = EntidadResponsable.query.get_or_404(entidad_id)
    data = request.get_json()
    if 'tipo_entidad' in data:
        tipo = data['tipo_entidad']
        if tipo not in TipoEntidad._member_names_:
            return jsonify({'error': 'Tipo de entidad inválido'}), 400
        data['tipo_entidad'] = TipoEntidad[tipo]
    for key, value in data.items():
        setattr(entidad, key, value)
    db.session.commit()
    return jsonify({'mensaje': 'Entidad responsable actualizada exitosamente'})

@entidad_bp.route('/<string:entidad_id>', methods=['DELETE'])
def eliminar_entidad(entidad_id):
    entidad = EntidadResponsable.query.get_or_404(entidad_id)
    db.session.delete(entidad)
    db.session.commit()
    return jsonify({'mensaje': 'Entidad responsable eliminada exitosamente'})
