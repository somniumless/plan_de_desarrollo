from flask import Flask
from app import create_app, db
from app.auth.models import Usuario 

app = create_app()

if __name__ == '__main__':

    with app.app_context():
        admin_user = Usuario.query.filter_by(email='admin@example.com').first()
        if not admin_user:
            from werkzeug.security import generate_password_hash
            try:
                new_admin = Usuario(
                    usuario_id='admin_zipa_1',
                    nombre='Administrador Prueba',
                    email='admin@example.com',
                    password_hash=generate_password_hash('password123'),
                    activo=True,
                    rol_id='ADMIN',      
                )
                db.session.add(new_admin)
                db.session.commit()
                print("--- USUARIO ADMINISTRADOR DE PRUEBA CREADO: admin@example.com / password123 ---")
            except Exception as e:
                db.session.rollback()
                print(f"--- ERROR AL CREAR USUARIO ADMINISTRADOR DE PRUEBA: {e} ---")

    app.run(debug=True)