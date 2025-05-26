from flask import Blueprint, request, jsonify
from .models import Indicador, MetaIndicador
from app import db

indicadores_bp = Blueprint('indicadores', __name__, url_prefix='/indicadores')

@indicadores_bp.route('/', methods=['GET'])
def get_indicadores():
    indicadores = Indicador.query.all()
    return jsonify([{
        "indicador_id": i.indicador_id,
        "nombre": i.nombre,
        "formula": i.formula
    } for i in indicadores])

@indicadores_bp.route('/<indicador_id>/metas', methods=['POST'])
def link_to_meta(indicador_id):
    data = request.get_json()
    link = MetaIndicador(
        meta_id=data['meta_id'],
        indicador_id=indicador_id,
        valor_actual=data.get('valor_actual')
    )
    db.session.add(link)
    db.session.commit()
    return jsonify({"message": "Indicador vinculado a meta"}), 201