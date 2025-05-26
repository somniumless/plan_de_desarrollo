# avances/routes/avance_routes.py
from flask import Blueprint, request, jsonify
from app import db
from metas.models import Avance

avance_bp = Blueprint('avance', __name__, url_prefix='/avances')

def avance_to_dict(avance):
    return {
        'avance_id': avance.avance_id,
        'titulo': avance.titulo,
        'descripcion': avance.descripcion,
        'fecha_registro': avance.fecha_registro.isoformat() if avance.fecha_registro else None,
        'porcentaje': float(avance.porcentaje) if avance.porcentaje is not None else None,
        'aprobado': avance.aprobado,
        'usuario_id': avance.usuario_id,
        'usuario_aprobador': avance.usuario_aprobador,
        'fecha_aprobacion': avance.fecha_aprobacion.isoformat() if avance.fecha_aprobacion else None,
    }

@avance_bp.route('/', methods=['POST'])
def crear_avance():
    data = request.get_json()
    avance = Avance(**data)
    db.session.add(avance)
    db.session.commit()
    return jsonify({'mensaje': 'Avance creado exitosamente'}), 201

@avance_bp.route('/', methods=['GET'])
def listar_avances():
    avances = Avance.query.all()
    return jsonify([avance_to_dict(a) for a in avances])

@avance_bp.route('/<int:avance_id>', methods=['GET'])
def obtener_avance(avance_id):
    avance = Avance.query.get_or_404(avance_id)
    return jsonify(avance_to_dict(avance))

@avance_bp.route('/<int:avance_id>', methods=['PUT'])
def actualizar_avance(avance_id):
    avance = Avance.query.get_or_404(avance_id)
    data = request.get_json()
    for key, value in data.items():
        setattr(avance, key, value)
    db.session.commit()
    return jsonify({'mensaje': 'Avance actualizado exitosamente'})

@avance_bp.route('/<int:avance_id>', methods=['DELETE'])
def eliminar_avance(avance_id):
    avance = Avance.query.get_or_404(avance_id)
    db.session.delete(avance)
    db.session.commit()
    return jsonify({'mensaje': 'Avance eliminado exitosamente'})
