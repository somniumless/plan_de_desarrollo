from flask import Blueprint, current_app, send_from_directory
import os

static_files_bp = Blueprint('static_files_bp', __name__)

@static_files_bp.route('/archivos/<path:filename>') 
def serve_document(filename):
    directory = current_app.static_folder + '/documentos'
    full_path = os.path.join(directory, filename)

    print(f"DEBUG: Intentando servir el documento desde: {full_path}")
    print(f"DEBUG: ¿Existe el archivo para el documento? {os.path.exists(full_path)}")

    try:
        file_ext = os.path.splitext(filename)[1].lower()
        mimetype = None
        if file_ext == '.pdf':
            mimetype = 'application/pdf'
        elif file_ext == '.png':
            mimetype = 'image/png'
        else:
            mimetype = None 

        return send_from_directory(
            directory=directory,
            path=filename,
            as_attachment=False, 
            mimetype=mimetype
        )
    except FileNotFoundError:
        print(f"DEBUG: FileNotFoundError para: {full_path}")
        return "Archivo no encontrado", 404