from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime 

class Usuario(UserMixin, db.Model):
    __tablename__ = 'Usuario'
    usuario_id = db.Column(db.String(20), primary_key=True)
    rol_id = db.Column(db.String(20), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.usuario_id)

    def to_dict(self):
        return {
            'usuario_id': self.usuario_id,
            'rol_id': self.rol_id,
            'nombre': self.nombre,
            'email': self.email,
        }

class Meta(db.Model):
    __tablename__ = 'Meta'
    meta_id = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    meta_resultado = db.Column(db.Text)
    descripcion_resultado = db.Column(db.Text)
    unidad_medida = db.Column(db.String(50))
    estado = db.Column(db.Enum('PLANIFICADA', 'EN_EJECUCION', 'CUMPLIDA', 'CANCELADA'), default='PLANIFICADA')
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    fecha_registro = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'meta_id': self.meta_id,
            'nombre': self.nombre,
            'meta_resultado': self.meta_resultado,
            'descripcion_resultado': self.descripcion_resultado,
            'unidad_medida': self.unidad_medida,
            'estado': self.estado,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }