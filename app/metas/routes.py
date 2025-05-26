from flask import Blueprint, request, jsonify
from .models import Meta, Avance
from app import db

metas_bp = Blueprint('metas', __name__, url_prefix='/metas')

@metas_bp.route('/', methods=['GET'])
def get_metas():
    metas = Meta.query.all()
    return jsonify([{
        "meta_id": m.meta_id,
        "nombre": m.nombre,
        "estado": m.estado
    } for m in metas])

@metas_bp.route('/<meta_id>/avances', methods=['POST'])
def add_avance(meta_id):
    data = request.get_json()
    new_avance = Avance(
        meta_id=meta_id,
        porcentaje=data['porcentaje'],
        usuario_id=data['usuario_id']
    )
    db.session.add(new_avance)
    db.session.commit()
    return jsonify({"message": "Avance registrado"}), 201