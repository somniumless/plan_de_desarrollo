from flask import Blueprint, request, jsonify
from app import db
from models import Usuario

usuario_bp = Blueprint('usuario_bp', __name__)

def usuario_to_dict(usuario):
    return {
        'usuario_id': usuario.usuario_id,
        'nombre': usuario.nombre,
        'email': usuario.email,
        # agrega otros campos que quieras enviar al cliente
    }

@usuario_bp.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    nuevo_usuario = Usuario(**data)
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({'mensaje': 'Usuario creado exitosamente'}), 201

@usuario_bp.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([usuario_to_dict(u) for u in usuarios])

@usuario_bp.route('/usuarios/<string:usuario_id>', methods=['GET'])
def obtener_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    return jsonify(usuario_to_dict(usuario))

@usuario_bp.route('/usuarios/<string:usuario_id>', methods=['PUT'])
def actualizar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    data = request.get_json()
    for key, value in data.items():
        setattr(usuario, key, value)
    db.session.commit()
    return jsonify({'mensaje': 'Usuario actualizado exitosamente'})

@usuario_bp.route('/usuarios/<string:usuario_id>', methods=['DELETE'])
def eliminar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'mensaje': 'Usuario eliminado exitosamente'})
