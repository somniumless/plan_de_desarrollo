from . import db
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    __tablename__ = 'Usuario'
    usuario_id = db.Column(db.String(20), primary_key=True)
    rol_id = db.Column(db.String(20), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return self.usuario_id

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
