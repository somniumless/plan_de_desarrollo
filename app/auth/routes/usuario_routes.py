# app/auth/routes/usuario_routes.py
from flask import Blueprint, request, jsonify, redirect, url_for, flash, render_template
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.auth.models import Usuario, Rol
from app.auditoria.utils import registrar_auditoria, ResultadoAccion
from app.auditoria.decorators import audit_action
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

usuario_bp = Blueprint('usuario_bp', __name__, template_folder='../../templates', url_prefix='/auth')

@usuario_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Ya has iniciado sesión.', 'info')
        return redirect(url_for('main.index_publico')) 

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'

        if not email or not password:
            flash("Se requieren email y contraseña.", 'error')
            registrar_auditoria(
                accion='INICIO_SESION_FALLIDO',
                entidad_afectada='Usuario',
                id_entidad="N/A",
                detalles={'email_intentado': email, 'razon': 'campos incompletos'},
                resultado=ResultadoAccion.FALLO,
                usuario_id="ANONYMOUS"
            )
            return redirect(url_for('usuario_bp.login'))

        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario:
            flash("Credenciales inválidas.", 'error')
            registrar_auditoria(
                accion='INICIO_SESION_FALLIDO',
                entidad_afectada='Usuario',
                id_entidad="N/A",
                detalles={'email_intentado': email, 'razon': 'usuario no encontrado'},
                resultado=ResultadoAccion.FALLO,
                usuario_id="ANONYMOUS"
            )
            return redirect(url_for('usuario_bp.login'))

        if not usuario.activo:
            flash("Su cuenta está inactiva. Contacte al administrador.", 'error')
            registrar_auditoria(
                accion='INTENTO_LOGIN_CUENTA_INACTIVA',
                entidad_afectada='Usuario',
                id_entidad=usuario.usuario_id,
                detalles={'email': email, 'estado_cuenta': 'inactiva'},
                resultado=ResultadoAccion.FALLO,
                usuario_id="ANONYMOUS"
            )
            return redirect(url_for('usuario_bp.login'))

        if usuario.fecha_bloqueo and usuario.fecha_bloqueo > datetime.utcnow():
            flash(f"Su cuenta ha sido bloqueada hasta {usuario.fecha_bloqueo.strftime('%Y-%m-%d %H:%M')}. Contacte al administrador.", 'error')
            registrar_auditoria(
                accion='INTENTO_LOGIN_CUENTA_BLOQUEADA',
                entidad_afectada='Usuario',
                id_entidad=usuario.usuario_id,
                detalles={'email': email, 'estado_cuenta': 'bloqueada'},
                resultado=ResultadoAccion.FALLO,
                usuario_id="ANONYMOUS"
            )
            return redirect(url_for('usuario_bp.login'))

        if check_password_hash(usuario.password_hash, password):
            login_user(usuario, remember=remember_me)
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

            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index_publico') 
            return redirect(next_page)

        else:
            usuario.intentos_fallidos = (usuario.intentos_fallidos or 0) + 1
            if usuario.intentos_fallidos >= 5:
                usuario.fecha_bloqueo = datetime.utcnow() + timedelta(minutes=15)
                flash("Su cuenta ha sido bloqueada debido a múltiples intentos fallidos. Contacte al administrador.", 'error')
                registrar_auditoria(
                    accion='CUENTA_BLOQUEADA_POR_INTENTOS',
                    entidad_afectada='Usuario',
                    id_entidad=usuario.usuario_id,
                    detalles={'email': email, 'intentos_fallidos': usuario.intentos_fallidos, 'bloqueado_hasta': str(usuario.fecha_bloqueo)},
                    resultado=ResultadoAccion.ADVERTENCIA,
                    usuario_id="ANONYMOUS"
                )
            else:
                flash("Credenciales inválidas.", 'error')

            db.session.commit()

            registrar_auditoria(
                accion='INICIO_SESION_FALLIDO',
                entidad_afectada='Usuario',
                id_entidad=usuario.usuario_id,
                detalles={'email_intentado': email, 'razon': 'contraseña incorrecta'},
                resultado=ResultadoAccion.FALLO,
                usuario_id="ANONYMOUS"
            )
            return redirect(url_for('usuario_bp.login'))

    return render_template('auth/login.html')

@usuario_bp.route('/logout', methods=['GET', 'POST'])
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
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('usuario_bp.login'))

@usuario_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index_publico')) 

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        nombre = request.form.get('nombre')

        if not email or not password or not nombre:
            flash('Todos los campos son obligatorios para el registro.', 'error')
            return redirect(url_for('usuario_bp.register'))

        if Usuario.query.filter_by(email=email).first():
            flash('El correo electrónico ya está registrado. Por favor, utiliza otro.', 'warning')
            return redirect(url_for('usuario_bp.register'))

        try:
            hashed_password = generate_password_hash(password)
            nuevo_usuario = Usuario(
                usuario_id=email,
                nombre=nombre,
                email=email,
                password_hash=hashed_password,
                activo=True,
                rol_id='USUARIO_NORMAL',
            )
            db.session.add(nuevo_usuario)
            db.session.commit()
            flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('usuario_bp.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error durante el registro: {str(e)}. Por favor, inténtalo de nuevo.', 'error')
            return redirect(url_for('usuario_bp.register'))

    return render_template('auth/register.html')

@usuario_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        flash('Si su correo electrónico está en nuestro sistema, recibirá un enlace para restablecer su contraseña.', 'info')
        return redirect(url_for('usuario_bp.login'))

    return render_template('auth/forgot_password.html')

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