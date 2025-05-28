from flask import Blueprint, request, jsonify, render_template
from app import db 
from app.metas.models import Meta, EstadoMetaEnum 
from app.auditoria.utils import registrar_auditoria, ResultadoAccion
from app.auditoria.decorators import audit_action
from flask_login import current_user 

metas_bp = Blueprint('metas_bp', __name__, url_prefix='/metas') 

def meta_to_dict(meta):
    return {
        'meta_id': meta.meta_id,
        'nombre': meta.nombre,
        'meta_resultado': meta.meta_resultado,
        'descripcion_resultado': meta.descripcion_resultado,
        'unidad_medida': meta.unidad_medida,
        'estado': meta.estado.value if meta.estado else None, 
        'fecha_inicio': meta.fecha_inicio.isoformat() if meta.fecha_inicio else None,
        'fecha_fin': meta.fecha_fin.isoformat() if meta.fecha_fin else None,
        'fecha_registro': meta.fecha_registro.isoformat() if meta.fecha_registro else None,
    }

@metas_bp.route('/', methods=['POST'])
@audit_action(
    accion='CREAR_META',
    entidad_afectada_name='Meta',
    include_args_in_details=['data'], 
    obj_id_attr='meta_id' 
)
def crear_meta():
    data = request.get_json()
    
    # Validación de campos requeridos
    if 'meta_id' not in data:
        return jsonify({'error': 'El campo meta_id es requerido'}), 400
        
    if 'titulo' in data:
        data['nombre'] = data.pop('titulo')
    elif 'nombre' not in data:
        return jsonify({'error': 'Se requiere nombre o titulo para la meta'}), 400
    
    # Manejo del estado
    if 'estado' in data:
        try:
            data['estado'] = EstadoMetaEnum[data['estado'].upper()]
        except KeyError:
            return jsonify({
                'error': f'Estado inválido. Valores permitidos: {", ".join([e.value for e in EstadoMetaEnum])}'
            }), 400
    
    # Filtramos solo los campos válidos del modelo
    campos_permitidos = {
        'meta_id', 'nombre', 'meta_resultado', 'descripcion_resultado',
        'unidad_medida', 'estado', 'fecha_inicio', 'fecha_fin'
    }
    data_filtrada = {k: v for k, v in data.items() if k in campos_permitidos}
    
    try:
        meta = Meta(**data_filtrada)
        db.session.add(meta)
        db.session.commit()
        
        return jsonify({
            'mensaje': 'Meta creada exitosamente',
            'meta': meta_to_dict(meta)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear la meta: ' + str(e)}), 500

@metas_bp.route('/', methods=['GET'])
def listar_metas():
    metas = Meta.query.all()
    return jsonify([meta_to_dict(m) for m in metas])

@metas_bp.route('/<string:meta_id>', methods=['GET'])
def obtener_meta(meta_id):
    meta = Meta.query.get_or_404(meta_id)
    return jsonify(meta_to_dict(meta))

@metas_bp.route('/<string:meta_id>', methods=['PUT'])
@audit_action(
    accion='ACTUALIZAR_META',
    entidad_afectada_name='Meta',
    id_param_name='meta_id', 
    include_args_in_details=['data'] 
)
def actualizar_meta(meta_id):
    meta = Meta.query.get_or_404(meta_id)
    data = request.get_json()
    for key, value in data.items():
        if key == 'estado' and value:
            try:
                setattr(meta, key, EstadoMetaEnum[value.upper()]) 
            except KeyError:
                return jsonify({'error': f'Estado inválido para {key}: {value}. Valores permitidos: {", ".join([e.value for e in EstadoMetaEnum])}.'}), 400
        else:
            setattr(meta, key, value)
    db.session.commit()
    return jsonify({'mensaje': 'Meta actualizada exitosamente'})

@metas_bp.route('/<string:meta_id>', methods=['DELETE'])
@audit_action(
    accion='ELIMINAR_META',
    entidad_afectada_name='Meta',
    id_param_name='meta_id', 
    include_obj_attrs_in_details=['nombre', 'estado'] 
)
def eliminar_meta(meta_id):
    meta = Meta.query.get_or_404(meta_id)
    db.session.delete(meta)
    db.session.commit()
    return jsonify({'mensaje': 'Meta eliminada exitosamente'})

@metas_bp.route('/')
def metas():
    return render_template('metas/metas.html')