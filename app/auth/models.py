from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Rol(db.Model):
    __tablename__ = 'Rol'
    rol_id = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text)
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

class Permiso(db.Model):
    __tablename__ = 'Permiso'
    permiso_id = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    nivel_acceso = db.Column(db.Enum('LECTURA', 'ESCRITURA', 'TOTAL'), nullable=False)

class RolPermiso(db.Model):
    __tablename__ = 'Rol_Permiso'
    rol_id = db.Column(db.String(20), db.ForeignKey('Rol.rol_id'), primary_key=True)
    permiso_id = db.Column(db.String(20), db.ForeignKey('Permiso.permiso_id'), primary_key=True)

class Usuario(db.Model, UserMixin):
    __tablename__ = 'Usuario'
    usuario_id = db.Column(db.String(20), primary_key=True)
    rol_id = db.Column(db.String(20), db.ForeignKey('Rol.rol_id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)