# app/documentos/routes/documento_routes.py

from flask import Blueprint, request, jsonify
from app import db
from app.documentos.models import Documento, TipoDocumento
from app.auth.models import Usuario 
from app.auditoria.utils import registrar_auditoria, ResultadoAccion
from app.auditoria.decorators import audit_action
from flask_login import current_user 
from datetime import datetime

documento_bp = Blueprint('documento_bp', __name__, url_prefix='/documentos') 

def documento_to_dict(doc):
    return {
        "documento_id": doc.documento_id,
        "usuario_id": doc.usuario_id,
        "nombre": doc.nombre,
        "tipo": doc.tipo.name if doc.tipo else None, 
        "tamaño_mb": float(doc.tamaño_mb) if doc.tamaño_mb is not None else None,
        "fecha_subida": doc.fecha_subida.isoformat() if doc.fecha_subida else None,
        "ubicacion_almacenamiento": doc.ubicacion_almacenamiento,
        "hash_archivo": doc.hash_archivo,
        "eliminado": doc.eliminado
    }

@documento_bp.route('/', methods=['POST'])
@audit_action(
    accion='CREAR_DOCUMENTO',
    entidad_afectada_name='Documento',
    include_args_in_details=['data'], 
    obj_id_attr='documento_id' 
)
def crear_documento():
    data = request.json
    try:
        tipo_documento_str = data.get('tipo')
        if tipo_documento_str:
            try:
                data['tipo'] = TipoDocumento[tipo_documento_str.upper()]
            except KeyError:
                return jsonify({'error': f'Tipo de documento inválido: {tipo_documento_str}. Valores permitidos: {", ".join([e.name for e in TipoDocumento])}.'}), 400

        if 'usuario_id' in data and not Usuario.query.get(data['usuario_id']):
            return jsonify({'error': 'El usuario_id proporcionado no existe'}), 400

        if 'usuario_id' not in data and current_user.is_authenticated:
            data['usuario_id'] = current_user.usuario_id

        nuevo_doc = Documento(**data)
        db.session.add(nuevo_doc)
        db.session.commit()
        return jsonify({"mensaje": "Documento creado exitosamente", "data": documento_to_dict(nuevo_doc)}), 201
    except Exception as e:
        db.session.rollback() 
        return jsonify({"error": str(e)}), 400

@documento_bp.route('/', methods=['GET'])
def obtener_documentos():
    documentos = Documento.query.all()
    return jsonify([documento_to_dict(d) for d in documentos])

@documento_bp.route('/<string:id>', methods=['GET'])
def obtener_documento(id):
    doc = Documento.query.get_or_404(id) 
    return jsonify(documento_to_dict(doc))

@documento_bp.route('/<string:id>', methods=['PUT'])
@audit_action(
    accion='ACTUALIZAR_DOCUMENTO',
    entidad_afectada_name='Documento',
    id_param_name='id', 
    include_args_in_details=['data'] 
)
def actualizar_documento(id):
    doc = Documento.query.get_or_404(id)
    data = request.json
    try:
        if 'tipo' in data:
            try:
                doc.tipo = TipoDocumento[data['tipo'].upper()]
            except KeyError:
                return jsonify({'error': f'Tipo de documento inválido: {data["tipo"]}. Valores permitidos: {", ".join([e.name for e in TipoDocumento])}.'}), 400
        
        for key, value in data.items():
            if key not in ['tipo', 'documento_id', 'usuario_id', 'fecha_subida']: 
                setattr(doc, key, value)

        db.session.commit()
        return jsonify({"mensaje": "Documento actualizado correctamente", "data": documento_to_dict(doc)})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@documento_bp.route('/<string:id>', methods=['DELETE'])
@audit_action(
    accion='ELIMINAR_DOCUMENTO',
    entidad_afectada_name='Documento',
    id_param_name='id',
    include_obj_attrs_in_details=['nombre', 'tipo'] 
)
def eliminar_documento(id):
    doc = Documento.query.get_or_404(id)
    try:
        db.session.delete(doc)
        db.session.commit()
        return jsonify({"mensaje": "Documento eliminado exitosamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400