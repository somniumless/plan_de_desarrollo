# app/metas/metas_routes.py

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
        'estado': meta.estado.value, 
        'fecha_inicio': meta.fecha_inicio.isoformat() if meta.fecha_inicio else None,
        'fecha_fin': meta.fecha_fin.isoformat() if meta.fecha_fin else None,
        'fecha_registro': meta.fecha_registro.isoformat() if meta.fecha_registro else None,
    }

@metas_bp.route('/gestion', methods=['GET']) 
@login_required
def gestion_metas_page():
    from datetime import datetime
    return render_template('metas/gestion_metas.html', 
                            title='Gestión Integral de Metas', 
                            EstadoMetaEnum=EstadoMetaEnum,
                            current_timestamp=datetime.utcnow().timestamp())


@metas_bp.route('/crear', methods=['POST']) 
@audit_action(
    accion='CREAR_META_API',
    entidad_afectada_name='Meta',
    include_args_in_details=['data'],
    obj_id_attr='meta_id'
)
def crear_meta_api():
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

    if 'resultado_esperado' in data and 'meta_resultado' not in data:
        data['meta_resultado'] = data.pop('resultado_esperado')

    if 'estado' in data and data['estado']:
        estado_input = data['estado'].strip().lower().replace('_', ' ').replace('-', ' ')
        estado_match = None
        for e in EstadoMetaEnum:
            if e.value.strip().lower() == estado_input or e.name.strip().lower().replace('_', ' ') == estado_input:
                estado_match = e
                break
        if estado_match:
            data['estado'] = estado_match
        else:
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

    from datetime import datetime
    if 'fecha_registro' not in data_filtrada:
        data_filtrada['fecha_registro'] = datetime.utcnow()

    estado_para_db = data['estado']
    if isinstance(estado_para_db, str):
        estado_para_db = EstadoMetaEnum([e for e in EstadoMetaEnum if e.value == estado_para_db][0])
    data_filtrada['estado'] = estado_para_db

    print("DEBUG: data_filtrada antes de crear Meta:", data_filtrada)

    try:
        if Meta.query.get(data_filtrada['meta_id']):
            return jsonify({'error': f"Ya existe una meta con ID '{data_filtrada['meta_id']}'."}), 409

        meta = Meta(**data_filtrada)
        db.session.add(meta)
        print("DEBUG: Meta añadida a la sesión.") 
        db.session.commit()
        print("DEBUG: Commit exitoso. Meta guardada en DB.") 

        flash(f'Meta \"{meta.nombre}\" creada exitosamente.', 'success')

        return jsonify({
            'mensaje': 'Meta creada exitosamente',
            'meta': meta_to_dict(meta)
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback; traceback.print_exc()
        print(f"ERROR al crear la meta: {e}") 
        return jsonify({'error': 'Error al crear la meta: ' + str(e)}), 500

@metas_bp.route('/', methods=['GET']) 
def listar_metas():
    metas = Meta.query.all()
    print("DEBUG: Metas encontradas:", metas)
    result = [meta_to_dict(m) for m in metas]
    print("DEBUG: Resultado serializado:", result)
    return jsonify(result)

@metas_bp.route('/<string:meta_id>', methods=['GET']) 
def obtener_meta(meta_id):
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
                estado_input = value.strip().lower().replace('_', ' ').replace('-', ' ')
                found_state = None
                for e in EstadoMetaEnum:
                    if e.value.strip().lower() == estado_input or e.name.strip().lower().replace('_', ' ') == estado_input:
                        found_state = e
                        break
                if found_state:
                    setattr(meta, key, found_state)
                else:
                    valid_states = [e.value for e in EstadoMetaEnum]
                    return jsonify({'error': f'Estado inválido para {key}: {value}. Valores permitidos: {", ".join(valid_states)}.'}), 400
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