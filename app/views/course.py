from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, Response, Flask)
import sqlite3
from ..utils import get_all_courses
from app.db.db import get_db

# Création d'un blueprint contenant les routes ayant le préfixe /course/...
course_bp = Blueprint('course', __name__, url_prefix='/course')

# Fonction pour récupérer les détails d'une course spécifique depuis la base de données
def get_course_details():
    # Connexion à la base de données SQLite
    db=get_db()

    # Exécution d'une requête SQL pour récupérer les détails de la course avec l'ID spécifié
    course_data=db.execute('SELECT name, sport, date, location, canton, carte, description, categorie_id FROM course').fetchone()
    

    # Fermeture de la connexion à la base de données

    return course_data

@course_bp.route('/<int:course_id>-<course_name>/information')
def course_information(course_id, course_name):
    # Logique pour récupérer les données de la base de données pour la course
    course_data = get_course_details(course_id)
    # ...

    return render_template('course/information.html', course_data=course_data, course_name=course_name)

# Route pour la page de paiement de la course
@course_bp.route('/course/<int:course_id>-<course_name>/paiement')
def course_paiement(course_id, course_name):
    # Logique pour récupérer les données de la base de données pour la course
    course_data = get_course_details(course_id)
    # ...

    return render_template('course/paiement.html', course_data=course_data, course_name=course_name)

@course_bp.route('/')
def all_courses():
    # Récupérez toutes les courses
    all_courses = get_all_courses()

    return render_template('home/index.html', all_courses=all_courses)
