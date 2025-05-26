from flask import Blueprint, request, jsonify
from app import db
from documentos.models import VersionDocumento

version_bp = Blueprint('version_documento', __name__, url_prefix='/versiones')

@version_bp.route('/', methods=['POST'])
def crear_version():
    data = request.json
    try:
        nueva_version = VersionDocumento(
            documento_id=data['documento_id'],
            numero_version=data['numero_version'],
            usuario_id=data['usuario_id'],
            cambios=data.get('cambios'),
            hash_version=data.get('hash_version')
        )
        db.session.add(nueva_version)
        db.session.commit()
        return jsonify({"mensaje": "Versión creada exitosamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@version_bp.route('/', methods=['GET'])
def obtener_versiones():
    versiones = VersionDocumento.query.all()
    return jsonify([
        {
            "version_id": v.version_id,
            "documento_id": v.documento_id,
            "numero_version": v.numero_version,
            "usuario_id": v.usuario_id,
            "fecha_modificacion": v.fecha_modificacion.isoformat(),
            "cambios": v.cambios,
            "hash_version": v.hash_version
        } for v in versiones
    ])

@version_bp.route('/<int:id>', methods=['GET'])
def obtener_version(id):
    v = VersionDocumento.query.get(id)
    if not v:
        return jsonify({"error": "Versión no encontrada"}), 404
    return jsonify({
        "version_id": v.version_id,
        "documento_id": v.documento_id,
        "numero_version": v.numero_version,
        "usuario_id": v.usuario_id,
        "fecha_modificacion": v.fecha_modificacion.isoformat(),
        "cambios": v.cambios,
        "hash_version": v.hash_version
    })

@version_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_version(id):
    v = VersionDocumento.query.get(id)
    if not v:
        return jsonify({"error": "Versión no encontrada"}), 404
    db.session.delete(v)
    db.session.commit()
    return jsonify({"mensaje": "Versión eliminada correctamente"})