from . import db
import enum

class TipoNotificacion(enum.Enum):
    SISTEMA = "SISTEMA"
    DOCUMENTO = "DOCUMENTO"
    USUARIO = "USUARIO"
    TAREA = "TAREA"
    REPORTE = "REPORTE"

class PrioridadNotificacion(enum.Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    URGENTE = "URGENTE"

class Notificacion(db.Model):
    __tablename__ = 'Notificacion'

    notificacion_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.String(20), db.ForeignKey('Usuario.usuario_id', ondelete='CASCADE'), nullable=False)
    tipo = db.Column(db.Enum(TipoNotificacion), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    fecha_envio = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    fecha_lectura = db.Column(db.DateTime)
    leida = db.Column(db.Boolean, default=False)
    url_accion = db.Column(db.String(512))
    prioridad = db.Column(db.Enum(PrioridadNotificacion), default=PrioridadNotificacion.MEDIA)

    usuario = db.relationship('Usuario', backref=db.backref('notificaciones', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<Notificacion {self.notificacion_id} - {self.titulo}>"
