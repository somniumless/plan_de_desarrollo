from flask import Flask
from app import create_app, db
from app.auth.models import Usuario 

app = create_app()

if __name__ == '__main__':

    app.run(debug=True)