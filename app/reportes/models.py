from app import db

class Reporte(db.Model):
    __tablename__ = 'Reporte'
    reporte_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.String(20), db.ForeignKey('Usuario.usuario_id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    parametros = db.Column(db.JSON)  # Para almacenar filtros usados