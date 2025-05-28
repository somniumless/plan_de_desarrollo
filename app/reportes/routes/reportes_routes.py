from flask import Blueprint, request, jsonify
from app import db
from app.reportes.models import Reporte, EstadoReporte
from app.auth.models import Usuario 
from app.auditoria.utils import registrar_auditoria, ResultadoAccion
from app.auditoria.decorators import audit_action
from flask_login import current_user 
from datetime import datetime
from flask import render_template

reportes_bp = Blueprint('reportes_bp', __name__, url_prefix='/reportes') 

def reporte_to_dict(r):
    return {
        'reporte_id': r.reporte_id,
        'usuario_id': r.usuario_id,
        'tipo': r.tipo, 
        'nombre': r.nombre,
        'fecha_generacion': r.fecha_generacion.isoformat() if r.fecha_generacion else None,
        'fecha_inicio': r.fecha_inicio.isoformat() if r.fecha_inicio else None,
        'fecha_fin': r.fecha_fin.isoformat() if r.fecha_fin else None,
        'parametros': r.parametros,
        'ubicacion_almacenamiento': r.ubicacion_almacenamiento,
        'estado': r.estado.value if r.estado else None
    }

@reportes_bp.route('/vista')
def vista_reportes():
    return render_template('reportes/reportes.html')

@reportes_bp.route('/', methods=['GET'])
def listar_reportes():
    reportes = Reporte.query.all()
    return jsonify([reporte_to_dict(r) for r in reportes])

@reportes_bp.route('/<int:reporte_id>', methods=['GET'])
def obtener_reporte(reporte_id):
    reporte = Reporte.query.get_or_404(reporte_id)
    return jsonify(reporte_to_dict(reporte))

@reportes_bp.route('/', methods=['POST'])
@audit_action(
    accion='CREAR_REPORTE',
    entidad_afectada_name='Reporte',
    include_args_in_details=['data'],
    obj_id_attr='reporte_id'
)
def crear_reporte():
    data = request.get_json()
    try:
        estado_str = data.get('estado', 'PENDIENTE') 
        try:
            estado_enum = EstadoReporte[estado_str.upper()]
        except KeyError:
            return jsonify({'error': f'Estado de reporte inválido: {estado_str}. Valores permitidos: {", ".join([e.value for e in EstadoReporte])}.'}), 400

        if 'usuario_id' in data and not Usuario.query.get(data['usuario_id']):
            return jsonify({'error': 'El usuario_id proporcionado no existe.'}), 400

        if 'usuario_id' not in data and current_user.is_authenticated:
            data['usuario_id'] = current_user.usuario_id
        elif 'usuario_id' not in data:
            return jsonify({'error': 'El campo "usuario_id" es obligatorio si no hay usuario autenticado.'}), 400

        fecha_inicio = None
        if 'fecha_inicio' in data and data['fecha_inicio']:
            try:
                fecha_inicio = datetime.fromisoformat(data['fecha_inicio'])
            except ValueError:
                return jsonify({'error': 'Formato de fecha_inicio inválido. Use ISO 8601.'}), 400

        fecha_fin = None
        if 'fecha_fin' in data and data['fecha_fin']:
            try:
                fecha_fin = datetime.fromisoformat(data['fecha_fin'])
            except ValueError:
                return jsonify({'error': 'Formato de fecha_fin inválido. Use ISO 8601.'}), 400

        nuevo_reporte = Reporte(
            usuario_id=data['usuario_id'],
            tipo=data['tipo'],
            nombre=data['nombre'],
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            parametros=data.get('parametros'),
            ubicacion_almacenamiento=data.get('ubicacion_almacenamiento'),
            estado=estado_enum
        )

        db.session.add(nuevo_reporte)
        db.session.commit()

        return jsonify({'mensaje': 'Reporte creado', 'data': reporte_to_dict(nuevo_reporte)}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@reportes_bp.route('/<int:reporte_id>', methods=['PUT'])
@audit_action(
    accion='ACTUALIZAR_REPORTE',
    entidad_afectada_name='Reporte',
    id_param_name='reporte_id',
    include_args_in_details=['data']
)
def actualizar_reporte(reporte_id):
    reporte = Reporte.query.get_or_404(reporte_id)
    data = request.get_json()
    try:
        if 'tipo' in data:
            reporte.tipo = data['tipo']
        if 'nombre' in data:
            reporte.nombre = data['nombre']
        
        if 'fecha_inicio' in data and data['fecha_inicio']:
            try:
                reporte.fecha_inicio = datetime.fromisoformat(data['fecha_inicio'])
            except ValueError:
                return jsonify({'error': 'Formato de fecha_inicio inválido. Use ISO 8601.'}), 400
        elif 'fecha_inicio' in data and not data['fecha_inicio']:
            reporte.fecha_inicio = None 

        if 'fecha_fin' in data and data['fecha_fin']:
            try:
                reporte.fecha_fin = datetime.fromisoformat(data['fecha_fin'])
            except ValueError:
                return jsonify({'error': 'Formato de fecha_fin inválido. Use ISO 8601.'}), 400
        elif 'fecha_fin' in data and not data['fecha_fin']:
            reporte.fecha_fin = None 

        if 'parametros' in data:
            reporte.parametros = data['parametros']
        if 'ubicacion_almacenamiento' in data:
            reporte.ubicacion_almacenamiento = data['ubicacion_almacenamiento']
        
        if 'estado' in data:
            try:
                reporte.estado = EstadoReporte[data['estado'].upper()]
            except KeyError:
                return jsonify({'error': f'Estado de reporte inválido: {data["estado"]}. Valores permitidos: {", ".join([e.value for e in EstadoReporte])}.'}), 400

        db.session.commit()
        return jsonify({'mensaje': 'Reporte actualizado', 'data': reporte_to_dict(reporte)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@reportes_bp.route('/<int:reporte_id>', methods=['DELETE'])
@audit_action(
    accion='ELIMINAR_REPORTE',
    entidad_afectada_name='Reporte',
    id_param_name='reporte_id',
    include_obj_attrs_in_details=['nombre', 'tipo', 'estado']
)
def eliminar_reporte(reporte_id):
    reporte = Reporte.query.get_or_404(reporte_id)
    try:
        db.session.delete(reporte)
        db.session.commit()
        return jsonify({'mensaje': 'Reporte eliminado'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400