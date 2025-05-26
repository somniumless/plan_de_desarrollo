from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum
from sqlalchemy.dialects.mysql import TINYINT

class Rol(db.Model):
    __tablename__ = 'Rol'

    rol_id = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    fecha_actualizacion = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    def __repr__(self):
        return f"<Rol {self.rol_id} - {self.nombre}>"



# Enum de nivel de acceso
class NivelAcceso(enum.Enum):
    LECTURA = "LECTURA"
    ESCRITURA = "ESCRITURA"
    TOTAL = "TOTAL"

class Permiso(db.Model):
    __tablename__ = 'Permiso'

    permiso_id = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    nivel_acceso = db.Column(db.Enum(NivelAcceso), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Permiso {self.permiso_id} - {self.nombre}>"


class RolPermiso(db.Model):
    __tablename__ = 'Rol_Permiso'

    rol_id = db.Column(db.String(20), db.ForeignKey('Rol.rol_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    permiso_id = db.Column(db.String(20), db.ForeignKey('Permiso.permiso_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    fecha_asignacion = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # Relaciones inversas (opcional, si quieres acceder desde Rol o Permiso)
    rol = db.relationship('Rol', backref=db.backref('permisos_asignados', cascade='all, delete-orphan'))
    permiso = db.relationship('Permiso', backref=db.backref('roles_asociados', cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<RolPermiso rol_id={self.rol_id}, permiso_id={self.permiso_id}>"


class Usuario(db.Model):
    __tablename__ = 'Usuario'

    usuario_id = db.Column(db.String(20), primary_key=True)
    rol_id = db.Column(db.String(20), db.ForeignKey('Rol.rol_id', onupdate='CASCADE'), nullable=False)

    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    fecha_creacion = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    ultimo_login = db.Column(db.DateTime)
    activo = db.Column(db.Boolean, default=True)

    intentos_fallidos = db.Column(TINYINT(unsigned=True), default=0)
    fecha_bloqueo = db.Column(db.DateTime)

    # Relación con la tabla Rol
    rol = db.relationship('Rol', backref=db.backref('usuarios', lazy=True))

    def __repr__(self):
        return f"<Usuario {self.usuario_id} - {self.nombre}>"