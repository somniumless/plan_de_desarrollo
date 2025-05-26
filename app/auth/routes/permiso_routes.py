from flask import Blueprint, request, jsonify
from app import db 
from app.auth.models import Permiso, NivelAcceso
from app.auditoria.utils import registrar_auditoria, ResultadoAccion
from app.auditoria.decorators import audit_action
from flask_login import current_user 

permiso_bp = Blueprint('permiso_bp', __name__)

def permiso_to_dict(permiso):
    return {
        'permiso_id': permiso.permiso_id,
        'nombre': permiso.nombre,
        'nivel_acceso': permiso.nivel_acceso.value if permiso.nivel_acceso else None, 
        'descripcion': permiso.descripcion,
        'fecha_creacion': permiso.fecha_creacion.isoformat() if permiso.fecha_creacion else None
    }

@permiso_bp.route('/permisos', methods=['POST'])
@audit_action(
    accion='CREAR_PERMISO',
    entidad_afectada_name='Permiso',
    include_args_in_details=['data'], 
    obj_id_attr='permiso_id' 
)
def crear_permiso():
    data = request.get_json()
    
    nivel_acceso_str = data.get('nivel_acceso')
    if nivel_acceso_str:
        try:
            data['nivel_acceso'] = NivelAcceso[nivel_acceso_str.upper()] 
        except KeyError:
            return jsonify({'error': f'Nivel de acceso inválido: {nivel_acceso_str}. Valores permitidos: LECTURA, ESCRITURA, TOTAL.'}), 400
    
    nuevo_permiso = Permiso(**data)
    db.session.add(nuevo_permiso)
    db.session.commit()
    return jsonify({'mensaje': 'Permiso creado exitosamente', 'permiso_id': nuevo_permiso.permiso_id}), 201

@permiso_bp.route('/permisos', methods=['GET'])
def obtener_permisos():
    permisos = Permiso.query.all()
    return jsonify([permiso_to_dict(p) for p in permisos])

@permiso_bp.route('/permisos/<string:permiso_id>', methods=['GET'])
def obtener_permiso(permiso_id):
    permiso = Permiso.query.get_or_404(permiso_id)
    return jsonify(permiso_to_dict(permiso))

@permiso_bp.route('/permisos/<string:permiso_id>', methods=['PUT'])
@audit_action(
    accion='ACTUALIZAR_PERMISO',
    entidad_afectada_name='Permiso',
    id_param_name='permiso_id',
    include_args_in_details=['data'] 
)
def actualizar_permiso(permiso_id):
    permiso = Permiso.query.get_or_404(permiso_id)
    data = request.get_json()
    for key, value in data.items():
        if key == 'nivel_acceso' and value:
            try:
                setattr(permiso, key, NivelAcceso[value.upper()]) 
            except KeyError:
                return jsonify({'error': f'Nivel de acceso inválido para {key}: {value}. Valores permitidos: LECTURA, ESCRITURA, TOTAL.'}), 400
        else:
            setattr(permiso, key, value)
    db.session.commit()
    return jsonify({'mensaje': 'Permiso actualizado exitosamente'})

@permiso_bp.route('/permisos/<string:permiso_id>', methods=['DELETE'])
@audit_action(
    accion='ELIMINAR_PERMISO',
    entidad_afectada_name='Permiso',
    id_param_name='permiso_id', 
    include_obj_attrs_in_details=['nombre', 'nivel_acceso'] 
)
def eliminar_permiso(permiso_id):
    permiso = Permiso.query.get_or_404(permiso_id)
    db.session.delete(permiso)
    db.session.commit()
    return jsonify({'mensaje': 'Permiso eliminado exitosamente'})