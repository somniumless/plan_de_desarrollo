from flask import Blueprint, request, jsonify, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from .models import Usuario, Rol
from app import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'])
    new_user = Usuario(
        usuario_id=data['usuario_id'],
        rol_id=data['rol_id'],
        nombre=data['nombre'],
        email=data['email'],
        password_hash=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Usuario creado"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    # Lógica de login (usar Flask-Login)
    pass

@auth_bp.route('/roles', methods=['GET'])
def list_roles():
    roles = Rol.query.all()
    return jsonify([{"rol_id": r.rol_id, "nombre": r.nombre} for r in roles])