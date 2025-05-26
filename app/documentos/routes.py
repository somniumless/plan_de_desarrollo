from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from .models import Documento
from app import app, db

documentos_bp = Blueprint('documentos', __name__, url_prefix='/documentos')

@documentos_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No se encontró el archivo"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nombre de archivo inválido"}), 400
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    new_doc = Documento(
        documento_id=generate_id(),  # Función personalizada
        nombre=filename,
        tipo=filename.split('.')[-1].upper(),
        usuario_id=request.form['usuario_id']
    )
    db.session.add(new_doc)
    db.session.commit()
    
    return jsonify({"documento_id": new_doc.documento_id}), 201