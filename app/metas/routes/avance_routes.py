from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from app import db 
from app.metas.models import Avance, Meta 
from app.auditoria.utils import registrar_auditoria, ResultadoAccion
from app.auditoria.decorators import audit_action
from flask_login import current_user 
from app.auth.models import Usuario 

avances_bp = Blueprint('avances_bp', __name__, url_prefix='/avances')

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

@avances_bp.route('/', methods=['POST'])
@audit_action(
    accion='CREAR_AVANCE',
    entidad_afectada_name='Avance',
    include_args_in_details=['data'], 
    obj_id_attr='avance_id' 
)
def crear_avance():
    data = request.get_json()
    
    if 'usuario_id' not in data and current_user.is_authenticated:
        data['usuario_id'] = current_user.usuario_id

    if 'porcentaje' in data and isinstance(data['porcentaje'], str):
        try:
            data['porcentaje'] = float(data['porcentaje'])
        except ValueError:
            return jsonify({'error': 'El porcentaje debe ser un número válido.'}), 400

    avance = Avance(**data)
    db.session.add(avance)
    db.session.commit()
    return jsonify({'mensaje': 'Avance creado exitosamente', 'avance_id': avance.avance_id}), 201

@avances_bp.route('/', methods=['GET'])
def avances():
    return render_template('avances/avances.html')


@avances_bp.route('/<int:avance_id>', methods=['GET'])
def obtener_avance(avance_id):
    avance = Avance.query.get_or_404(avance_id)
    return jsonify(avance_to_dict(avance))

@avances_bp.route('/<int:avance_id>', methods=['PUT'])
@audit_action(
    accion='ACTUALIZAR_AVANCE',
    entidad_afectada_name='Avance',
    id_param_name='avance_id', 
    include_args_in_details=['data']
)
def actualizar_avance(avance_id):
    avance = Avance.query.get_or_404(avance_id)
    data = request.get_json()
    for key, value in data.items():
        if key == 'porcentaje' and isinstance(value, str):
            try:
                setattr(avance, key, float(value))
            except ValueError:
                return jsonify({'error': 'El porcentaje debe ser un número válido.'}), 400
        elif key == 'aprobado' and value is True:
            if current_user.is_authenticated:
                avance.aprobado = True
                avance.usuario_aprobador = current_user.usuario_id
                avance.fecha_aprobacion = datetime.now()
            else:
                return jsonify({'error': 'Usuario no autenticado para aprobar el avance.'}), 401
        else:
            setattr(avance, key, value)
    db.session.commit()
    return jsonify({'mensaje': 'Avance actualizado exitosamente'})

@avances_bp.route('/<int:avance_id>', methods=['DELETE'])
@audit_action(
    accion='ELIMINAR_AVANCE',
    entidad_afectada_name='Avance',
    id_param_name='avance_id', 
    include_obj_attrs_in_details=['titulo', 'usuario_id'] 
)
def eliminar_avance(avance_id):
    avance = Avance.query.get_or_404(avance_id)
    db.session.delete(avance)
    db.session.commit()
    return jsonify({'mensaje': 'Avance eliminado exitosamente'})