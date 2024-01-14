from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, Response, Flask)
import sqlite3
from ..utils import get_all_courses
from app.db.db import get_db

# Création d'un blueprint contenant les routes ayant le préfixe /course/...
course_bp = Blueprint('course', __name__, url_prefix='/course')

# Fonction pour récupérer les détails d'une course spécifique depuis la base de données
def get_course_details(course_id):
    # Connexion à la base de données SQLite
    db=get_db()

    # Exécution d'une requête SQL pour récupérer les détails de la course avec l'ID spécifié
    course_data = db.execute('SELECT id_course, name, date, sport, club, site_club, location, canton, country, carte FROM course WHERE id_course = ?', (course_id,)).fetchone()
    return dict(course_data) if course_data else None


# Fonction pour récupérer toutes les courses
def get_all_courses():
    db = get_db()
    all_courses = [dict(row) for row in db.execute('SELECT id_course, name, date, sport, club, site_club, location, canton, country, carte FROM course').fetchall()]
    return all_courses

@course_bp.route('/')
def all_courses():
    all_courses = get_all_courses()
    return render_template('course/index.html', all_courses=all_courses)

@course_bp.route('/<int:id_course>-<name>/information')
def course_information(id_course, name):
    db = get_db()
    course_data = db.execute('SELECT * FROM course WHERE id_course = ?', (id_course,)).fetchone()

    if course_data:
        course_data = dict(course_data)
        return render_template('course/information.html', course_data=course_data, course_name=name)

    return render_template('404.html', message="Course not found")

