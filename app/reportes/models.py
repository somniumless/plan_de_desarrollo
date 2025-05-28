from app import db 
import enum
from datetime import datetime 
from sqlalchemy.dialects.mysql import JSON 
from sqlalchemy.orm import relationship 
from sqlalchemy import ForeignKey 

class EstadoReporte(enum.Enum):
    PENDIENTE = "PENDIENTE"
    PROCESANDO = "PROCESANDO"
    COMPLETADO = "COMPLETADO"
    FALLIDO = "FALLIDO"

class Reporte(db.Model):
    __tablename__ = 'reporte' 

    reporte_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.String(20), db.ForeignKey('usuario.usuario_id', ondelete='RESTRICT'), nullable=False)
    
    tipo = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    fecha_generacion = db.Column(db.DateTime, server_default=db.func.current_timestamp(), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=True) 
    fecha_fin = db.Column(db.Date, nullable=True) 
    parametros = db.Column(JSON, nullable=True) 
    ubicacion_almacenamiento = db.Column(db.String(512), nullable=True) 
    estado = db.Column(db.Enum(EstadoReporte), default=EstadoReporte.PENDIENTE, nullable=False)

    usuario = db.relationship('Usuario', backref=db.backref('reportes', lazy=True))

    def __repr__(self):
        return f"<Reporte {self.reporte_id} - {self.nombre} - Estado: {self.estado.value}>"