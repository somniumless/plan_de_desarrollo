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
    }

@usuario_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario:
            if usuario.fecha_bloqueo and usuario.fecha_bloqueo > datetime.utcnow():
                flash(f'Su cuenta ha sido bloqueada hasta {usuario.fecha_bloqueo.strftime("%Y-%m-%d %H:%M")}. Contacte al administrador.', 'danger')
                registrar_auditoria(
                    accion='INTENTO_LOGIN_CUENTA_BLOQUEADA',
                    entidad_afectada='Usuario',
                    id_entidad=usuario.usuario_id,
                    detalles={'email': email, 'estado_cuenta': 'bloqueada'},
                    resultado=ResultadoAccion.FALLO,
                    usuario_id="ANONYMOUS" 
                )
                return redirect(url_for('usuario_bp.login'))

        if usuario and check_password_hash(usuario.password_hash, password):
            login_user(usuario)
            usuario.intentos_fallidos = 0
            usuario.fecha_bloqueo = None 
            usuario.ultimo_login = datetime.utcnow()
            db.session.commit()

            flash('Sesión iniciada con éxito.', 'success')
            registrar_auditoria(
                accion='INICIO_SESION',
                entidad_afectada='Usuario',
                id_entidad=usuario.usuario_id,
                detalles={'email': email},
                resultado=ResultadoAccion.EXITO,
                usuario_id=usuario.usuario_id
            )
            return redirect(url_for('main.dashboard')) # <-- ¡CAMBIA 'main.dashboard' por tu ruta real!

        else:
            if usuario:
                usuario.intentos_fallidos = (usuario.intentos_fallidos or 0) + 1 
                if usuario.intentos_fallidos >= 5:
                    usuario.fecha_bloqueo = datetime.utcnow() + timedelta(minutes=15) 
                    flash('Su cuenta ha sido bloqueada debido a múltiples intentos fallidos. Contacte al administrador.', 'danger')
                    registrar_auditoria(
                        accion='CUENTA_BLOQUEADA_POR_INTENTOS',
                        entidad_afectada='Usuario',
                        id_entidad=usuario.usuario_id,
                        detalles={'email': email, 'intentos_fallidos': usuario.intentos_fallidos, 'bloqueado_hasta': str(usuario.fecha_bloqueo)},
                        resultado=ResultadoAccion.ADVERTENCIA,
                        usuario_id=usuario.usuario_id
                    )
                db.session.commit()

                flash('Credenciales inválidas.', 'danger')
                registrar_auditoria(
                    accion='INICIO_SESION_FALLIDO',
                    entidad_afectada='Usuario',
                    id_entidad=usuario.usuario_id, 
                    detalles={'email_intentado': email, 'razon': 'contraseña incorrecta'},
                    resultado=ResultadoAccion.FALLO,
                    usuario_id="ANONYMOUS"
                )
            else:
                flash('Credenciales inválidas.', 'danger')
                registrar_auditoria(
                    accion='INICIO_SESION_FALLIDO',
                    entidad_afectada='Usuario',
                    id_entidad=email, 
                    detalles={'email_intentado': email, 'razon': 'usuario no encontrado'},
                    resultado=ResultadoAccion.FALLO,
                    usuario_id="ANONYMOUS"
                )
    
    return render_template('auth/login.html') # <-- ¡CAMBIA 'auth/login.html' por la ruta de tu plantilla de login!

@usuario_bp.route('/logout')
@login_required 
def logout():
    usuario_id = current_user.usuario_id 
    logout_user() 
    flash('Sesión cerrada.', 'info')
    registrar_auditoria(
        accion='CIERRE_SESION',
        entidad_afectada='Usuario',
        id_entidad=usuario_id,
        resultado=ResultadoAccion.EXITO,
        usuario_id=usuario_id 
    )
    return redirect(url_for('usuario_bp.login')) # Redirige a la página de login


@usuario_bp.route('/usuarios', methods=['POST'])
@audit_action(
    accion='CREAR_USUARIO',
    entidad_afectada_name='Usuario',
    include_args_in_details=['data'], 
    obj_id_attr='usuario_id' 
)
def crear_usuario():
    data = request.get_json()
    if 'password' in data:
        data['password_hash'] = generate_password_hash(data['password'])
        del data['password'] 
    
    nuevo_usuario = Usuario(**data)
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({'mensaje': 'Usuario creado exitosamente', 'usuario_id': nuevo_usuario.usuario_id}), 201

@usuario_bp.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([usuario_to_dict(u) for u in usuarios])

@usuario_bp.route('/usuarios/<string:usuario_id>', methods=['GET'])
def obtener_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    return jsonify(usuario_to_dict(usuario))

@usuario_bp.route('/usuarios/<string:usuario_id>', methods=['PUT'])
@audit_action(
    accion='ACTUALIZAR_USUARIO',
    entidad_afectada_name='Usuario',
    id_param_name='usuario_id', 
    include_args_in_details=['data'] 
)
def actualizar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    data = request.get_json()
    for key, value in data.items():
        if key == 'password': 
            setattr(usuario, 'password_hash', generate_password_hash(value))
        else:
            setattr(usuario, key, value)
    db.session.commit()
    return jsonify({'mensaje': 'Usuario actualizado exitosamente'})

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
    return jsonify({'mensaje': 'Usuario eliminado exitosamente'})