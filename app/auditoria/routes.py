from flask import Blueprint, request, jsonify, abort
from . import db
from .models import Auditoria, ResultadoAccion

auditoria_bp = Blueprint('auditoria', __name__, url_prefix='/auditoria')

# Crear un nuevo registro
@auditoria_bp.route('/', methods=['POST'])
def crear_auditoria():
    data = request.get_json()

    # Validar campos obligatorios
    required_fields = ['accion', 'entidad_afectada', 'id_entidad', 'resultado']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Falta el campo {field}'}), 400

    try:
        resultado_enum = ResultadoAccion[data['resultado']]
    except KeyError:
        return jsonify({'error': 'Resultado inválido'}), 400

    auditoria = Auditoria(
        usuario_id = data.get('usuario_id'),
        accion = data['accion'],
        entidad_afectada = data['entidad_afectada'],
        id_entidad = data['id_entidad'],
        detalles = data.get('detalles'),
        ip_origen = data.get('ip_origen'),
        user_agent = data.get('user_agent'),
        resultado = resultado_enum
    )

    db.session.add(auditoria)
    db.session.commit()

    return jsonify({'mensaje': 'Registro creado', 'id': auditoria.auditoria_id}), 201

# Obtener todos los registros
@auditoria_bp.route('/', methods=['GET'])
def listar_auditorias():
    auditorias = Auditoria.query.all()
    resultados = []
    for a in auditorias:
        resultados.append({
            'auditoria_id': a.auditoria_id,
            'usuario_id': a.usuario_id,
            'accion': a.accion,
            'entidad_afectada': a.entidad_afectada,
            'id_entidad': a.id_entidad,
            'fecha_accion': a.fecha_accion.isoformat(),
            'detalles': a.detalles,
            'ip_origen': a.ip_origen,
            'user_agent': a.user_agent,
            'resultado': a.resultado.value
        })
    return jsonify(resultados), 200

# Obtener un registro por ID
@auditoria_bp.route('/<int:auditoria_id>', methods=['GET'])
def obtener_auditoria(auditoria_id):
    auditoria = Auditoria.query.get_or_404(auditoria_id)
    resultado = {
        'auditoria_id': auditoria.auditoria_id,
        'usuario_id': auditoria.usuario_id,
        'accion': auditoria.accion,
        'entidad_afectada': auditoria.entidad_afectada,
        'id_entidad': auditoria.id_entidad,
        'fecha_accion': auditoria.fecha_accion.isoformat(),
        'detalles': auditoria.detalles,
        'ip_origen': auditoria.ip_origen,
        'user_agent': auditoria.user_agent,
        'resultado': auditoria.resultado.value
    }
    return jsonify(resultado), 200

# Actualizar un registro
@auditoria_bp.route('/<int:auditoria_id>', methods=['PUT'])
def actualizar_auditoria(auditoria_id):
    auditoria = Auditoria.query.get_or_404(auditoria_id)
    data = request.get_json()

    if 'accion' in data:
        auditoria.accion = data['accion']
    if 'entidad_afectada' in data:
        auditoria.entidad_afectada = data['entidad_afectada']
    if 'id_entidad' in data:
        auditoria.id_entidad = data['id_entidad']
    if 'detalles' in data:
        auditoria.detalles = data['detalles']
    if 'ip_origen' in data:
        auditoria.ip_origen = data['ip_origen']
    if 'user_agent' in data:
        auditoria.user_agent = data['user_agent']
    if 'resultado' in data:
        try:
            auditoria.resultado = ResultadoAccion[data['resultado']]
        except KeyError:
            return jsonify({'error': 'Resultado inválido'}), 400

    db.session.commit()
    return jsonify({'mensaje': 'Registro actualizado'}), 200

# Eliminar un registro
@auditoria_bp.route('/<int:auditoria_id>', methods=['DELETE'])
def eliminar_auditoria(auditoria_id):
    auditoria = Auditoria.query.get_or_404(auditoria_id)
    db.session.delete(auditoria)
    db.session.commit()
    return jsonify({'mensaje': 'Registro eliminado'}), 200
