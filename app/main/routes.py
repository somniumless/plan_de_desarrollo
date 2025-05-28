# app/main/routes.py
from flask import render_template
from flask_login import login_required, current_user
from app.main.__init__ import main_bp 

@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required 
def dashboard():
    metas_ejemplo = [
        {'nombre': 'Meta A', 'estado': 'PLANIFICADA'},
        {'nombre': 'Meta B', 'estado': 'EN_EJECUCION'},
        {'nombre': 'Meta C', 'estado': 'CUMPLIDA'},
    ]
    return render_template('dashboard.html', metas=metas_ejemplo, user=current_user)

@main_bp.route('/home')
def home():
    return "<h1>Bienvenido a la página de inicio pública</h1><p><a href='/login'>Login</a></p>"