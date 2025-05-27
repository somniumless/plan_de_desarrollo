from app.extensiones import db
from datetime import datetime
from sqlalchemy import Enum 
import enum 
from sqlalchemy.orm import relationship
from sqlalchemy import CheckConstraint, ForeignKey

class EstadoMetaEnum(enum.Enum):
    PLANIFICADA = "PLANIFICADA"
    EN_EJECUCION = "EN_EJECUCION"
    CUMPLIDA = "CUMPLIDA"
    CANCELADA = "CANCELADA"

class Meta(db.Model):
    __tablename__ = 'Meta'
    
    meta_id = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    meta_resultado = db.Column(db.Text)
    descripcion_resultado = db.Column(db.Text)
    unidad_medida = db.Column(db.String(50))
    estado = db.Column(
        db.Enum(EstadoMetaEnum), 
        default=EstadoMetaEnum.PLANIFICADA, 
        nullable=False
    )
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    fecha_registro = db.Column(
        db.TIMESTAMP,
        server_default=db.func.current_timestamp(),
        nullable=False
    )
    
    avances = db.relationship('Avance', backref='meta', lazy=True) 
    indicadores = db.relationship('Indicador', secondary='Meta_Indicador', backref='metas')
    entidades = db.relationship('EntidadResponsable', secondary='Meta_Entidad', backref='metas')

    def __repr__(self):
        return f'<Meta {self.meta_id}: {self.nombre}>'


class TipoEntidad(enum.Enum):
    LIDER = "LIDER"
    CORRESPONSABLE = "CORRESPONSABLE"


class EntidadResponsable(db.Model):
    __tablename__ = 'Entidad_Responsable'

    entidad_id = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo_entidad = db.Column(db.Enum(TipoEntidad), nullable=False)

    def __repr__(self):
        return f"<EntidadResponsable {self.entidad_id} - {self.nombre}>"


class MetaEntidad(db.Model):
    __tablename__ = 'Meta_Entidad'
    
    meta_id = db.Column(
        db.String(20),
        db.ForeignKey('Meta.meta_id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False
    )
    
    entidad_id = db.Column(
        db.String(20),
        db.ForeignKey('Entidad_Responsable.entidad_id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False
    )
    
    meta = db.relationship('Meta', backref=db.backref('meta_entidades', cascade='all, delete'))
    entidad = db.relationship('EntidadResponsable', backref=db.backref('meta_entidades', cascade='all, delete'))

    def __repr__(self):
        return f'<MetaEntidad meta_id={self.meta_id} entidad_id={self.entidad_id}>'

class Avance(db.Model):
    __tablename__ = 'Avance'

    avance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    meta_id = db.Column(db.String(20), db.ForeignKey('Meta.meta_id'), nullable=False) 
    
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_registro = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    porcentaje = db.Column(db.Numeric(5, 2), nullable=True)
    aprobado = db.Column(db.Boolean, default=False)

    usuario_id = db.Column(db.String(20), db.ForeignKey('Usuario.usuario_id', ondelete='RESTRICT'), nullable=False)
    usuario_aprobador = db.Column(db.String(20), db.ForeignKey('Usuario.usuario_id', ondelete='SET NULL'), nullable=True)
    fecha_aprobacion = db.Column(db.DateTime, nullable=True)

    usuario = relationship('Usuario', foreign_keys=[usuario_id], backref='avances_creados')
    aprobador = relationship('Usuario', foreign_keys=[usuario_aprobador], backref='avances_aprobados')

    __table_args__ = (
        CheckConstraint('porcentaje >= 0 AND porcentaje <= 100', name='check_porcentaje_range'),
    )

    def __repr__(self):
        return f"<Avance {self.avance_id} - {self.titulo}>"