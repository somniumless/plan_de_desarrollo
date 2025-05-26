from app import db

class Documento(db.Model):
    __tablename__ = 'Documento'
    documento_id = db.Column(db.String(20), primary_key=True)
    usuario_id = db.Column(db.String(20), db.ForeignKey('Usuario.usuario_id'), nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.Enum('PDF', 'DOCX', 'XLSX', 'PPTX', 'JPG', 'PNG', 'TXT', 'OTRO'), nullable=False)
    hash_archivo = db.Column(db.String(64))  # Para verificar integridad

class VersionDocumento(db.Model):
    __tablename__ = 'Version_Documento'
    version_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    documento_id = db.Column(db.String(20), db.ForeignKey('Documento.documento_id'), nullable=False)
    numero_version = db.Column(db.Integer, nullable=False)