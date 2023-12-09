from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.utils import *
from app.db.db import get_db

admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/home', methods=('GET', 'POST'))
@login_required 
def show_home():
    return render_template('admin/admin_home.html')

