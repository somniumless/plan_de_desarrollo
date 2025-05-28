# metas models.py

from app.extensiones import db
from datetime import datetime
from sqlalchemy import Enum
import enum
from sqlalchemy.orm import relationship
from sqlalchemy import CheckConstraint, ForeignKey
from app.auth.models import EntidadResponsable, Usuario

class EstadoMetaEnum(enum.Enum):
    PLANIFICADA = "Planificada"
    PENDIENTE = "Pendiente"
    EN_PROGRESO = "En progreso"
    COMPLETADA = "Completada"

class Meta(db.Model):
    __tablename__ = 'meta'

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

    indicadores = db.relationship(
        'Indicador',
        secondary='meta_indicador',
        backref=db.backref('metas', overlaps="meta_indicadores,indicador"),
        overlaps="meta_indicadores,indicador"
    )

    meta_entidades = db.relationship('MetaEntidad', back_populates='meta', cascade='all, delete-orphan', overlaps="metas")

    entidades = db.relationship(
        'EntidadResponsable',
        secondary='meta_entidad',
        back_populates='metas',
        overlaps="meta_entidades"
    )

    def __repr__(self):
        return f'<Meta {self.meta_id}: {self.nombre}>'

class MetaEntidad(db.Model):
    __tablename__ = 'meta_entidad'

    meta_id = db.Column(
        db.String(20),
        db.ForeignKey('meta.meta_id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False
    )

    entidad_id = db.Column(
        db.String(20),
        db.ForeignKey('entidad_responsable.entidad_id', ondelete='CASCADE'),
        primary_key=True,
        nullable=False
    )

    meta = db.relationship('Meta', back_populates='meta_entidades', overlaps="entidades,metas")
    entidad = db.relationship('EntidadResponsable', back_populates='meta_entidades', overlaps="entidades,metas")

    def __repr__(self):
        return f'<MetaEntidad meta_id={self.meta_id} entidad_id={self.entidad_id}>'

class Avance(db.Model):
    __tablename__ = 'avance'

    avance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    meta_id = db.Column(db.String(20), db.ForeignKey('meta.meta_id'), nullable=False)

    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_registro = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    porcentaje = db.Column(db.Numeric(5, 2), nullable=True)
    aprobado = db.Column(db.Boolean, default=False)

    usuario_id = db.Column(db.String(20), db.ForeignKey('usuario.usuario_id', ondelete='RESTRICT'), nullable=False)
    usuario_aprobador = db.Column(db.String(20), db.ForeignKey('usuario.usuario_id', ondelete='SET NULL'), nullable=True)
    fecha_aprobacion = db.Column(db.DateTime, nullable=True)

    usuario = relationship('Usuario', foreign_keys=[usuario_id], backref='avances_creados')
    aprobador = relationship('Usuario', foreign_keys=[usuario_aprobador], backref='avances_aprobados')

    __table_args__ = (
        CheckConstraint('porcentaje >= 0 AND porcentaje <= 100', name='check_porcentaje_range'),
    )

    def __repr__(self):
        return f"<Avance {self.avance_id} - {self.titulo}>"