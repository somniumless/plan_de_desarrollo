from app import db

class Indicador(db.Model):
    __tablename__ = 'Indicador'
    indicador_id = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    formula = db.Column(db.Text, nullable=False)
    metas = db.relationship('Meta', secondary='Meta_Indicador', backref='indicadores')

class MetaIndicador(db.Model):
    __tablename__ = 'Meta_Indicador'
    meta_id = db.Column(db.String(20), db.ForeignKey('Meta.meta_id'), primary_key=True)
    indicador_id = db.Column(db.String(20), db.ForeignKey('Indicador.indicador_id'), primary_key=True)
    valor_actual = db.Column(db.Numeric(15,2))