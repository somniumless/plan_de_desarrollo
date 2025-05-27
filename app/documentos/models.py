from app.extensiones import db
import enum

class TipoDocumento(enum.Enum):
    PDF = "PDF"
    DOCX = "DOCX"
    XLSX = "XLSX"
    PPTX = "PPTX"
    JPG = "JPG"
    PNG = "PNG"
    TXT = "TXT"
    OTRO = "OTRO"

class Documento(db.Model):
    __tablename__ = 'Documento'

    documento_id = db.Column(db.String(20), primary_key=True)
    usuario_id = db.Column(db.String(20), db.ForeignKey('Usuario.usuario_id', ondelete='RESTRICT'), nullable=False)

    nombre = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.Enum(TipoDocumento), nullable=False)
    tamaño_mb = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_subida = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    ubicacion_almacenamiento = db.Column(db.String(512))
    hash_archivo = db.Column(db.String(64))
    eliminado = db.Column(db.Boolean, default=False)

    usuario = db.relationship('Usuario', backref=db.backref('documentos', lazy=True))

    __table_args__ = (
        db.CheckConstraint('tamaño_mb > 0', name='check_tamaño_mb_positive'),
    )

    def __repr__(self):
        return f"<Documento {self.documento_id} - {self.nombre}>"

class VersionDocumento(db.Model):
    __tablename__ = 'Version_Documento'

    version_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    documento_id = db.Column(db.String(20), db.ForeignKey('Documento.documento_id', ondelete='CASCADE'), nullable=False)
    numero_version = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.String(20), db.ForeignKey('Usuario.usuario_id', ondelete='RESTRICT'), nullable=False)

    fecha_modificacion = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    cambios = db.Column(db.Text)
    hash_version = db.Column(db.String(64))

    documento = db.relationship('Documento', backref=db.backref('versiones', cascade='all, delete-orphan', lazy=True))
    usuario = db.relationship('Usuario', backref=db.backref('versiones_documento', lazy=True))

    __table_args__ = (
        db.UniqueConstraint('documento_id', 'numero_version', name='uk_documento_version'),
    )

    def __repr__(self):
        return f"<VersionDocumento {self.version_id} - Doc: {self.documento_id} v{self.numero_version}>"
