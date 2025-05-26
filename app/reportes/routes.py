from flask import Blueprint, request, jsonify
from .models import Reporte
from app import db
import datetime

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/generate', methods=['POST'])
def generate_report():
    data = request.get_json()
    new_report = Reporte(
        tipo=data['tipo'],
        usuario_id=data['usuario_id'],
        parametros=data.get('parametros', {})
    )
    db.session.add(new_report)
    db.session.commit()
    return jsonify({"reporte_id": new_report.reporte_id}), 201