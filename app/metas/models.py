from app import db

class Meta(db.Model):
    __tablename__ = 'Meta'
    meta_id = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.Enum('PLANIFICADA', 'EN_EJECUCION', 'CUMPLIDA', 'CANCELADA'), default='PLANIFICADA')
    entidades = db.relationship('EntidadResponsable', secondary='Meta_Entidad', backref='metas')

class EntidadResponsable(db.Model):
    __tablename__ = 'Entidad_Responsable'
    entidad_id = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

class MetaEntidad(db.Model):
    __tablename__ = 'Meta_Entidad'
    meta_id = db.Column(db.String(20), db.ForeignKey('Meta.meta_id'), primary_key=True)
    entidad_id = db.Column(db.String(20), db.ForeignKey('Entidad_Responsable.entidad_id'), primary_key=True)

class Avance(db.Model):
    __tablename__ = 'Avance'
    avance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    meta_id = db.Column(db.String(20), db.ForeignKey('Meta.meta_id'))
    porcentaje = db.Column(db.Numeric(5,2), nullable=False)
    usuario_id = db.Column(db.String(20), db.ForeignKey('Usuario.usuario_id'))