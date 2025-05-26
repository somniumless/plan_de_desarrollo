from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_user
from ..models import Usuario
from .. import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')
