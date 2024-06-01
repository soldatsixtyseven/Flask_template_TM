from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, Response, Flask)
import sqlite3
from ..utils import get_course_details, get_user_birth_year, get_user_info, login_required, get_participant_info, get_participant_birth_year
from app.db.db import get_db, close_db


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
    
@course_bp.route('/information/participant/<int:id_course>/<string:course_name>')
def course_competitor(id_course, course_name):
    # Récupération des détails de la course
    course_details = get_course_details(id_course)

    # Connexion à la base de données
    db = get_db()
    cursor = db.cursor()

    # Récupération des informations des utilisateurs inscrits en ligne
    cursor.execute("""
        SELECT categorie.name, users.name, users.surname, users.sexe, users.club
        FROM users 
        JOIN inscription ON users.id = inscription.user_id
        JOIN categorie ON inscription.categorie_id = categorie.id_categorie
        WHERE categorie.course_id = ?
        ORDER BY categorie.name, users.name, users.surname""", (id_course,))
    
    # Récupération des informations des utilisateurs inscrits en ligne
    liste_competitor_users = cursor.fetchall()

    # Récupération des informations des participants inscrits sur place
    cursor.execute("""
        SELECT categorie.name, participant.name, participant.surname, participant.sexe, participant.club
        FROM participant
        JOIN inscription ON participant.id_participant = inscription.participant_id
        JOIN categorie ON inscription.categorie_id = categorie.id_categorie
        WHERE categorie.course_id = ?
        ORDER BY categorie.name, participant.name, participant.surname""", (id_course,))
    
    # Récupération des informations des participants inscrits sur place
    liste_competitor_participants = cursor.fetchall()

    # Fermeture de la connexion à la base de données
    db.close()

    # Combinaison des deux listes d'inscrits
    liste_competitor = liste_competitor_users + liste_competitor_participants

    # Calcul du nombre total de participants
    total_participants = len(liste_competitor)
    
    # Affichage des informations sur une course dans le template liste_competitor.html
    return render_template('course/liste_competitor.html', 
                           id_course=id_course,    
                           course_name=course_name, 
                           liste_competitor=liste_competitor,                         
                           total_participants=total_participants,
                           date=course_details['date'],
                           location=course_details['location'])


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
        name = request.form['name']
        surname = request.form['surname']
        sexe = request.form['sexe']
        age = request.form['age']
        location = request.form['location']
        origin = request.form['origin']
        club = request.form['club']
        license = request.form['license']

        # Vérifier si tous les champs sont remplis
        if not name or not surname or not sexe or not age or not origin or not location:
            error = 'Veuillez remplir tous les champs.'
            flash(error)
            return redirect(url_for('course_bp.manual_registration', id_course=id_course, course_name=course_name))

        # Insérer l'utilisateur dans la base de données
        db = get_db()
        try:
            db.execute("INSERT INTO participant (name, surname, sexe, age, origin, location, club, license) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (name, surname, sexe, age, origin, location, club, license))
            db.commit()
            # Récupérer l'ID de l'utilisateur inséré
            participant_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
            # Stocker l'ID de l'utilisateur dans la session
            session['participant_id'] = participant_id
        
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
    participant_id = session.get('participant_id')
    participant_info = get_participant_info(participant_id)
    participant_birth_year = int(get_participant_birth_year(participant_info))
    participant_sexe = participant_info['sexe']
    
    if course_details:
        categories = course_details['categories']
        # Filtrer les catégories en fonction de l'année de naissance de l'utilisateur
        filtered_categories = []
        filtered_categories = []
        for category in categories:
            age_min = category.get('year_min')
            age_max = category.get('year_max')
            sexe_categorie = category.get('sexe')
            
            if participant_sexe == 1:
                if sexe_categorie == "f" or sexe_categorie == "i":
                    if age_min == "-" and age_max == "-":
                        filtered_categories.append(category)
                    elif age_min == "-":
                        if participant_birth_year >= int(age_max):
                            filtered_categories.append(category)
                    elif age_max == "-":
                        if participant_birth_year <= int(age_min):
                            filtered_categories.append(category)
                    else:
                        if int(age_min) >= participant_birth_year >= int(age_max):
                            filtered_categories.append(category)
            elif participant_sexe == 2 or participant_sexe == 3:
                if sexe_categorie == "h" or sexe_categorie == "i":
                    if age_min == "-" and age_max == "-":
                        filtered_categories.append(category)
                    elif age_min == "-":
                        if participant_birth_year >= int(age_max):
                            filtered_categories.append(category)
                    elif age_max == "-":
                        if participant_birth_year <= int(age_min):
                            filtered_categories.append(category)
                    else:
                        if int(age_min) >= participant_birth_year >= int(age_max):
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
        elif selected_payment == 'invited':
            return redirect(url_for('payment_bp.invited_payment', id_course=id_course, course_name=course_name, category_name=category_name))
        # Si aucun paiement n'est sélectionne, envoyer un message d'erreur
        else:
            flash("Veuillez sélectionner un moyen de paiement", "error")
            return redirect(url_for('course_bp.manual_payment', id_course=id_course, course_name=course_name, category_name=category_name))
        
    # Récupérer les informations de l'utilisateur comme le nom, le prénom, et l'année de naissance
    participant_id = session.get('participant_id')
    participant_info = get_participant_info(participant_id)
    participant_name = participant_info['name']
    participant_surname = participant_info['surname']
    participant_birth_year = int(get_participant_birth_year(participant_info))

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
                           participant_name=participant_name, user_surname=participant_surname,
                           participant_birth_year=participant_birth_year,
                           participant_location=participant_info['location'],
                           participant_origin=participant_info['origin'],
                           location=course_details['location'],
                           category_start_time=category_details['start_time'],
                           category_price=category_details['price'])

# Création d'un URL dynamique pour la liste des participants depuis la page home.html
@course_bp.route('/liste_inscription/<int:id_course>/<string:course_name>', methods=['GET'])
def liste_inscription(id_course, course_name):
    db = get_db()
    cursor = db.cursor()

    # Sélectionner les données nécessaires, y compris les compteurs
    cursor.execute("""
        SELECT 
            users.name AS user_name,
            users.surname AS user_surname,
            users.age AS user_age,
            users.sexe AS user_sexe,
            users.origin AS user_origin,
            users.location AS user_location,
            users.club AS user_club,
            categorie.name AS category_name,
            categorie.price AS category_price,
            inscription.payment_place AS payment_place,
            inscription.payment_method AS payment_method
        FROM inscription
        JOIN users ON inscription.user_id = users.id
        JOIN categorie ON inscription.categorie_id = categorie.id_categorie
        WHERE categorie.course_id = ?

        UNION ALL

        SELECT 
            participant.name AS participant_name,
            participant.surname AS participant_surname,
            participant.age AS participant_age,
            participant.sexe AS participant_sexe,
            participant.origin AS participant_origin,
            participant.location AS participant_location,
            participant.club AS participant_club,
            categorie.name AS category_name,
            categorie.price AS category_price,
            inscription.payment_place AS payment_place,
            inscription.payment_method AS payment_method
        FROM inscription
        JOIN participant ON inscription.participant_id = participant.id_participant
        JOIN categorie ON inscription.categorie_id = categorie.id_categorie
        WHERE categorie.course_id = ?

        ORDER BY categorie.name, users.name, users.surname""", (id_course, id_course))

    # Récupérer toutes les données et les compteurs
    listes = cursor.fetchall()

    # Compter le nombre total de participants
    total_participants = len(listes)

    # Initialiser les compteurs de paiement
    count_cash = 0
    count_paypal = 0
    count_twint = 0
    count_carte_bancaire = 0
    count_post_finance = 0

    # Initialiser les compteurs de mode d'inscription
    count_on_site = 0
    count_online = 0
    count_guests = 0

    # Parcourir les données pour compter les paiements et les modes d'inscription
    for participant in listes:
        payment_method = participant[10]
        payment_place = participant[9]

        # Compter les paiements
        if payment_method == 'cash':
            count_cash += 1
        elif payment_method == 'paypal':
            count_paypal += 1
        elif payment_method == 'twint':
            count_twint += 1
        elif payment_method == 'carte bancaire':
            count_carte_bancaire += 1
        elif payment_method == 'postfinance':
            count_post_finance += 1
        elif payment_method == 'invited':
            count_guests += 1
        else :
            print("Erreur : donnée invalide pour les données sur les moyens de paiement")

        # Compter les modes d'inscription
        if payment_method != 'invited':
            if payment_place == 2:
                count_on_site += 1
            elif payment_place == 1 :
                count_online += 1
            else:
                print("Erreur : donnée invalide pour les données sur les payments en ligne ou sur place")

    
    # Initialiser les dictionnaires pour les catégories
    category_counts = {}
    payment_counts = {
        'total_cash': 0,
        'total_paypal': 0,
        'total_twint': 0,
        'total_carte_bancaire': 0,
        'total_post_finance': 0,
    }
    total_amount = 0
    
    for participant in listes:
        category_name = participant[7]
        category_price_str = participant[8]
        category_price = float(category_price_str.split()[0])  
        if category_name not in category_counts:
            category_counts[category_name] = {
                'price': participant[8],
                'total': 0,
                'on_site': 0,
                'online': 0,
                'invited': 0,
                'cash': 0,
                'paypal': {'on_site': 0, 'online': 0},
                'twint': {'on_site': 0, 'online': 0},
                'carte_bancaire': 0,
                'post_finance': 0,
                'amount': 0,
                'amount_cash': 0,
                'amount_paypal': {'on_site': 0, 'online': 0},
                'amount_twint': {'on_site': 0, 'online': 0},
                'amount_carte_bancaire': 0,
                'amount_post_finance': 0,
            }

        category_counts[category_name]['total'] += 1
        payment_method = participant[10]
        payment_place = participant[9]

        # Compter les invités
        if payment_method == 'invited':
            category_counts[category_name]['invited'] += 1
        else:
            # Compter les paiements
            if payment_method == 'cash':
                category_counts[category_name]['cash'] += 1
                category_counts[category_name]['amount_cash'] += category_price
                payment_counts['total_cash'] += category_price
            elif payment_method == 'paypal':
                if payment_place == 2:
                    category_counts[category_name]['paypal']['on_site'] += 1
                    category_counts[category_name]['amount_paypal']['on_site'] += category_price
                    payment_counts['total_paypal'] += category_price
                elif payment_place == 1:
                    category_counts[category_name]['paypal']['online'] += 1
                    category_counts[category_name]['amount_paypal']['online'] += category_price
                    payment_counts['total_paypal'] += category_price
            elif payment_method == 'twint':
                if payment_place == 2:
                    category_counts[category_name]['twint']['on_site'] += 1
                    category_counts[category_name]['amount_twint']['on_site'] += category_price
                    payment_counts['total_twint'] += category_price
                elif payment_place == 1:
                    category_counts[category_name]['twint']['online'] += 1
                    category_counts[category_name]['amount_twint']['online'] += category_price
                    payment_counts['total_twint'] += category_price
            elif payment_method == 'carte bancaire':
                category_counts[category_name]['carte_bancaire'] += 1
                category_counts[category_name]['amount_carte_bancaire'] += category_price
                payment_counts['total_carte_bancaire'] += category_price
            elif payment_method == 'postfinance':
                category_counts[category_name]['post_finance'] += 1
                category_counts[category_name]['amount_post_finance'] += category_price
                payment_counts['total_post_finance'] += category_price

            # Compter les modes d'inscription
            if payment_place == 2:
                category_counts[category_name]['on_site'] += 1
            elif payment_place == 1:
                category_counts[category_name]['online'] += 1
            else:
                print("Erreur : donnée invalide pour les données sur les payments en ligne ou sur place")
            # Ajouter au montant des inscriptions pour cette catégorie
            category_counts[category_name]['amount'] += category_price
    
    # Calculer le montant total des inscriptions
    for details in category_counts.values():
        total_amount += details['amount']
            
            
    # Fermer la connexion à la base de données
    db.close()

    # Rediriger vers la page liste_inscription.html avec les informations nécessaires
    return render_template('course/liste_inscription.html', 
                           listes=listes,
                           id_course=id_course, 
                           course_name=course_name,
                           total_participants=total_participants,
                           count_cash=count_cash,
                           count_paypal=count_paypal,
                           count_twint=count_twint,
                           count_carte_bancaire=count_carte_bancaire,
                           count_post_finance=count_post_finance,
                           count_on_site=count_on_site,
                           count_online=count_online,
                           count_guests=count_guests,
                           category_counts=category_counts,
                           total_amount=total_amount,
                           payment_counts=payment_counts)

