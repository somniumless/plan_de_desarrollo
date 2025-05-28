from flask import Blueprint, request, jsonify
from app import db
from app.documentos.models import VersionDocumento
from app.documentos.models import Documento 
from app.auth.models import Usuario
from app.auditoria.utils import registrar_auditoria, ResultadoAccion
from app.auditoria.decorators import audit_action
from flask_login import current_user 
from datetime import datetime 

version_bp = Blueprint('version_documento_bp', __name__, url_prefix='/versiones')

def version_documento_to_dict(v):
    return {
        "version_id": v.version_id,
        "documento_id": v.documento_id,
        "numero_version": v.numero_version,
        "usuario_id": v.usuario_id,
        "fecha_modificacion": v.fecha_modificacion.isoformat() if v.fecha_modificacion else None,
        "cambios": v.cambios,
        "hash_version": v.hash_version,
    }

@version_bp.route('/', methods=['POST'])
@audit_action(
    accion='CREAR_VERSION_DOCUMENTO',
    entidad_afectada_name='VersionDocumento',
    include_args_in_details=['data'], 
    obj_id_attr='version_id' 
)
def crear_version():
    data = request.json
    try:
        if 'documento_id' in data and not Documento.query.get(data['documento_id']):
            return jsonify({'error': 'El documento_id proporcionado no existe'}), 400
        
        if 'usuario_id' in data and not Usuario.query.get(data['usuario_id']):
            return jsonify({'error': 'El usuario_id proporcionado no existe'}), 400

        if 'usuario_id' not in data and current_user.is_authenticated:
            data['usuario_id'] = current_user.usuario_id

        nueva_version = VersionDocumento(**data)
        db.session.add(nueva_version)
        db.session.commit()
        return jsonify({"mensaje": "Versión creada exitosamente", "data": version_documento_to_dict(nueva_version)}), 201
    except Exception as e:
        db.session.rollback() 
        return jsonify({"error": str(e)}), 400

@version_bp.route('/', methods=['GET'])
def obtener_versiones():
    versiones = VersionDocumento.query.all()
    return jsonify([version_documento_to_dict(v) for v in versiones])

@version_bp.route('/<int:id>', methods=['GET'])
def obtener_version(id):
    v = VersionDocumento.query.get_or_404(id) 
    return jsonify(version_documento_to_dict(v))

@version_bp.route('/<int:id>', methods=['DELETE'])
@audit_action(
    accion='ELIMINAR_VERSION_DOCUMENTO',
    entidad_afectada_name='VersionDocumento',
    id_param_name='id', 
    include_obj_attrs_in_details=['documento_id', 'numero_version'] 
)
def eliminar_version(id):
    v = VersionDocumento.query.get_or_404(id)
    try:
        db.session.delete(v)
        db.session.commit()
        return jsonify({"mensaje": "Versión eliminada correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400