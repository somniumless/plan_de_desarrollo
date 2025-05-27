# app/notificaciones/models.py

from app import db
import enum
from datetime import datetime
from sqlalchemy.orm import relationship

class TipoNotificacion(enum.Enum):
    SISTEMA = "SISTEMA"
    DOCUMENTO = "DOCUMENTO"
    USUARIO = "USUARIO"
    TAREA = "TAREA"
    REPORTE = "REPORTE"
    ALERTA = "ALERTA" 
    INFORMATIVA = "INFORMATIVA" 
    RECORDATORIO = "RECORDATORIO" 
    APROBACION = "APROBACION" 

class PrioridadNotificacion(enum.Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    URGENTE = "URGENTE" 
    CRITICA = "CRITICA"

class Notificacion(db.Model):
    __tablename__ = 'Notificacion'

    notificacion_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.String(20), db.ForeignKey('Usuario.usuario_id', ondelete='CASCADE'), nullable=False)
    tipo = db.Column(db.Enum(TipoNotificacion), nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    fecha_envio = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)
    fecha_lectura = db.Column(db.DateTime, nullable=True) 
    leida = db.Column(db.Boolean, default=False, nullable=False) 
    url_accion = db.Column(db.String(512), nullable=True) 
    prioridad = db.Column(db.Enum(PrioridadNotificacion), default=PrioridadNotificacion.MEDIA, nullable=False) 

    usuario = db.relationship('Usuario', backref=db.backref('notificaciones', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<Notificacion {self.notificacion_id} - {self.titulo}>"