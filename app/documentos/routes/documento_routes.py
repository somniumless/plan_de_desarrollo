from flask import Blueprint, request, jsonify
from app import db
from documentos.models import Documento, TipoDocumento
from auth.models import Usuario  # Asegúrate que Usuario está en auth.models

documento_bp = Blueprint('documento', __name__, url_prefix='/documentos')

@documento_bp.route('/', methods=['POST'])
def crear_documento():
    data = request.json
    try:
        nuevo_doc = Documento(
            documento_id=data['documento_id'],
            usuario_id=data['usuario_id'],
            nombre=data['nombre'],
            tipo=TipoDocumento[data['tipo']],
            tamaño_mb=data['tamaño_mb'],
            ubicacion_almacenamiento=data.get('ubicacion_almacenamiento'),
            hash_archivo=data.get('hash_archivo'),
        )
        db.session.add(nuevo_doc)
        db.session.commit()
        return jsonify({"mensaje": "Documento creado exitosamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@documento_bp.route('/', methods=['GET'])
def obtener_documentos():
    documentos = Documento.query.all()
    return jsonify([
        {
            "documento_id": d.documento_id,
            "usuario_id": d.usuario_id,
            "nombre": d.nombre,
            "tipo": d.tipo.name,
            "tamaño_mb": float(d.tamaño_mb),
            "fecha_subida": d.fecha_subida.isoformat(),
            "ubicacion_almacenamiento": d.ubicacion_almacenamiento,
            "eliminado": d.eliminado
        }
        for d in documentos
    ])

@documento_bp.route('/<string:id>', methods=['GET'])
def obtener_documento(id):
    doc = Documento.query.get(id)
    if not doc:
        return jsonify({"error": "Documento no encontrado"}), 404
    return jsonify({
        "documento_id": doc.documento_id,
        "usuario_id": doc.usuario_id,
        "nombre": doc.nombre,
        "tipo": doc.tipo.name,
        "tamaño_mb": float(doc.tamaño_mb),
        "fecha_subida": doc.fecha_subida.isoformat(),
        "ubicacion_almacenamiento": doc.ubicacion_almacenamiento,
        "eliminado": doc.eliminado
    })

@documento_bp.route('/<string:id>', methods=['PUT'])
def actualizar_documento(id):
    doc = Documento.query.get(id)
    if not doc:
        return jsonify({"error": "Documento no encontrado"}), 404
    data = request.json
    try:
        doc.nombre = data.get('nombre', doc.nombre)
        if 'tipo' in data:
            doc.tipo = TipoDocumento[data['tipo']]
        doc.tamaño_mb = data.get('tamaño_mb', doc.tamaño_mb)
        doc.ubicacion_almacenamiento = data.get('ubicacion_almacenamiento', doc.ubicacion_almacenamiento)
        doc.eliminado = data.get('eliminado', doc.eliminado)
        db.session.commit()
        return jsonify({"mensaje": "Documento actualizado correctamente"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@documento_bp.route('/<string:id>', methods=['DELETE'])
def eliminar_documento(id):
    doc = Documento.query.get(id)
    if not doc:
        return jsonify({"error": "Documento no encontrado"}), 404
    db.session.delete(doc)
    db.session.commit()
    return jsonify({"mensaje": "Documento eliminado"})