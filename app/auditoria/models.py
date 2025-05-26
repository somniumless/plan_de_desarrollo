from app import db

class Auditoria(db.Model):
    __tablename__ = 'Auditoria'
    auditoria_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.String(20), db.ForeignKey('Usuario.usuario_id'))
    accion = db.Column(db.String(50), nullable=False)
    detalles = db.Column(db.JSON)  # Datos adicionales en formato JSON