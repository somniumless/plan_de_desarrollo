# app/metas/routes.py

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from app import db
from app.metas.models import Meta, EstadoMetaEnum
from app.auditoria.utils import registrar_auditoria, ResultadoAccion
from app.auditoria.decorators import audit_action
from flask_login import current_user, login_required
from datetime import datetime

metas_bp = Blueprint('metas_bp', __name__, url_prefix='/api/metas', template_folder='../../templates')

def meta_to_dict(meta):
    """Convierte un objeto Meta a un diccionario para respuestas JSON."""
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

@metas_bp.route('/gestion', methods=['GET']) 
@login_required
def gestion_metas_page():
    """Renderiza la página principal de gestión de metas con la tabla y el formulario JS."""
    from datetime import datetime
    return render_template('metas/gestion_metas.html', 
                           title='Gestión Integral de Metas', 
                           EstadoMetaEnum=EstadoMetaEnum,
                           current_timestamp=datetime.utcnow().timestamp())


@metas_bp.route('/', methods=['POST']) 
@audit_action(
    accion='CREAR_META_API',
    entidad_afectada_name='Meta',
    include_args_in_details=['data'],
    obj_id_attr='meta_id'
)
def crear_meta_api():
    """API para crear una nueva meta. Espera datos JSON del cliente (JS)."""
    data = request.get_json()
    print(f"DEBUG: Datos recibidos para POST: {data}") 

    if not data:
        return jsonify({'error': 'No se proporcionaron datos JSON válidos'}), 400

    if 'meta_id' not in data or not data['meta_id']:
        return jsonify({'error': 'El campo meta_id es requerido y no puede estar vacío para crear una meta.'}), 400
    if 'titulo' in data:
        data['nombre'] = data.pop('titulo')
    elif 'nombre' not in data or not data['nombre']:
        return jsonify({'error': 'Se requiere nombre para la meta'}), 400

    if 'estado' in data and data['estado']:
        try:
            data['estado'] = EstadoMetaEnum[data['estado'].upper().replace(' ', '_')]
        except KeyError:
            valid_states = [e.value for e in EstadoMetaEnum]
            return jsonify({
                'error': f'Estado inválido. Valores permitidos: {", ".join(valid_states)}'
            }), 400
    elif 'estado' not in data or not data['estado']:
        data['estado'] = EstadoMetaEnum.PENDIENTE

    campos_permitidos = {
        'meta_id', 'nombre', 'meta_resultado', 'descripcion_resultado',
        'unidad_medida', 'estado', 'fecha_inicio', 'fecha_fin'
    }
    data_filtrada = {k: v for k, v in data.items() if k in campos_permitidos}

    for date_field in ['fecha_inicio', 'fecha_fin']:
        if date_field in data_filtrada and data_filtrada[date_field]:
            try:
                data_filtrada[date_field] = datetime.strptime(data_filtrada[date_field], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': f'Formato de fecha inválido para {date_field}. Use YYYY-MM-DD.'}), 400

    try:
        if Meta.query.get(data_filtrada['meta_id']):
            return jsonify({'error': f"Ya existe una meta con ID '{data_filtrada['meta_id']}'."}), 409

        meta = Meta(**data_filtrada)
        db.session.add(meta)
        print("DEBUG: Meta añadida a la sesión.") 
        db.session.commit()
        print("DEBUG: Commit exitoso. Meta guardada en DB.") 

        flash(f'Meta "{meta.nombre}" creada exitosamente.', 'success')

        return jsonify({
            'mensaje': 'Meta creada exitosamente',
            'meta': meta_to_dict(meta)
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"ERROR al crear la meta: {e}") 
        return jsonify({'error': 'Error al crear la meta: ' + str(e)}), 500

@metas_bp.route('/', methods=['GET']) 
def listar_metas():
    """API para listar todas las metas. Devuelve JSON."""
    metas = Meta.query.all()
    return jsonify([meta_to_dict(m) for m in metas])

@metas_bp.route('/<string:meta_id>', methods=['GET']) 
def obtener_meta(meta_id):
    """API para obtener una meta específica por ID. Devuelve JSON."""
    meta = db.session.get(Meta, meta_id)
    if not meta:
        return jsonify({'error': 'Meta no encontrada'}), 404
    return jsonify(meta_to_dict(meta))

@metas_bp.route('/<string:meta_id>', methods=['PUT']) 
@audit_action(
    accion='ACTUALIZAR_META',
    entidad_afectada_name='Meta',
    id_param_name='meta_id',
    include_args_in_details=['data']
)
def actualizar_meta(meta_id):
    """API para actualizar una meta existente. Espera JSON del cliente (JS)."""
    data = request.get_json()
    print(f"DEBUG: Datos recibidos para PUT de {meta_id}: {data}") 
    
    meta = db.session.get(Meta, meta_id)
    print(f"DEBUG: Meta encontrada para actualizar: {meta}") 
    
    if not meta:
        return jsonify({'error': 'Meta no encontrada'}), 404

    if not data:
        return jsonify({'error': 'No se proporcionaron datos JSON válidos para actualizar'}), 400

    for key, value in data.items():
        if key == 'estado' and value:
            try:
                setattr(meta, key, EstadoMetaEnum[value.upper().replace(' ', '_')])
            except KeyError:
                valid_states = [e.value for e in EstadoMetaEnum]
                return jsonify({'error': f'Estado inválido para {key}: {value}. Valores permitidos: {", ".join(valid_states)}.'}), 400
        elif key in ['fecha_inicio', 'fecha_fin'] and value:
            try:
                setattr(meta, key, datetime.strptime(value, '%Y-%m-%d').date())
            except ValueError:
                return jsonify({'error': f'Formato de fecha inválido para {key}. Use YYYY-MM-DD.'}), 400
        elif hasattr(meta, key):
            if key != 'meta_id':
                setattr(meta, key, value)

    try:
        db.session.commit()
        print("DEBUG: Commit de actualización exitoso.") 
        flash(f'Meta "{meta.nombre}" actualizada exitosamente.', 'success')
        return jsonify({'mensaje': 'Meta actualizada exitosamente', 'meta': meta_to_dict(meta)})
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar la meta: {e}") 
        return jsonify({'error': 'Error al actualizar la meta: ' + str(e)}), 500


@metas_bp.route('/<string:meta_id>', methods=['DELETE']) 
@audit_action(
    accion='ELIMINAR_META',
    entidad_afectada_name='Meta',
    id_param_name='meta_id',
    include_obj_attrs_in_details=['nombre', 'estado']
)
def eliminar_meta(meta_id):
    """API para eliminar una meta. """
    meta = db.session.get(Meta, meta_id)
    if not meta:
        return jsonify({'error': 'Meta no encontrada'}), 404

    try:
        db.session.delete(meta)
        db.session.commit()
        flash(f'Meta "{meta.nombre}" eliminada exitosamente.', 'success')
        return jsonify({'mensaje': 'Meta eliminada exitosamente'})
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar la meta: {e}") 
        return jsonify({'error': 'Error al eliminar la meta: ' + str(e)}), 500