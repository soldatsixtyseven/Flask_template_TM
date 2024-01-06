from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# Fonction pour récupérer les détails d'une course spécifique depuis la base de données
def get_course_details(course_id):
    # Connexion à la base de données SQLite
    conn = sqlite3.connect('SportLog.db')
    cursor = conn.cursor()

    # Exécution d'une requête SQL pour récupérer les détails de la course avec l'ID spécifié
    cursor.execute('SELECT * FROM course WHERE id = ?', (course_id,))
    course_data = cursor.fetchone()

    # Fermeture de la connexion à la base de données
    conn.close()

    return course_data

# Route pour la page d'information de la course
@app.route('/course/<course_id>/information')
def course_information(course_id):
    # Logique pour récupérer les données de la base de données pour la course
    course_data = get_course_details(course_id)
    # ...

    return render_template('course/information.html', course_data=course_data)

# Route pour la page de paiement de la course
@app.route('/course/<course_id>/paiement')
def course_paiement(course_id):
    # Logique pour récupérer les données de la base de données pour la course
    course_data = get_course_details(course_id)
    # ...

    return render_template('course/paiement.html', course_data=course_data)

if __name__ == '__main__':
    app.run(debug=True)