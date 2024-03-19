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
    
    # Envoyer toutes les informations sur une course au template information.html
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

# Création d'un URL dynamique pour une page d'information pour chaque course qui sélectionne les catégories auxquelles un utilisateur peut s'inscrire par son âge
@course_bp.route('/information/user/<int:id_course>/<string:course_name>')
@login_required
def course_information_user(id_course, course_name):

    # Récupération de la fonction qui récupère toutes les informations sur les courses
    course_details = get_course_details(id_course)

    # Récupération de l'année de naissance et du sexe de l'utilisateur connecté
    user_id = session.get('user_id')
    user_info = get_user_info(user_id)
    user_sexe = user_info['sexe']
    user_birth_year = int(get_user_birth_year(user_info))

    if course_details:
        categories = course_details['categories']
        
        # Filtrer les catégories en fonction du sexe de l'utilisateur
        filtered_categories = []
        for category in categories:
            age_min = category.get('year_min')
            age_max = category.get('year_max')
            sexe_categorie = category.get('sexe')
            
            if user_sexe == 1:
                if sexe_categorie == "f" or sexe_categorie == "i":
                    if age_min == "-" and age_max == "-":
                        filtered_categories.append(category)
                    elif age_min == "-":
                        if user_birth_year >= int(age_max):
                            filtered_categories.append(category)
                    elif age_max == "-":
                        if user_birth_year <= int(age_min):
                            filtered_categories.append(category)
                    else:
                        if int(age_min) >= user_birth_year >= int(age_max):
                            filtered_categories.append(category)
            elif user_sexe == 2 or user_sexe == 3:
                if sexe_categorie == "h" or sexe_categorie == "i":
                    if age_min == "-" and age_max == "-":
                        filtered_categories.append(category)
                    elif age_min == "-":
                        if user_birth_year >= int(age_max):
                            filtered_categories.append(category)
                    elif age_max == "-":
                        if user_birth_year <= int(age_min):
                            filtered_categories.append(category)
                    else:
                        if int(age_min) >= user_birth_year >= int(age_max):
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

# Création d'un URL dynamique pour une page de paiement en ligne pour les utilisateurs
@course_bp.route('/payment/<int:id_course>/<string:course_name>/<string:category_name>', methods=['GET', 'POST'])
@login_required
def user_payment(id_course, course_name, category_name):
    # Récupérer le moyen de paiement sélectionné dans le formulaire
    if request.method == 'POST':
        selected_payment = request.form.get('payment')

        # Récupérer le moyen de paiement sélectionné dans le formulaire
        if selected_payment is None:
            flash("Veuillez choisir un moyen de paiement", "error")
            return redirect(url_for('course_bp.user_payment', id_course=id_course, course_name=course_name, category_name=category_name))

        # Récupérer les détails de la course et de la catégorie en fonction de id_course et category_name
        course_details = get_course_details(id_course)
        
        # Rechercher les informations sur la catégorie choisie
        category_details = None
        for category in course_details['categories']:
            if category['name'] == category_name:
                category_details = category
                break

        if not category_details:
            # Gérer l'erreur si la catégorie n'est pas trouvée
            flash("Catégorie introuvable", "error")
            return redirect(url_for('course_bp.course_information_user', id_course=id_course, course_name=course_name))

        # Rediriger en fonction du moyen de paiement sélectionné
        if selected_payment == 'twint':
            return redirect(url_for('payment_bp.twint_payment_user', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_details['price']))
        elif selected_payment == 'postfinance':
            return redirect(url_for('payment_bp.postfinance_payment_user', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_details['price']))
        elif selected_payment == 'paypal':
            return redirect(url_for('payment_bp.paypal_payment_user', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_details['price']))
        elif selected_payment == 'carte_bancaire':
            return redirect(url_for('payment_bp.bank_card_payment_user', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_details['price']))
        # Si aucun paiement n'est sélectionne, envoyer un message d'erreur
        else:
            flash("Veuillez sélectionner un moyen de paiement", "error")
            return redirect(url_for('course_bp.user_payment', id_course=id_course, course_name=course_name, category_name=category_name))
        
    # Récupérer les informations de l'utilisateur comme le nom, le prénom, et l'année de naissance
    user_id = session.get('user_id')
    user_info = get_user_info(user_id)
    user_name = user_info['name']
    user_surname = user_info['surname']
    user_birth_year = int(get_user_birth_year(user_info))

    # Récupérer les détails de la course pour afficher les informations nécessaires
    course_details = get_course_details(id_course)

    # Rechercher les informations sur la catégorie choisie
    category_details = None
    for category in course_details['categories']:
        if category['name'] == category_name:
            category_details = category
            break

    if not category_details:
        # Gérer l'erreur si la catégorie n'est pas trouvée
        flash("Catégorie introuvable", "error")
        return redirect(url_for('course_bp.course_information_user', id_course=id_course, course_name=course_name))

    # Rediriger vers la page user_payment.html avec les informations nécessaires
    return render_template('course/user_payment.html', id_course=id_course, course_name=course_name, category_name=category_name,
                           user_name=user_name, user_surname=user_surname,
                           user_birth_year=user_birth_year,
                           user_location=user_info['location'],
                           user_origin=user_info['origin'],
                           location=course_details['location'],
                           category_start_time=category_details['start_time'],
                           category_price=category_details['price'])

# Création d'un URL dynamique pour l'inscription manuelle de participants depuis la page home.html
@course_bp.route('/inscription/<int:id_course>/<string:course_name>', methods=['GET', 'POST'])
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
        
        # Afficher un message d'erreur en cas de problème
        except db.IntegrityError:
            error = "Une erreur s'est produite."
            flash(error)
            return redirect(url_for('course_bp.manual_registration', id_course=id_course, course_name=course_name))

        # Rediriger vers la page manual_information.html avec les informations nécessaire
        return redirect(url_for('course_bp.manual_information', id_course=id_course, course_name=course_name))

    else:
        # En cas d'erreur, afficher le formulaire d'inscription
        return render_template('course/manual_registration.html', id_course=id_course, course_name=course_name)

# Création d'un URL dynamique pour l'inscription manuelle de participants depuis la page home.html
@course_bp.route('/inscription/information/<int:id_course>/<string:course_name>', methods=['GET'])
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
            # Rediriger vers la page manual_information.html avec les informations nécessaires
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
    
@course_bp.route('/inscription/payment/<int:id_course>/<string:course_name>/<string:category_name>', methods=['GET', 'POST'])
def manual_payment(id_course, course_name, category_name):
    # Récupérer le moyen de paiement sélectionné dans le formulaire
    if request.method == 'POST':
        selected_payment = request.form.get('payment')

        # Récupérer le moyen de paiement sélectionné dans le formulaire
        if selected_payment is None:
            flash("Veuillez choisir un moyen de paiement", "error")
            return redirect(url_for('course_bp.manual_payment', id_course=id_course, course_name=course_name, category_name=category_name))

        # Récupérer les détails de la course et de la catégorie en fonction de id_course et category_name
        course_details = get_course_details(id_course)
        
        # Rechercher les informations sur la catégorie choisie
        category_details = None
        for category in course_details['categories']:
            if category['name'] == category_name:
                category_details = category
                break

        if not category_details:
            # Gérer l'erreur si la catégorie n'est pas trouvée
            flash("Catégorie introuvable", "error")
            return redirect(url_for('course_bp.manual_payment', id_course=id_course, course_name=course_name))

        # Rediriger en fonction du moyen de paiement sélectionné
        if selected_payment == 'twint':
            return redirect(url_for('payment_bp.twint_manual_payment', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_details['price']))
        elif selected_payment == 'paypal':
            print(1)
            return redirect(url_for('payment_bp.paypal_manual_payment', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_details['price']))
        elif selected_payment == 'cash':
            return redirect(url_for('payment_bp.cash_manual_payment', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_details['price']))
        # Si aucun paiement n'est sélectionne, envoyer un message d'erreur
        else:
            flash("Veuillez sélectionner un moyen de paiement", "error")
            return redirect(url_for('course_bp.manual_payment', id_course=id_course, course_name=course_name, category_name=category_name))
        
    # Récupérer les informations de l'utilisateur comme le nom, le prénom, et l'année de naissance
    user_id = session.get('user_id')
    user_info = get_user_info(user_id)
    user_name = user_info['name']
    user_surname = user_info['surname']
    user_birth_year = int(get_user_birth_year(user_info))

    # Récupérer les détails de la course pour afficher les informations nécessaires
    course_details = get_course_details(id_course)

    # Rechercher les informations sur la catégorie choisie
    category_details = None
    for category in course_details['categories']:
        if category['name'] == category_name:
            category_details = category
            break

    if not category_details:
        # Gérer l'erreur si la catégorie n'est pas trouvée
        flash("Catégorie introuvable", "error")
        return redirect(url_for('course_bp.manual_payment', id_course=id_course, course_name=course_name, category_name=category_name))

    # Rediriger vers la page manual_payment.html avec toutes les informations nécessaires
    return render_template('course/manual_payment.html', id_course=id_course, course_name=course_name, category_name=category_name,
                           user_name=user_name, user_surname=user_surname,
                           user_birth_year=user_birth_year,
                           user_location=user_info['location'],
                           user_origin=user_info['origin'],
                           location=course_details['location'],
                           category_start_time=category_details['start_time'],
                           category_price=category_details['price'])

# Création d'un URL dynamique pour la liste des participants depuis la page home.html
@course_bp.route('/liste_inscription/<int:id_course>/<string:course_name>', methods=['GET'])
def liste_inscription(id_course, course_name):
    db = get_db()
    cursor = db.cursor()

    # Croiser les liens entre les tables "users", "course", "categorie" et "inscription" pour afficher toutes les utilisateurs inscrits dans une même course avec leurs informations personnelles et la catégorie choisie
    cursor.execute("""
                   SELECT categorie.name, users.age, users.name, users.surname, users.sexe, users.location, users.origin, users.club
                   FROM users 
                   JOIN inscription ON users.id = inscription.users_id
                   JOIN categorie ON inscription.categorie_id = categorie.id_categorie
                   JOIN course ON categorie.course_id = course.id_course
                   WHERE course.id_course = ?
                   ORDER BY categorie.name, users.name, users.surname""", (id_course,))
    
    # Regroupe toutes ses informations dans une variable listes
    listes = cursor.fetchall()
    db.close()

    # Rediriger vers la page liste_inscription.html avec les informations nécessaires
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


