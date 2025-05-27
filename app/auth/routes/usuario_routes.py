# app/auth/routes/usuario_routes.py
from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth.models import Usuario 
from app.auditoria.utils import registrar_auditoria, ResultadoAccion
from app.auditoria.decorators import audit_action
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

usuario_bp = Blueprint('usuario_bp', __name__)

def usuario_to_dict(usuario):
    return {
        'usuario_id': usuario.usuario_id,
        'nombre': usuario.nombre, 
        'email': usuario.email,   
        'activo': usuario.activo,
        'ultimo_login': usuario.ultimo_login.isoformat() if usuario.ultimo_login else None,
        'intentos_fallidos': usuario.intentos_fallidos,
        'fecha_bloqueo': usuario.fecha_bloqueo.isoformat() if usuario.fecha_bloqueo else None,
        'rol_id': usuario.rol_id,
        'rol_nombre': usuario.rol.nombre if usuario.rol else None,  
    }

@usuario_bp.route('/login', methods=['POST']) 
def login():

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Se requieren email y contraseña"}), 400

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        registrar_auditoria(
            accion='INICIO_SESION_FALLIDO',
            entidad_afectada='Usuario',
            id_entidad="N/A",
            detalles={'email_intentado': email, 'razon': 'usuario no encontrado'},
            resultado=ResultadoAccion.FALLO,
            usuario_id="ANONYMOUS"
        )
        return jsonify({"error": "Credenciales inválidas"}), 401

    if not usuario.activo: 
        registrar_auditoria(
            accion='INTENTO_LOGIN_CUENTA_INACTIVA',
            entidad_afectada='Usuario',
            id_entidad=usuario.usuario_id,
            detalles={'email': email, 'estado_cuenta': 'inactiva'},
            resultado=ResultadoAccion.FALLO,
            usuario_id="ANONYMOUS"
        )
        return jsonify({"error": "Su cuenta está inactiva. Contacte al administrador."}), 401


    if usuario.fecha_bloqueo and usuario.fecha_bloqueo > datetime.utcnow():
        registrar_auditoria(
            accion='INTENTO_LOGIN_CUENTA_BLOQUEADA',
            entidad_afectada='Usuario',
            id_entidad=usuario.usuario_id,
            detalles={'email': email, 'estado_cuenta': 'bloqueada'},
            resultado=ResultadoAccion.FALLO,
            usuario_id="ANONYMOUS"
        )
        return jsonify({"error": f"Su cuenta ha sido bloqueada hasta {usuario.fecha_bloqueo.strftime('%Y-%m-%d %H:%M')}. Contacte al administrador."}), 401

    if check_password_hash(usuario.password_hash, password):
        login_user(usuario)
        usuario.intentos_fallidos = 0
        usuario.fecha_bloqueo = None
        usuario.ultimo_login = datetime.utcnow()
        db.session.commit()

        registrar_auditoria(
            accion='INICIO_SESION',
            entidad_afectada='Usuario',
            id_entidad=usuario.usuario_id,
            detalles={'email': email},
            resultado=ResultadoAccion.EXITO,
            usuario_id=usuario.usuario_id
        )

        return jsonify({
            "mensaje": "Inicio de sesión exitoso",
            "usuario": usuario_to_dict(usuario)
        }), 200

    else: 
        usuario.intentos_fallidos = (usuario.intentos_fallidos or 0) + 1
        if usuario.intentos_fallidos >= 5: 
            usuario.fecha_bloqueo = datetime.utcnow() + timedelta(minutes=15)
            registrar_auditoria(
                accion='CUENTA_BLOQUEADA_POR_INTENTOS',
                entidad_afectada='Usuario',
                id_entidad=usuario.usuario_id,
                detalles={'email': email, 'intentos_fallidos': usuario.intentos_fallidos, 'bloqueado_hasta': str(usuario.fecha_bloqueo)},
                resultado=ResultadoAccion.ADVERTENCIA,
                usuario_id=usuario.usuario_id
            )
            db.session.commit()
            return jsonify({"error": "Su cuenta ha sido bloqueada debido a múltiples intentos fallidos. Contacte al administrador."}), 401

        db.session.commit() 
        
        registrar_auditoria(
            accion='INICIO_SESION_FALLIDO',
            entidad_afectada='Usuario',
            id_entidad=usuario.usuario_id,
            detalles={'email_intentado': email, 'razon': 'contraseña incorrecta'},
            resultado=ResultadoAccion.FALLO,
            usuario_id=usuario.usuario_id
        )
        return jsonify({"error": "Credenciales inválidas"}), 401


@usuario_bp.route('/logout', methods=['POST']) 
@login_required
def logout():
    usuario_id = current_user.usuario_id
    logout_user()
    registrar_auditoria(
        accion='CIERRE_SESION',
        entidad_afectada='Usuario',
        id_entidad=usuario_id,
        resultado=ResultadoAccion.EXITO,
        usuario_id=usuario_id
    )
    return jsonify({'mensaje': 'Sesión cerrada exitosamente'}), 200

@usuario_bp.route('/usuarios', methods=['POST'])
@audit_action(
    accion='CREAR_USUARIO',
    entidad_afectada_name='Usuario',
    include_args_in_details=['data'],
    obj_id_attr='usuario_id'
)
def crear_usuario():
    data = request.get_json()
    
    required_fields = ['usuario_id', 'nombre', 'email', 'password', 'rol_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'El campo "{field}" es requerido'}), 400

    if 'secretaria_id' not in data:
         return jsonify({'error': 'El campo "secretaria_id" es requerido'}), 400
    
    data['password_hash'] = generate_password_hash(data['password'])
    del data['password'] 

    try:
        nuevo_usuario = Usuario(**data)
        db.session.add(nuevo_usuario)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear usuario: {str(e)}'}), 500

    return jsonify({'mensaje': 'Usuario creado exitosamente', 'usuario_id': nuevo_usuario.usuario_id}), 201

@usuario_bp.route('/usuarios/<string:usuario_id>', methods=['DELETE'])
@audit_action(
    accion='ELIMINAR_USUARIO',
    entidad_afectada_name='Usuario',
    id_param_name='usuario_id',
    include_obj_attrs_in_details=['nombre', 'email']
)
def eliminar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'mensaje': 'Usuario eliminado exitosamente'}), 200 