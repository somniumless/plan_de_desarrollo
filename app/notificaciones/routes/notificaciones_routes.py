# app/notificaciones/routes/notificaciones_routes.py

from flask import Blueprint, request, jsonify
from app import db
from app.notificaciones.models import Notificacion, TipoNotificacion, PrioridadNotificacion
from app.auth.models import Usuario 
from app.auditoria.utils import registrar_auditoria, ResultadoAccion
from app.auditoria.decorators import audit_action
from flask_login import current_user 
from datetime import datetime

notificaciones_bp = Blueprint('notificaciones_bp', __name__, url_prefix='/notificaciones')

def notificacion_to_dict(n):
    return {
        'notificacion_id': n.notificacion_id,
        'usuario_id': n.usuario_id,
        'tipo': n.tipo.value if n.tipo else None,
        'titulo': n.titulo,
        'mensaje': n.mensaje,
        'fecha_envio': n.fecha_envio.isoformat() if n.fecha_envio else None,
        'fecha_lectura': n.fecha_lectura.isoformat() if n.fecha_lectura else None,
        'leida': n.leida,
        'url_accion': n.url_accion,
        'prioridad': n.prioridad.value if n.prioridad else None
    }

@notificaciones_bp.route('/', methods=['GET'])
def listar_notificaciones():
    notificaciones = Notificacion.query.all()
    return jsonify([notificacion_to_dict(n) for n in notificaciones])

@notificaciones_bp.route('/<int:notificacion_id>', methods=['GET'])
def obtener_notificacion(notificacion_id):
    notificacion = Notificacion.query.get_or_404(notificacion_id)
    return jsonify(notificacion_to_dict(notificacion))

@notificaciones_bp.route('/', methods=['POST'])
@audit_action(
    accion='CREAR_NOTIFICACION',
    entidad_afectada_name='Notificacion',
    include_args_in_details=['data'],
    obj_id_attr='notificacion_id'
)
def crear_notificacion():
    data = request.get_json()
    try:
        tipo_str = data.get('tipo')
        if not tipo_str:
            return jsonify({'error': 'El campo "tipo" es obligatorio.'}), 400
        try:
            tipo_enum = TipoNotificacion[tipo_str.upper()]
        except KeyError:
            return jsonify({'error': f'Tipo de notificación inválido: {tipo_str}. Valores permitidos: {", ".join([e.value for e in TipoNotificacion])}.'}), 400

        prioridad_str = data.get('prioridad', 'MEDIA') 
        try:
            prioridad_enum = PrioridadNotificacion[prioridad_str.upper()]
        except KeyError:
            return jsonify({'error': f'Prioridad de notificación inválida: {prioridad_str}. Valores permitidos: {", ".join([e.value for e in PrioridadNotificacion])}.'}), 400

        if 'usuario_id' in data and not Usuario.query.get(data['usuario_id']):
            return jsonify({'error': 'El usuario_id proporcionado no existe.'}), 400

        if 'usuario_id' not in data and current_user.is_authenticated:
            data['usuario_id'] = current_user.usuario_id
        elif 'usuario_id' not in data:
             return jsonify({'error': 'El campo "usuario_id" es obligatorio si no hay usuario autenticado.'}), 400

        fecha_envio = None
        if 'fecha_envio' in data and data['fecha_envio']:
            try:
                fecha_envio = datetime.fromisoformat(data['fecha_envio'])
            except ValueError:
                return jsonify({'error': 'Formato de fecha_envio inválido. Use ISO 8601.'}), 400
        
        fecha_lectura = None
        if 'fecha_lectura' in data and data['fecha_lectura']:
            try:
                fecha_lectura = datetime.fromisoformat(data['fecha_lectura'])
            except ValueError:
                return jsonify({'error': 'Formato de fecha_lectura inválido. Use ISO 8601.'}), 400

        notificacion = Notificacion(
            usuario_id=data['usuario_id'],
            tipo=tipo_enum,
            titulo=data['titulo'],
            mensaje=data['mensaje'],
            fecha_envio=fecha_envio, 
            fecha_lectura=fecha_lectura,
            leida=data.get('leida', False), 
            url_accion=data.get('url_accion'),
            prioridad=prioridad_enum
        )

        db.session.add(notificacion)
        db.session.commit()

        return jsonify({'mensaje': 'Notificación creada', 'data': notificacion_to_dict(notificacion)}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@notificaciones_bp.route('/<int:notificacion_id>', methods=['PUT'])
@audit_action(
    accion='ACTUALIZAR_NOTIFICACION',
    entidad_afectada_name='Notificacion',
    id_param_name='notificacion_id',
    include_args_in_details=['data']
)
def actualizar_notificacion(notificacion_id):
    notificacion = Notificacion.query.get_or_404(notificacion_id)
    data = request.get_json()
    try:
        if 'titulo' in data:
            notificacion.titulo = data['titulo']
        if 'mensaje' in data:
            notificacion.mensaje = data['mensaje']
        if 'leida' in data:
            notificacion.leida = data['leida']
            if notificacion.leida and not notificacion.fecha_lectura: 
                notificacion.fecha_lectura = datetime.utcnow()
            elif not notificacion.leida: 
                notificacion.fecha_lectura = None
        if 'url_accion' in data:
            notificacion.url_accion = data['url_accion']
        
        if 'prioridad' in data:
            try:
                notificacion.prioridad = PrioridadNotificacion[data['prioridad'].upper()]
            except KeyError:
                return jsonify({'error': f'Prioridad de notificación inválida: {data["prioridad"]}. Valores permitidos: {", ".join([e.value for e in PrioridadNotificacion])}.'}), 400

        if 'fecha_lectura' in data and data['fecha_lectura']: 
            try:
                notificacion.fecha_lectura = datetime.fromisoformat(data['fecha_lectura'])
            except ValueError:
                return jsonify({'error': 'Formato de fecha_lectura inválido. Use ISO 8601.'}), 400
        elif 'fecha_lectura' in data and not data['fecha_lectura']: 
            notificacion.fecha_lectura = None

        db.session.commit()
        return jsonify({'mensaje': 'Notificación actualizada', 'data': notificacion_to_dict(notificacion)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@notificaciones_bp.route('/<int:notificacion_id>', methods=['DELETE'])
@audit_action(
    accion='ELIMINAR_NOTIFICACION',
    entidad_afectada_name='Notificacion',
    id_param_name='notificacion_id',
    include_obj_attrs_in_details=['titulo', 'usuario_id', 'tipo']
)
def eliminar_notificacion(notificacion_id):
    notificacion = Notificacion.query.get_or_404(notificacion_id)
    try:
        db.session.delete(notificacion)
        db.session.commit()
        return jsonify({'mensaje': 'Notificación eliminada'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400