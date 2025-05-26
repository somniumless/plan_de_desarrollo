from flask import Blueprint, render_template
from ..models import Meta
from .. import db

metas = Blueprint('metas', __name__)

@metas.route('/')
def dashboard():
    metas = Meta.query.all()
    return render_template('dashboard.html', metas=metas)
