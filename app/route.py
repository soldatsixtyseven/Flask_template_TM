from flask import Flask, render_template
import sqlite3
from utils import get_all_courses

app = Flask(__name__)

# Fonction pour récupérer les détails d'une course spécifique depuis la base de données
def get_course_details(course_id):
    # Connexion à la base de données SQLite
    conn = sqlite3.connect('SportLog.db')
    cursor = conn.cursor()

    # Exécution d'une requête SQL pour récupérer les détails de la course avec l'ID spécifié
    cursor.execute('SELECT name, sport, date, location, canton, carte, description, categorie_id FROM course WHERE id = ?', (course_id,))
    course_data = cursor.fetchone()

    # Fermeture de la connexion à la base de données
    conn.close()

    return course_data

@app.route('/course/<int:course_id>-<course_name>/information')
def course_information(course_id, course_name):
    # Logique pour récupérer les données de la base de données pour la course
    course_data = get_course_details(course_id)
    # ...

    return render_template('course/information.html', course_data=course_data, course_name=course_name)

# Route pour la page de paiement de la course
@app.route('/course/<int:course_id>-<course_name>/paiement')
def course_paiement(course_id, course_name):
    # Logique pour récupérer les données de la base de données pour la course
    course_data = get_course_details(course_id)
    # ...

    return render_template('course/paiement.html', course_data=course_data, course_name=course_name)

@app.route('/courses')
def all_courses():
    # Récupérez toutes les courses
    all_courses = get_all_courses()

    return render_template('home/index.html', all_courses=all_courses)

if __name__ == '__main__':
    app.run(debug=True)