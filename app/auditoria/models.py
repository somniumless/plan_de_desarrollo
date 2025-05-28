# app/auditoria/models.py
from app.extensiones import db 
from sqlalchemy import Enum, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from sqlalchemy.dialects.mysql import JSON 

class ResultadoAccion(enum.Enum):
    EXITO = "EXITO"
    FALLO = "FALLO"
    ADVERTENCIA = "ADVERTENCIA"

class Auditoria(db.Model):
    __tablename__ = 'auditoria' 

    auditoria_id = db.Column(BigInteger, primary_key=True, autoincrement=True)

    usuario_id = db.Column(db.String(20), db.ForeignKey('usuario.usuario_id', ondelete='SET NULL'), nullable=True) 

    accion = db.Column(db.String(50), nullable=False)
    entidad_afectada = db.Column(db.String(50), nullable=False)

    id_entidad = db.Column(db.String(50), nullable=True) 
    fecha_accion = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    detalles = db.Column(JSON, nullable=True) 
    user_agent = db.Column(db.String(255), nullable=True)
    resultado = db.Column(db.Enum(ResultadoAccion), nullable=False)
    usuario = relationship('Usuario', backref='registros_auditoria') 
    def __repr__(self):
        return f"<Auditoria {self.auditoria_id} - {self.accion}>"

    def to_dict(self):
        return {
            'auditoria_id': self.auditoria_id,
            'usuario_id': self.usuario_id,
            'accion': self.accion,
            'entidad_afectada': self.entidad_afectada,
            'id_entidad': self.id_entidad,
            'fecha_accion': self.fecha_accion.isoformat() if self.fecha_accion else None,
            'detalles': self.detalles,
            'user_agent': self.user_agent,
            'resultado': self.resultado.value 
        }