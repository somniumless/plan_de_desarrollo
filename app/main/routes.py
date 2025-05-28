# app/main/routes.py
from flask import render_template, redirect, url_for, Blueprint, current_app, send_from_directory
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index_publico():
    plan_de_desarrollo_data = [
        {
            'nombre_display': 'Beneficiar a 220 estudiantes con la Cátedra de Turismo',
            'estado': 'Planificación',
            'progreso': '0%',
            'secretaria': 'Secretaría de Desarrollo Económico y Turismo'
        },
        {
            'nombre_display': 'Implementar 81 proyectos ambientales educativos',
            'estado': 'En Ejecución',
            'progreso': '25%',
            'secretaria': 'Secretaría de Desarrollo Rural y Ambiente'
        },
        {
            'nombre_display': 'Beneficiar 1500 estudiantes con estrategias de promoción del bilingüismo',
            'estado': 'Cumplida',
            'progreso': '100%',
            'secretaria': 'Secretaría de Educación'
        },
    ]
    return render_template('public/index.html', title='Plan de Desarrollo Municipal', plan_data=plan_de_desarrollo_data)

@main_bp.route('/el-plan-de-desarrollo')
def plan_detalles():
    return render_template('public/plan_detalles.html', title='El Plan de Desarrollo Municipal') 

@main_bp.route('/ver_plan_completo')
def serve_plan_completo_pdf():
    pdf_filename = 'plan-de-desarrollo.pdf' 
    directory = current_app.static_folder + '/documentos' 

    return send_from_directory(
        directory=directory,
        path=pdf_filename,
        as_attachment=False 
    )

@main_bp.route('/documentos/<path:filename>')
def serve_document(filename):
    directory = current_app.static_folder + '/documentos'
    try:
        return send_from_directory(
            directory=directory,
            path=filename,
            as_attachment=False
        )
    except FileNotFoundError:
        return "Archivo no encontrado", 404

@main_bp.route('/dashboard')
@login_required
def dashboard_privado():
    metas_del_usuario = [
        {'nombre': 'Mi Meta Asignada 1', 'estado': 'En Progreso', 'avance': '60%', 'fecha_limite': '2025-12-31'},
        {'nombre': 'Tarea Pendiente X', 'estado': 'Pendiente', 'avance': '0%', 'fecha_limite': '2025-06-15'},
    ]
    return render_template('private/dashboard.html', title='Mi Dashboard', user=current_user, metas=metas_del_usuario)

@main_bp.route('/preguntas-frecuentes')
def preguntas_frecuentes():
    return render_template('public/preguntas_frecuentes.html', title='Preguntas Frecuentes')

@main_bp.route('/contacto')
def contacto():
    return render_template('public/contacto.html', title='Contacto')