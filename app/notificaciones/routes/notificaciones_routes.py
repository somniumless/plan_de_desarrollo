from flask import Blueprint, request, jsonify
from app import db
from notificaciones.models import Notificacion, TipoNotificacion, PrioridadNotificacion

notificaciones_bp = Blueprint('notificaciones', __name__, url_prefix='/notificaciones')


@notificaciones_bp.route('/', methods=['GET'])
def listar_notificaciones():
    notificaciones = Notificacion.query.all()
    resultado = [
        {
            'id': n.notificacion_id,
            'usuario_id': n.usuario_id,
            'tipo': n.tipo.value,
            'titulo': n.titulo,
            'mensaje': n.mensaje,
            'fecha_envio': n.fecha_envio,
            'fecha_lectura': n.fecha_lectura,
            'leida': n.leida,
            'url_accion': n.url_accion,
            'prioridad': n.prioridad.value
        }
        for n in notificaciones
    ]
    return jsonify(resultado)


@notificaciones_bp.route('/<int:notificacion_id>', methods=['GET'])
def obtener_notificacion(notificacion_id):
    notificacion = Notificacion.query.get_or_404(notificacion_id)
    return jsonify({
        'id': notificacion.notificacion_id,
        'usuario_id': notificacion.usuario_id,
        'tipo': notificacion.tipo.value,
        'titulo': notificacion.titulo,
        'mensaje': notificacion.mensaje,
        'fecha_envio': notificacion.fecha_envio,
        'fecha_lectura': notificacion.fecha_lectura,
        'leida': notificacion.leida,
        'url_accion': notificacion.url_accion,
        'prioridad': notificacion.prioridad.value
    })


@notificaciones_bp.route('/', methods=['POST'])
def crear_notificacion():
    data = request.get_json()

    notificacion = Notificacion(
        usuario_id=data['usuario_id'],
        tipo=TipoNotificacion[data['tipo']],
        titulo=data['titulo'],
        mensaje=data['mensaje'],
        url_accion=data.get('url_accion'),
        prioridad=PrioridadNotificacion[data.get('prioridad', 'MEDIA')]
    )

    db.session.add(notificacion)
    db.session.commit()

    return jsonify({'mensaje': 'Notificación creada', 'id': notificacion.notificacion_id}), 201


@notificaciones_bp.route('/<int:notificacion_id>', methods=['PUT'])
def actualizar_notificacion(notificacion_id):
    notificacion = Notificacion.query.get_or_404(notificacion_id)
    data = request.get_json()

    notificacion.titulo = data.get('titulo', notificacion.titulo)
    notificacion.mensaje = data.get('mensaje', notificacion.mensaje)
    notificacion.leida = data.get('leida', notificacion.leida)
    notificacion.url_accion = data.get('url_accion', notificacion.url_accion)
    notificacion.prioridad = PrioridadNotificacion[data.get('prioridad', notificacion.prioridad.name)]

    if data.get('fecha_lectura'):
        notificacion.fecha_lectura = data['fecha_lectura']

    db.session.commit()
    return jsonify({'mensaje': 'Notificación actualizada'})


@notificaciones_bp.route('/<int:notificacion_id>', methods=['DELETE'])
def eliminar_notificacion(notificacion_id):
    notificacion = Notificacion.query.get_or_404(notificacion_id)
    db.session.delete(notificacion)
    db.session.commit()
    return jsonify({'mensaje': 'Notificación eliminada'})
