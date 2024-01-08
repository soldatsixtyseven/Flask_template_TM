from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, Response, Flask)
import sqlite3
from ..utils import get_all_courses

# Routes /...
home_bp = Blueprint('home', __name__)

# Route /
@home_bp.route('/', methods=('GET', 'POST'))
def landing_page():
    # Récupérez toutes les courses
    all_courses = get_all_courses()

    return render_template('home/index.html', course_data=all_courses)


# Gestionnaire d'erreur 404 pour toutes les routes inconnues
@home_bp.route('/<path:text>', methods=['GET', 'POST'])
def not_found_error(text):
    return render_template('home/404.html'), 404

# Route /sports
@home_bp.route('/sports', methods=['GET', 'POST'])
def sports_page():
    return render_template('home/sports.html')

# Route /contact
@home_bp.route('/contact', methods=['GET', 'POST'])
def contact_page():
    return render_template('home/contact.html')



