from flask import Blueprint, request, jsonify, redirect, url_for, flash
from app import db 
from app.auditoria.models import Auditoria, ResultadoAccion 
from app.auditoria.decorators import audit_action 
from flask_login import current_user 
from datetime import datetime 
from flask import render_template

auditoria_bp = Blueprint('auditoria_bp', __name__, url_prefix='/auditoria') 



def auditoria_to_dict(auditoria):
    return {
        'auditoria_id': auditoria.auditoria_id,
        'usuario_id': auditoria.usuario_id,
        'accion': auditoria.accion,
        'entidad_afectada': auditoria.entidad_afectada,
        'id_entidad': auditoria.id_entidad,
        'fecha_accion': auditoria.fecha_accion.isoformat() if auditoria.fecha_accion else None,
        'detalles': auditoria.detalles,
        'user_agent': auditoria.user_agent,
        'resultado': auditoria.resultado.value if auditoria.resultado else None
    }

@auditoria_bp.route('/nueva', methods=['GET'])
def nueva_auditoria():
    return render_template('auditoria/crear_auditoria.html')


@auditoria_bp.route('/', methods=['POST'])
@audit_action(
    accion='CREAR_REGISTRO_AUDITORIA',
    entidad_afectada_name='Auditoria',
    include_args_in_details=['data'], 
    obj_id_attr='auditoria_id'
)
def crear_auditoria():
    data = request.form  # <-- si usas formulario HTML, usa form en vez de get_json

    required_fields = ['accion', 'entidad_afectada', 'id_entidad', 'resultado']
    for field in required_fields:
        if field not in data:
            flash(f'Falta el campo {field}', 'error')
            return redirect(url_for('auditoria_bp.listar_auditorias'))

    try:
        resultado_enum = ResultadoAccion[data['resultado'].upper()]
    except KeyError:
        flash(f'Resultado inválido: {data["resultado"]}', 'error')
        return redirect(url_for('auditoria_bp.listar_auditorias'))

    if 'usuario_id' not in data and current_user.is_authenticated:
        data = data.copy()  # Flask's request.form is immutable
        data['usuario_id'] = current_user.usuario_id

    auditoria = Auditoria(
        usuario_id = data.get('usuario_id'),
        accion = data['accion'],
        entidad_afectada = data['entidad_afectada'],
        id_entidad = data['id_entidad'],
        detalles = data.get('detalles'),
        ip_origen = request.remote_addr,
        user_agent = request.headers.get('User-Agent'),
        resultado = resultado_enum
    )

    db.session.add(auditoria)
    db.session.commit()

    flash('Auditoría creada correctamente', 'success')
    return redirect(url_for('auditoria_bp.listar_auditorias'))

@auditoria_bp.route('/', methods=['GET'])
def listar_auditorias():
    auditorias = Auditoria.query.all()
    return render_template('auditoria/listar_auditorias.html', auditorias=auditorias)

@auditoria_bp.route('/<int:auditoria_id>', methods=['GET'])
def obtener_auditoria(auditoria_id):
    auditoria = Auditoria.query.get_or_404(auditoria_id)
    return jsonify(auditoria_to_dict(auditoria)), 200

@auditoria_bp.route('/<int:auditoria_id>', methods=['PUT'])
@audit_action(
    accion='ACTUALIZAR_REGISTRO_AUDITORIA',
    entidad_afectada_name='Auditoria',
    id_param_name='auditoria_id',
    include_args_in_details=['data'] 
)
def actualizar_auditoria(auditoria_id):
    auditoria = Auditoria.query.get_or_404(auditoria_id)
    data = request.get_json()
    try:
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
                auditoria.resultado = ResultadoAccion[data['resultado'].upper()]
            except KeyError:
                return jsonify({'error': f'Resultado inválido: {data["resultado"]}. Valores permitidos: {", ".join([e.value for e in ResultadoAccion])}.'}), 400

        db.session.commit()
        return jsonify({'mensaje': 'Registro actualizado', 'data': auditoria_to_dict(auditoria)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@auditoria_bp.route('/<int:auditoria_id>', methods=['DELETE'])
@audit_action(
    accion='ELIMINAR_REGISTRO_AUDITORIA',
    entidad_afectada_name='Auditoria',
    id_param_name='auditoria_id', 
    include_obj_attrs_in_details=['accion', 'entidad_afectada', 'id_entidad'] 
)
def eliminar_auditoria(auditoria_id):
    auditoria = Auditoria.query.get_or_404(auditoria_id)
    try:
        db.session.delete(auditoria)
        db.session.commit()
        return jsonify({'mensaje': 'Registro eliminado'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400