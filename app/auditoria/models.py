from . import db
from sqlalchemy import Enum, BigInteger
from sqlalchemy.orm import relationship
import enum

# Definimos el Enum de Python para 'resultado'
class ResultadoAccion(enum.Enum):
    EXITO = "EXITO"
    FALLO = "FALLO"
    ADVERTENCIA = "ADVERTENCIA"

class Auditoria(db.Model):
    __tablename__ = 'Auditoria'

    auditoria_id = db.Column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.String(20), db.ForeignKey('Usuario.usuario_id', ondelete='SET NULL'), nullable=True)
    accion = db.Column(db.String(50), nullable=False)
    entidad_afectada = db.Column(db.String(50), nullable=False)
    id_entidad = db.Column(db.String(50), nullable=False)
    fecha_accion = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    detalles = db.Column(db.JSON, nullable=True)
    ip_origen = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    resultado = db.Column(db.Enum(ResultadoAccion), nullable=False)

    # Relación con Usuario
    usuario = relationship('Usuario', backref='registros_auditoria', foreign_keys=[usuario_id])

    def __repr__(self):
        return f"<Auditoria {self.auditoria_id} - {self.accion}>"
