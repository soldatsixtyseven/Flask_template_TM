from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, Response, Flask)
import sqlite3
from ..utils import get_course_details
from app.db.db import get_db


import io
from flask import send_file
import xlsxwriter




# Création d'un blueprint contenant les routes ayant le préfixe /course/...
course_bp = Blueprint('course_bp', __name__, url_prefix='/course')

# Création d'un URL dynamique pour une page d'information pour chaque course
@course_bp.route('/course/information/<int:id_course>/<string:name>')
def course_information(id_course, name):
    # Récupération de la fonction qui récupère toutes les informations sur les courses
    course_details = get_course_details(id_course)
    
    if course_details:
        categories = course_details['categories']
        return render_template('course/information.html', id_course=id_course, name=name,
                               club=course_details['club'],
                               date=course_details['date'],
                               location=course_details['location'],
                               canton=course_details['canton'],
                               country=course_details['country'],
                               site_club=course_details['site_club'],
                               flyers=course_details['flyers'],
                               categories=categories)
    else:
        # Affichage d'une erreur dans le cas où les détails d'une course ne sont pas trouvés
        flash("Détails de la course non trouvés", "error")
        return redirect(url_for('home_bp.landing_page'))

# Création d'un URL dynamique pour l'inscription manuelle de participants depuis la page home.html
@course_bp.route('/inscription_manuelle/<int:course_id>/<string:course_name>', methods=['GET'])
def manual_registration(course_id, course_name):

    return render_template('course/manual_registration.html', course_id=course_id, course_name=course_name)

# Création d'un URL dynamique pour la liste des participants depuis la page home.html
@course_bp.route('/liste_inscription/<int:course_id>/<string:course_name>', methods=['GET'])
def liste_inscription(course_id, course_name):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
                   SELECT categorie.name, users.age, users.name, users.surname, users.sexe, users.location, users.origin, users.club
                   FROM users 
                   JOIN inscription ON users.id = inscription.users_id
                   JOIN categorie ON inscription.categorie_id = categorie.id_categorie
                   JOIN course ON categorie.course_id = course.id_course
                   WHERE course.id_course = ?
                   ORDER BY categorie.name, users.name, users.surname""", (course_id,))

    listes = cursor.fetchall()
    db.close()
    
    # Affichage des résultats
    for resultat in listes:
        nom_categorie = resultat[0]
        age = resultat[1]
        nom = resultat[2]
        prenom = resultat[3]
        sexe = resultat[4]
        location = resultat[5]
        origin = resultat[6]
        club = resultat[7]
        print(f"Catégorie: {nom_categorie}, Age: {age}, Nom: {nom}, Prénom: {prenom}, Sexe: {sexe}, Lieu: {location}, Origine: {origin}, Club: {club}")

    return render_template('course/liste_inscription.html', listes=listes, course_id=course_id, course_name=course_name)


@course_bp.route('/export_excel/<int:course_id>', methods=['POST'])
def export_excel(course_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
                   SELECT categorie.name, users.age, users.name, users.surname, users.sexe, users.location, users.origin, users.club
                   FROM users 
                   JOIN inscription  ON users.id = inscription.users_id
                   JOIN categorie  ON inscription.categorie_id = categorie.id_categorie
                   JOIN course ON categorie.course_id = course.id_course
                   WHERE course.id_course = ?
                   ORDER BY categorie.name, users.name, users.surname""", (course_id,))

    listes = cursor.fetchall()
    db.close()

    # Création du fichier Excel
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Écriture des en-têtes
    headers = ["Catégorie", "Année de naissance", "Nom", "Prénom", "Sexe", "Localité", "Origine", "Club"]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
    
    # Écriture des données
    for row, participant in enumerate(listes, start=1):
        for col, value in enumerate(participant):
            worksheet.write(row, col, value)
    
    workbook.close()
    
    # Configuration de la réponse pour le téléchargement
    output.seek(0)
    return send_file(output, attachment_filename="liste_participants.xlsx", as_attachment=True)



# Création d'un URL dynamique pour une page d'information pour chaque course
@course_bp.route('/course/<int:id_course>/<string:name>/user')
def course_user_information(id_course, name):
    # Récupération de la fonction qui récupère toutes les informations sur les courses
    course_details = get_course_details(id_course)
    
    if course_details:
        categories = course_details['categories']
        return render_template('course/information/user_information.html', id_course=id_course, name=name,
                               club=course_details['club'],
                               date=course_details['date'],
                               location=course_details['location'],
                               canton=course_details['canton'],
                               country=course_details['country'],
                               site_club=course_details['site_club'],
                               flyers=course_details['flyers'],
                               categories=categories)
    else:
        # Affichage d'une erreur dans le cas où les détails d'une course ne sont pas trouvés
        flash("Détails du cours non trouvés", "error")
        return redirect(url_for('home_bp.landing_page'))

