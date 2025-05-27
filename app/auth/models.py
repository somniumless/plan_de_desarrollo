# auth models.py

from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum
from sqlalchemy.dialects.mysql import TINYINT
from datetime import datetime
from sqlalchemy.orm import relationship 

class Rol(db.Model):
    __tablename__ = 'rol' 

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

class NivelAcceso(enum.Enum):
    LECTURA = "LECTURA"
    ESCRITURA = "ESCRITURA"
    TOTAL = "TOTAL"

class Permiso(db.Model):
    __tablename__ = 'permiso' 

    permiso_id = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    nivel_acceso = db.Column(db.Enum(NivelAcceso), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Permiso {self.permiso_id} - {self.nombre}>"

class RolPermiso(db.Model):
    __tablename__ = 'rol_permiso' 

    rol_id = db.Column(db.String(20), db.ForeignKey('rol.rol_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True) # <--- CORREGIDO ForeignKey
    permiso_id = db.Column(db.String(20), db.ForeignKey('permiso.permiso_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True) # <--- CORREGIDO ForeignKey
    fecha_asignacion = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    rol = db.relationship('Rol', backref=db.backref('permisos_asignados', cascade='all, delete-orphan'))
    permiso = db.relationship('Permiso', backref=db.backref('roles_asociados', cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<RolPermiso rol_id={self.rol_id}, permiso_id={self.permiso_id}>"

class TipoEntidad(enum.Enum): 
    LIDER = "LIDER"
    CORRESPONSABLE = "CORRESPONSABLE"

class EntidadResponsable(db.Model):
    __tablename__ = 'entidad_responsable' 

    entidad_id = db.Column(db.String(20), primary_key=True) 
    nombre = db.Column(db.String(100), nullable=False) 
    tipo_entidad = db.Column(db.Enum(TipoEntidad), nullable=False) 

    def __repr__(self):
        return f"<EntidadResponsable {self.entidad_id} - {self.nombre}>" 

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuario' 

    usuario_id = db.Column(db.String(20), primary_key=True)
    rol_id = db.Column(db.String(20), db.ForeignKey('rol.rol_id', onupdate='CASCADE'), nullable=False) # <--- CORREGIDO ForeignKey

    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    fecha_creacion = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    ultimo_login = db.Column(db.DateTime)
    activo = db.Column(db.Boolean, default=True)

    intentos_fallidos = db.Column(TINYINT(unsigned=True), default=0)
    fecha_bloqueo = db.Column(db.DateTime)

    secretaria_id = db.Column(db.String(20), db.ForeignKey('entidad_responsable.entidad_id', onupdate='CASCADE'), nullable=True) # <--- CORREGIDO: tipo, nombre de tabla y PK
    secretaria = relationship('EntidadResponsable', backref='usuarios_asignados', primaryjoin="Usuario.secretaria_id == EntidadResponsable.entidad_id") # <--- Añadida primaryjoin para claridad

    rol = db.relationship('Rol', backref=db.backref('usuarios', lazy=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        if self.fecha_bloqueo and self.fecha_bloqueo > datetime.utcnow():
            return False
        return self.activo

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.usuario_id)

    def __repr__(self):
        return f"<Usuario {self.usuario_id} - {self.nombre}>"

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(user_id)