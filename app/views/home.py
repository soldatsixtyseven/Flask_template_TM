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
    return render_template('home/index.html', all_courses=all_courses)


# Gestionnaire d'erreur 404 pour toutes les routes inconnues
@home_bp.route('/<path:text>', methods=['GET', 'POST'])
def not_found_error(text):
    return render_template('home/404.html'), 404

# Route /sports
@home_bp.route('/sports', methods=['GET', 'POST'])
def sports_page():
    all_courses = get_all_courses()
    athletisme = get_all_courses("athlétisme")
    course_a_pied = get_all_courses("course à pied")
    marche = get_all_courses("marche")
    hippisme = get_all_courses("hippisme")
    ski_alpin = get_all_courses("ski alpin")
    ski_nordique = get_all_courses("ski nordique")
    triathlon = get_all_courses("triathlon")
    vtt = get_all_courses("VTT")
    autres = get_all_courses("autres")

    return render_template('home/sports.html', all_courses=all_courses,
                           athletisme=athletisme,
                           course_a_pied=course_a_pied, marche=marche,
                           hippisme=hippisme, ski_alpin=ski_alpin,
                           ski_nordique=ski_nordique, triathlon=triathlon,
                           vtt=vtt, autres=autres)

# Route /contact
@home_bp.route('/contact', methods=['GET', 'POST'])
def contact_page():
    return render_template('home/contact.html')

# Route /FAQ
@home_bp.route('/about', methods=['GET', 'POST'])
def about_page():
    return render_template('home/about.html')



