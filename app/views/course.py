from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, Response, Flask)
import sqlite3
from ..utils import get_course_details, get_user_birth_year, get_user_info, login_required
from app.db.db import get_db, close_db


import io
from flask import send_file
import xlsxwriter




# Création d'un blueprint contenant les routes ayant le préfixe /course/...
course_bp = Blueprint('course_bp', __name__, url_prefix='/course')

# Création d'un URL dynamique pour une page d'information pour chaque course
@course_bp.route('/information/<int:id_course>/<string:course_name>')
def course_information(id_course, course_name):
    # Récupération de la fonction qui récupère toutes les informations sur les courses
    course_details = get_course_details(id_course)
    
    if course_details:
        categories = course_details['categories']
        return render_template('course/information.html', id_course=id_course, course_name=course_name,
                               club=course_details['club'],
                               date=course_details['date'],
                               location=course_details['location'],
                               canton=course_details['canton'],
                               country=course_details['country'],
                               site_club=course_details['site_club'],
                               flyers=course_details['flyers'],
                               sport=course_details['sport'],
                               categories=categories)
    else:
        # Affichage d'une erreur dans le cas où les détails d'une course ne sont pas trouvés
        flash("Détails de la course non trouvés", "error")
        return redirect(url_for('home_bp.landing_page'))
    
@course_bp.route('/information/user/<int:id_course>/<string:course_name>')
@login_required
def course_information_user(id_course, course_name):

    # Récupération de la fonction qui récupère toutes les informations sur les courses
    course_details = get_course_details(id_course)

    # Récupération de l'année de naissance de l'utilisateur connecté
    user_id = session.get('user_id')
    user_info = get_user_info(user_id)
    user_birth_year = int(get_user_birth_year(user_info))
    
    if course_details:
        categories = course_details['categories']
        # Filtrer les catégories en fonction de l'année de naissance de l'utilisateur
        filtered_categories = []
        for category in categories:
            age_min = category.get('year_min')
            age_max = category.get('year_max')
            
            if age_min == "-" and age_max != "-":
                if user_birth_year <= int(age_max):
                    filtered_categories.append(category)
            elif age_max == "-" and age_min != "-":
                if user_birth_year >= int(age_min):
                    filtered_categories.append(category)
            elif age_min == "-" and age_max == "-":
                filtered_categories.append(category)
            else:
                if int(age_min) <= user_birth_year <= int(age_max):
                    filtered_categories.append(category)

        if not filtered_categories:
            return "Aucune catégorie ne correspond à votre profil"
        else:
            # Retourner les catégories filtrées avec les autres informations de la course
            return render_template('course/user_information.html', id_course=id_course, course_name=course_name,
                                   club=course_details['club'],
                                   date=course_details['date'],
                                   location=course_details['location'],
                                   canton=course_details['canton'],
                                   country=course_details['country'],
                                   site_club=course_details['site_club'],
                                   flyers=course_details['flyers'],
                                   sport=course_details['sport'],
                                   categories=filtered_categories)
        
    else:
        # Affichage d'une erreur dans le cas où les détails d'une course ne sont pas trouvés
        flash("Détails de la course non trouvés", "error")
        return redirect(url_for('course_bp.course_information'))

@course_bp.route('/payment/<int:id_course>/<string:course_name>/<string:category_name>', methods=['GET'])
@login_required
def payment(id_course, course_name, category_name):
    # Vous pouvez ici récupérer les informations de l'utilisateur comme le nom, le prénom, et l'année de naissance
    user_id = session.get('user_id')
    user_info = get_user_info(user_id)
    user_name = user_info['name']
    user_surname = user_info['surname']
    user_birth_year = int(get_user_birth_year(user_info))
    
    # Récupérer les détails de la course et de la catégorie en fonction de id_course et category_name
    course_details = get_course_details(id_course)
    category_details = None
    for category in course_details['categories']:
        if category['name'] == category_name:
            category_details = category
            break

    if not category_details:
        # Gérer l'erreur si la catégorie n'est pas trouvée
        flash("Catégorie introuvable", "error")
        return redirect(url_for('course_bp.user_information', id_course=id_course, name=course_name))

    # Puis rendre le template payment.html avec toutes les informations nécessaires
    return render_template('course/user_payment.html', id_course=id_course, course_name=course_name, category_name=category_name,
                           user_name=user_name, user_surname=user_surname,
                           user_birth_year=user_birth_year,
                           user_location = user_info['location'],
                           user_origin = user_info['origin'],
                           location=course_details['location'],
                           category_start_time=category_details['start_time'],
                           category_price=category_details['price'])

@course_bp.route('/paiement/twint', methods=['POST'])
def paiement_twint():
    return redirect(url_for('home_bp.landing_page'))

@course_bp.route('/paiement/postfinance', methods=['POST'])
def paiement_postfinance():
    return redirect(url_for('home_bp.landing_page'))

@course_bp.route('/paiement/paypal', methods=['POST'])
def paiement_paypal():
    return redirect(url_for('home_bp.landing_page'))

@course_bp.route('/paiement/carte-bancaire', methods=['POST'])
def paiement_carte_bancaire():
    return redirect(url_for('home_bp.landing_page'))

# Création d'un URL dynamique pour l'inscription manuelle de participants depuis la page home.html
@course_bp.route('/inscription_manuelle/<int:id_course>/<string:course_name>', methods=['GET', 'POST'])
def manual_registration(id_course, course_name):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        form_name = request.form['name']
        surname = request.form['surname']
        sexe = request.form['sexe']
        age = request.form['age']
        location = request.form['location']
        origin = request.form['origin']
        club = request.form['club']

        # Vérifier si tous les champs sont remplis
        if not form_name or not surname or not sexe or not age or not origin or not location:
            error = 'Veuillez remplir tous les champs.'
            flash(error)
            return redirect(url_for('course_bp.manual_registration', id_course=id_course, course_name=course_name))

        # Insérer l'utilisateur dans la base de données
        db = get_db()
        try:
            db.execute("INSERT INTO users (name, surname, sexe, age, origin, location, club) VALUES (?, ?, ?, ?, ?, ?, ?)", (form_name, surname, sexe, age, origin, location, club))
            db.commit()
            # Récupérer l'ID de l'utilisateur inséré
            user_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            # Stocker l'ID de l'utilisateur dans la session
            session['user_id'] = user_id
        except db.IntegrityError:
            error = "Une erreur s'est produite."
            flash(error)
            return redirect(url_for('course_bp.manual_registration', id_course=id_course, course_name=course_name))

        # Rediriger vers la page manual_information.html
        return redirect(url_for('course_bp.manual_information', id_course=id_course, course_name=course_name))

    else:
        # Afficher le formulaire d'inscription
        return render_template('course/manual_registration.html', id_course=id_course, course_name=course_name)

# Création d'un URL dynamique pour l'inscription manuelle de participants depuis la page home.html
@course_bp.route('/inscription_manuelle/information/<int:id_course>/<string:course_name>', methods=['GET'])
def manual_information(id_course, course_name):
        # Récupération de la fonction qui récupère toutes les informations sur les courses
    course_details = get_course_details(id_course)

    # Récupération de l'année de naissance de l'utilisateur connecté
    user_id = session.get('user_id')
    user_info = get_user_info(user_id)
    user_birth_year = int(get_user_birth_year(user_info))
    
    if course_details:
        categories = course_details['categories']
        # Filtrer les catégories en fonction de l'année de naissance de l'utilisateur
        filtered_categories = []
        for category in categories:
            age_min = category.get('year_min')
            age_max = category.get('year_max')
            
            if age_min == "-" and age_max != "-":
                if user_birth_year <= int(age_max):
                    filtered_categories.append(category)
            elif age_max == "-" and age_min != "-":
                if user_birth_year >= int(age_min):
                    filtered_categories.append(category)
            elif age_min == "-" and age_max == "-":
                filtered_categories.append(category)
            else:
                if int(age_min) <= user_birth_year <= int(age_max):
                    filtered_categories.append(category)

        if not filtered_categories:
            return "Aucune catégorie ne correspond à votre profil"
        else:
            # Retourner les catégories filtrées avec les autres informations de la course
            return render_template('course/manual_information.html', id_course=id_course, course_name=course_name,
                                   club=course_details['club'],
                                   date=course_details['date'],
                                   location=course_details['location'],
                                   canton=course_details['canton'],
                                   country=course_details['country'],
                                   site_club=course_details['site_club'],
                                   flyers=course_details['flyers'],
                                   sport=course_details['sport'],
                                   categories=filtered_categories)
        
    else:
        # Affichage d'une erreur dans le cas où les détails d'une course ne sont pas trouvés
        flash("Détails de la course non trouvés", "error")
        return redirect(url_for('course_bp.manual_registration', id_course=id_course, course_name=course_name))
    
@course_bp.route('/inscription_manuelle/payment/<int:id_course>/<string:course_name>/<string:category_name>', methods=['GET'])
def manual_payment(id_course, course_name, category_name):
    # Vous pouvez ici récupérer les informations de l'utilisateur comme le nom, le prénom, et l'année de naissance
    user_id = session.get('user_id')
    user_info = get_user_info(user_id)
    user_name = user_info['name']
    user_surname = user_info['surname']
    user_birth_year = int(get_user_birth_year(user_info))
    
    # Récupérer les détails de la course et de la catégorie en fonction de id_course et category_name
    course_details = get_course_details(id_course)
    category_details = None
    for category in course_details['categories']:
        if category['name'] == category_name:
            category_details = category
            break

    if not category_details:
        # Gérer l'erreur si la catégorie n'est pas trouvée
        flash("Catégorie introuvable", "error")
        return redirect(url_for('course_bp.manual_information', id_course=id_course, name=course_name))

    # Puis rendre le template payment.html avec toutes les informations nécessaires
    return render_template('course/manual_payment.html', id_course=id_course, course_name=course_name, category_name=category_name,
                           user_name=user_name, user_surname=user_surname,
                           user_birth_year=user_birth_year,
                           user_location = user_info['location'],
                           user_origin = user_info['origin'],
                           location=course_details['location'],
                           category_start_time=category_details['start_time'],
                           category_price=category_details['price'])

# Création d'un URL dynamique pour la liste des participants depuis la page home.html
@course_bp.route('/liste_inscription/<int:id_course>/<string:course_name>', methods=['GET'])
def liste_inscription(id_course, course_name):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
                   SELECT categorie.name, users.age, users.name, users.surname, users.sexe, users.location, users.origin, users.club
                   FROM users 
                   JOIN inscription ON users.id = inscription.users_id
                   JOIN categorie ON inscription.categorie_id = categorie.id_categorie
                   JOIN course ON categorie.course_id = course.id_course
                   WHERE course.id_course = ?
                   ORDER BY categorie.name, users.name, users.surname""", (id_course,))

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

    return render_template('course/liste_inscription.html', listes=listes, id_course=id_course, course_name=course_name)

@course_bp.route('/export_excel/<int:id_course>', methods=['POST'])
def export_excel(id_course):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
                   SELECT categorie.name, users.age, users.name, users.surname, users.sexe, users.location, users.origin, users.club
                   FROM users 
                   JOIN inscription  ON users.id = inscription.users_id
                   JOIN categorie  ON inscription.categorie_id = categorie.id_categorie
                   JOIN course ON categorie.course_id = course.id_course
                   WHERE course.id_course = ?
                   ORDER BY categorie.name, users.name, users.surname""", (id_course,))

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


