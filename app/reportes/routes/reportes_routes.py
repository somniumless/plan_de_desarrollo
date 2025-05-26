from flask import Blueprint, request, jsonify
from app import db
from reportes.models import Reporte, EstadoReporte

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')


@reportes_bp.route('/', methods=['GET'])
def listar_reportes():
    reportes = Reporte.query.all()
    resultado = [
        {
            'id': r.reporte_id,
            'usuario_id': r.usuario_id,
            'tipo': r.tipo,
            'nombre': r.nombre,
            'fecha_generacion': r.fecha_generacion,
            'fecha_inicio': r.fecha_inicio,
            'fecha_fin': r.fecha_fin,
            'parametros': r.parametros,
            'ubicacion_almacenamiento': r.ubicacion_almacenamiento,
            'estado': r.estado.value
        }
        for r in reportes
    ]
    return jsonify(resultado)


@reportes_bp.route('/<int:reporte_id>', methods=['GET'])
def obtener_reporte(reporte_id):
    reporte = Reporte.query.get_or_404(reporte_id)
    return jsonify({
        'id': reporte.reporte_id,
        'usuario_id': reporte.usuario_id,
        'tipo': reporte.tipo,
        'nombre': reporte.nombre,
        'fecha_generacion': reporte.fecha_generacion,
        'fecha_inicio': reporte.fecha_inicio,
        'fecha_fin': reporte.fecha_fin,
        'parametros': reporte.parametros,
        'ubicacion_almacenamiento': reporte.ubicacion_almacenamiento,
        'estado': reporte.estado.value
    })


@reportes_bp.route('/', methods=['POST'])
def crear_reporte():
    data = request.get_json()

    nuevo_reporte = Reporte(
        usuario_id=data['usuario_id'],
        tipo=data['tipo'],
        nombre=data['nombre'],
        fecha_inicio=data.get('fecha_inicio'),
        fecha_fin=data.get('fecha_fin'),
        parametros=data.get('parametros'),
        ubicacion_almacenamiento=data.get('ubicacion_almacenamiento'),
        estado=EstadoReporte[data.get('estado', 'PENDIENTE')]
    )

    db.session.add(nuevo_reporte)
    db.session.commit()

    return jsonify({'mensaje': 'Reporte creado', 'id': nuevo_reporte.reporte_id}), 201


@reportes_bp.route('/<int:reporte_id>', methods=['PUT'])
def actualizar_reporte(reporte_id):
    reporte = Reporte.query.get_or_404(reporte_id)
    data = request.get_json()

    reporte.tipo = data.get('tipo', reporte.tipo)
    reporte.nombre = data.get('nombre', reporte.nombre)
    reporte.fecha_inicio = data.get('fecha_inicio', reporte.fecha_inicio)
    reporte.fecha_fin = data.get('fecha_fin', reporte.fecha_fin)
    reporte.parametros = data.get('parametros', reporte.parametros)
    reporte.ubicacion_almacenamiento = data.get('ubicacion_almacenamiento', reporte.ubicacion_almacenamiento)
    reporte.estado = EstadoReporte[data.get('estado', reporte.estado.name)]

    db.session.commit()
    return jsonify({'mensaje': 'Reporte actualizado'})


@reportes_bp.route('/<int:reporte_id>', methods=['DELETE'])
def eliminar_reporte(reporte_id):
    reporte = Reporte.query.get_or_404(reporte_id)
    db.session.delete(reporte)
    db.session.commit()
    return jsonify({'mensaje': 'Reporte eliminado'})
