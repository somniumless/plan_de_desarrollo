from app import db
import enum

class FrecuenciaCalculo(enum.Enum):
    DIARIO = "DIARIO"
    SEMANAL = "SEMANAL"
    MENSUAL = "MENSUAL"
    TRIMESTRAL = "TRIMESTRAL"
    SEMESTRAL = "SEMESTRAL"
    ANUAL = "ANUAL"
    PERSONALIZADO = "PERSONALIZADO"

class Indicador(db.Model):
    __tablename__ = 'Indicador'

    indicador_id = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    formula = db.Column(db.Text, nullable=False)
    descripcion = db.Column(db.Text)
    unidad_medida = db.Column(db.String(20))
    frecuencia_calculo = db.Column(db.Enum(FrecuenciaCalculo))
    es_critico = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Indicador {self.indicador_id} - {self.nombre}>"


class MetaIndicador(db.Model):
    __tablename__ = 'Meta_Indicador'

    meta_id = db.Column(db.String(20), db.ForeignKey('Meta.meta_id', ondelete='CASCADE'), primary_key=True)
    indicador_id = db.Column(db.String(20), db.ForeignKey('Indicador.indicador_id', ondelete='CASCADE'), primary_key=True)

    valor_actual = db.Column(db.Numeric(15, 2))
    meta = db.Column(db.Numeric(15, 2))
    fecha_calculo = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    calculado_por = db.Column(db.String(20), db.ForeignKey('Usuario.usuario_id', ondelete='SET NULL'))

    meta_rel = db.relationship('Meta', backref=db.backref('meta_indicadores', cascade='all, delete-orphan'))
    indicador = db.relationship('Indicador', backref=db.backref('meta_indicadores', cascade='all, delete-orphan'))
    usuario = db.relationship('Usuario', backref=db.backref('meta_indicadores_calculados', lazy=True))

    def __repr__(self):
        return f"<MetaIndicador Meta:{self.meta_id} Indicador:{self.indicador_id}>"