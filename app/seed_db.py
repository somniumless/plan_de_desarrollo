# app/seed_db.py

from app import db
from app.auth.models import Rol, EntidadResponsable, Usuario, TipoEntidad, Permiso, RolPermiso, NivelAcceso
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from datetime import datetime

def seed_db():
    print("Iniciando proceso de siembra de base de datos...")

    roles_data = [
        {'rol_id': 'ADMIN', 'nombre': 'Administrador del Sistema', 'descripcion': 'Acceso total y gestión del sistema'},
        {'rol_id': 'JEFE_GABINETE', 'nombre': 'Jefe de Gabinete', 'descripcion': 'Máxima autoridad después del alcalde'},
        {'rol_id': 'SECRETARIO', 'nombre': 'Secretario de Despacho', 'descripcion': 'Jefe de una secretaría municipal'},
        {'rol_id': 'ENCARGADO_SECRETARIO', 'nombre': 'Encargado de Secretaría', 'descripcion': 'Apoya al secretario en la gestión diaria'},
        {'rol_id': 'USUARIO_SECRETARIA', 'nombre': 'Usuario de Secretaría', 'descripcion': 'Personal base de una secretaría'},
        {'rol_id': 'USUARIO_NORMAL', 'nombre': 'Usuario General', 'descripcion': 'Usuario con acceso básico a la plataforma'},
    ]

    old_autoflush_roles = db.session.autoflush
    db.session.autoflush = False
    try:
        for role_data in roles_data:
            rol = Rol.query.get(role_data['rol_id'])
            if not rol:
                new_rol = Rol(**role_data)
                db.session.add(new_rol)
                print(f"   Rol '{new_rol.nombre}' creado.")
            else:
                print(f"   Rol '{rol.nombre}' ya existe.")
    finally:
        db.session.autoflush = old_autoflush_roles
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        print("Advertencia: Algunos roles ya existían durante el commit inicial de roles.")

    entidades_data = [
        {'entidad_id': 'SEC_DES_ECONOMICO_TURISMO', 'nombre': 'Secretaría de Desarrollo Económico y Turismo', 'tipo_entidad': TipoEntidad.LIDER},
        {'entidad_id': 'SEC_DES_RURAL_AMBIENTE', 'nombre': 'Secretaría de Desarrollo Rural y Ambiente', 'tipo_entidad': TipoEntidad.LIDER},
        {'entidad_id': 'SEC_EDUCACION', 'nombre': 'Secretaría de Educación', 'tipo_entidad': TipoEntidad.LIDER},
        {'entidad_id': 'SEC_SEGURIDAD_CONVIVENCIA', 'nombre': 'Secretaría de Seguridad y Convivencia', 'tipo_entidad': TipoEntidad.LIDER},
        {'entidad_id': 'SEC_SALUD', 'nombre': 'Secretaría de Salud', 'tipo_entidad': TipoEntidad.LIDER},
        {'entidad_id': 'ALCALDIA', 'nombre': 'Alcaldía Municipal', 'tipo_entidad': TipoEntidad.LIDER}, 
    ]

    old_autoflush_entidades = db.session.autoflush
    db.session.autoflush = False
    try:
        for entidad_data in entidades_data:
            entidad = EntidadResponsable.query.get(entidad_data['entidad_id'])
            if not entidad:
                new_entidad = EntidadResponsable(**entidad_data)
                db.session.add(new_entidad)
                print(f"   Entidad '{new_entidad.nombre}' creada.")
            else:
                print(f"   Entidad '{entidad.nombre}' ya existe.")
    finally:
        db.session.autoflush = old_autoflush_entidades
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        print("Advertencia: Algunas entidades ya existían durante el commit de entidades.")

    permisos_data = [
        {'permiso_id': 'GESTOR_USUARIOS', 'nombre': 'Gestionar Usuarios', 'nivel_acceso': NivelAcceso.TOTAL, 'descripcion': 'Permite crear, editar y eliminar usuarios.'},
        {'permiso_id': 'GESTOR_ROLES', 'nombre': 'Gestionar Roles', 'nivel_acceso': NivelAcceso.TOTAL, 'descripcion': 'Permite crear, editar y eliminar roles y sus permisos.'},
        {'permiso_id': 'VER_AUDITORIA', 'nombre': 'Ver Registros de Auditoría', 'nivel_acceso': NivelAcceso.LECTURA, 'descripcion': 'Permite visualizar el log de auditoría.'},
        {'permiso_id': 'GESTION_METAS', 'nombre': 'Gestionar Metas', 'nivel_acceso': NivelAcceso.TOTAL, 'descripcion': 'Permite crear, editar y eliminar metas.'},
        {'permiso_id': 'GESTION_AVANCES', 'nombre': 'Gestionar Avances', 'nivel_acceso': NivelAcceso.TOTAL, 'descripcion': 'Permite registrar y aprobar avances de metas.'},
        {'permiso_id': 'GESTION_DOCUMENTOS', 'nombre': 'Gestionar Documentos', 'nivel_acceso': NivelAcceso.TOTAL, 'descripcion': 'Permite subir, editar y eliminar documentos.'},
        {'permiso_id': 'VER_REPORTES', 'nombre': 'Ver Reportes', 'nivel_acceso': NivelAcceso.LECTURA, 'descripcion': 'Permite visualizar reportes generados.'},
        {'permiso_id': 'GENERAR_REPORTES', 'nombre': 'Generar Reportes', 'nivel_acceso': NivelAcceso.ESCRITURA, 'descripcion': 'Permite generar nuevos reportes.'},

    ]

    old_autoflush_permisos = db.session.autoflush
    db.session.autoflush = False
    try:
        for permiso_data in permisos_data:
            permiso = Permiso.query.get(permiso_data['permiso_id'])
            if not permiso:
                new_permiso = Permiso(**permiso_data)
                db.session.add(new_permiso)
                print(f"   Permiso '{new_permiso.nombre}' creado.")
            else:
                print(f"   Permiso '{permiso.nombre}' ya existe.")
    finally:
        db.session.autoflush = old_autoflush_permisos

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        print("Advertencia: Algunos permisos ya existían durante el commit de permisos.")

    rol_permiso_data = [
        {'rol_id': 'ADMIN', 'permiso_id': 'GESTOR_USUARIOS'},
        {'rol_id': 'ADMIN', 'permiso_id': 'GESTOR_ROLES'},
        {'rol_id': 'ADMIN', 'permiso_id': 'VER_AUDITORIA'},
        {'rol_id': 'ADMIN', 'permiso_id': 'GESTION_METAS'},
        {'rol_id': 'ADMIN', 'permiso_id': 'GESTION_AVANCES'},
        {'rol_id': 'ADMIN', 'permiso_id': 'GESTION_DOCUMENTOS'},
        {'rol_id': 'ADMIN', 'permiso_id': 'VER_REPORTES'},
        {'rol_id': 'ADMIN', 'permiso_id': 'GENERAR_REPORTES'},

    ]

    old_autoflush_rol_permiso = db.session.autoflush
    db.session.autoflush = False
    try:
        for rp_data in rol_permiso_data:
            rol_permiso = RolPermiso.query.get((rp_data['rol_id'], rp_data['permiso_id']))
            if not rol_permiso:
                new_rol_permiso = RolPermiso(**rp_data)
                db.session.add(new_rol_permiso)
                print(f"   Permiso '{rp_data['permiso_id']}' asignado a Rol '{rp_data['rol_id']}'.")
            else:
                print(f"   Permiso '{rp_data['permiso_id']}' ya asignado a Rol '{rp_data['rol_id']}'.")
    finally:
        db.session.autoflush = old_autoflush_rol_permiso

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        print("Advertencia: Algunas asignaciones Rol-Permiso ya existían durante el commit.")

    users_data = [
        # Usuario Administrador del Sistema
        {'usuario_id': 'admin@zipa.gov.co', 'nombre': 'Administrador General', 'email': 'admin@zipa.gov.co',
         'password': 'password', 'rol_id': 'ADMIN', 'secretaria_id': 'ALCALDIA'}, 

        # Jefe de Gabinete
        {'usuario_id': 'jefegabinete@zipa.gov.co', 'nombre': 'Jefe de Gabinete', 'email': 'jefegabinete@zipa.gov.co',
         'password': 'password', 'rol_id': 'JEFE_GABINETE', 'secretaria_id': 'ALCALDIA'}, 

        # Secretaría de Desarrollo Económico y Turismo
        {'usuario_id': 'sde@zipa.gov.co', 'nombre': 'Secretario Des. Económico', 'email': 'sde@zipa.gov.co',
         'password': 'password', 'rol_id': 'SECRETARIO', 'secretaria_id': 'SEC_DES_ECONOMICO_TURISMO'},
        {'usuario_id': 'esde@zipa.gov.co', 'nombre': 'Encargado Des. Económico', 'email': 'esde@zipa.gov.co',
         'password': 'password', 'rol_id': 'ENCARGADO_SECRETARIO', 'secretaria_id': 'SEC_DES_ECONOMICO_TURISMO'},
        {'usuario_id': 'usde1@zipa.gov.co', 'nombre': 'Usuario Des. Económico 1', 'email': 'usde1@zipa.gov.co',
         'password': 'password', 'rol_id': 'USUARIO_SECRETARIA', 'secretaria_id': 'SEC_DES_ECONOMICO_TURISMO'},
        {'usuario_id': 'usde2@zipa.gov.co', 'nombre': 'Usuario Des. Económico 2', 'email': 'usde2@zipa.gov.co',
         'password': 'password', 'rol_id': 'USUARIO_SECRETARIA', 'secretaria_id': 'SEC_DES_ECONOMICO_TURISMO'},

        # Secretaría de Desarrollo Rural y Ambiente
        {'usuario_id': 'sdra@zipa.gov.co', 'nombre': 'Secretario Des. Rural', 'email': 'sdra@zipa.gov.co',
         'password': 'password', 'rol_id': 'SECRETARIO', 'secretaria_id': 'SEC_DES_RURAL_AMBIENTE'},
        {'usuario_id': 'esdra@zipa.gov.co', 'nombre': 'Encargado Des. Rural', 'email': 'esdra@zipa.gov.co',
         'password': 'password', 'rol_id': 'ENCARGADO_SECRETARIO', 'secretaria_id': 'SEC_DES_RURAL_AMBIENTE'},
        {'usuario_id': 'usdra1@zipa.gov.co', 'nombre': 'Usuario Des. Rural 1', 'email': 'usdra1@zipa.gov.co',
         'password': 'password', 'rol_id': 'USUARIO_SECRETARIA', 'secretaria_id': 'SEC_DES_RURAL_AMBIENTE'},
        {'usuario_id': 'usdra2@zipa.gov.co', 'nombre': 'Usuario Des. Rural 2', 'email': 'usdra2@zipa.gov.co',
         'password': 'password', 'rol_id': 'USUARIO_SECRETARIA', 'secretaria_id': 'SEC_DES_RURAL_AMBIENTE'},

        # Secretaría de Educación
        {'usuario_id': 'sed@zipa.gov.co', 'nombre': 'Secretario Educación', 'email': 'sed@zipa.gov.co',
         'password': 'password', 'rol_id': 'SECRETARIO', 'secretaria_id': 'SEC_EDUCACION'},
        {'usuario_id': 'esed@zipa.gov.co', 'nombre': 'Encargado Educación', 'email': 'esed@zipa.gov.co',
         'password': 'password', 'rol_id': 'ENCARGADO_SECRETARIO', 'secretaria_id': 'SEC_EDUCACION'},
        {'usuario_id': 'used1@zipa.gov.co', 'nombre': 'Usuario Educación 1', 'email': 'used1@zipa.gov.co',
         'password': 'password', 'rol_id': 'USUARIO_SECRETARIA', 'secretaria_id': 'SEC_EDUCACION'},
        {'usuario_id': 'used2@zipa.gov.co', 'nombre': 'Usuario Educación 2', 'email': 'used2@zipa.gov.co',
         'password': 'password', 'rol_id': 'USUARIO_SECRETARIA', 'secretaria_id': 'SEC_EDUCACION'},

        # Secretaría de Seguridad y Convivencia
        {'usuario_id': 'ssc@zipa.gov.co', 'nombre': 'Secretario Seguridad', 'email': 'ssc@zipa.gov.co',
         'password': 'password', 'rol_id': 'SECRETARIO', 'secretaria_id': 'SEC_SEGURIDAD_CONVIVENCIA'},
        {'usuario_id': 'essc@zipa.gov.co', 'nombre': 'Encargado Seguridad', 'email': 'essc@zipa.gov.co',
         'password': 'password', 'rol_id': 'ENCARGADO_SECRETARIO', 'secretaria_id': 'SEC_SEGURIDAD_CONVIVENCIA'},
        {'usuario_id': 'ussc1@zipa.gov.co', 'nombre': 'Usuario Seguridad 1', 'email': 'ussc1@zipa.gov.co',
         'password': 'password', 'rol_id': 'USUARIO_SECRETARIA', 'secretaria_id': 'SEC_SEGURIDAD_CONVIVENCIA'},
        {'usuario_id': 'ussc2@zipa.gov.co', 'nombre': 'Usuario Seguridad 2', 'email': 'ussc2@zipa.gov.co',
         'password': 'password', 'rol_id': 'USUARIO_SECRETARIA', 'secretaria_id': 'SEC_SEGURIDAD_CONVIVENCIA'},

        # Secretaría de Salud
        {'usuario_id': 'ssa@zipa.gov.co', 'nombre': 'Secretario Salud', 'email': 'ssa@zipa.gov.co',
         'password': 'password', 'rol_id': 'SECRETARIO', 'secretaria_id': 'SEC_SALUD'},
        {'usuario_id': 'essa@zipa.gov.co', 'nombre': 'Encargado Salud', 'email': 'essa@zipa.gov.co',
         'password': 'password', 'rol_id': 'ENCARGADO_SECRETARIO', 'secretaria_id': 'SEC_SALUD'},
        {'usuario_id': 'ussa1@zipa.gov.co', 'nombre': 'Usuario Salud 1', 'email': 'ussa1@zipa.gov.co',
         'password': 'password', 'rol_id': 'USUARIO_SECRETARIA', 'secretaria_id': 'SEC_SALUD'},
        {'usuario_id': 'ussa2@zipa.gov.co', 'nombre': 'Usuario Salud 2', 'email': 'ussa2@zipa.gov.co',
         'password': 'password', 'rol_id': 'USUARIO_SECRETARIA', 'secretaria_id': 'SEC_SALUD'},
    ]

    old_autoflush_users = db.session.autoflush
    db.session.autoflush = False
    try:
        for user_data in users_data:
            usuario = Usuario.query.get(user_data['usuario_id'])
            if not usuario:
                user_data['password_hash'] = generate_password_hash(user_data['password'])
                del user_data['password']
                new_user = Usuario(**user_data)
                db.session.add(new_user)
                print(f"   Usuario '{new_user.email}' creado.")
            else:
                print(f"   Usuario '{usuario.email}' ya existe.")
    finally:
        db.session.autoflush = old_autoflush_users
    
    try:
        db.session.commit()
        print("Siembra de base de datos completada exitosamente.")
    except IntegrityError as e:
        db.session.rollback()
        print(f"Advertencia: Hubo un error de integridad durante la siembra de usuarios. Esto podría indicar un problema de datos o que algunos ya existían. Detalle: {e}")
    except Exception as e:
        db.session.rollback()
        print(f"Error inesperado durante la siembra de datos: {e}")