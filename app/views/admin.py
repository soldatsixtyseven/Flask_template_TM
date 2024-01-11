from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.db.db import get_db
from app.utils import login_required
import os

# Création d'un blueprint contenant les routes ayant le préfixe /admin/...
admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

# Route /admin/home
@admin_bp.route('/home', methods=('GET', 'POST'))
@login_required 
def admin_show_home():
    return render_template('admin/admin_home.html')

# Route /admin/login
@admin_bp.route('/login', methods=['GET', 'POST'])
def login_admin():
    # Si des données de formulaire sont envoyées vers la route /admin (ce qui est le cas lorsque le formulaire de login est envoyé)
    if request.method == 'POST':
        # On récupère les champs 'username' et 'password' de la requête HTTP
        username = request.form['username']
        password = request.form['password']
        
        # On récupère la base de données
        db = get_db()

        # On récupère l'administrateur avec l'username spécifié
        admin = db.execute('SELECT * FROM admin WHERE username = ?', (username,)).fetchone()

        error = None
        if admin is None:
            error = 'Identifiant incorrect.'
        elif admin['mdp'] != password:
            error = 'Mot de passe incorrect.'

        # S'il n'y a pas d'erreur, on ajoute l'id de l'administrateur dans une variable de session
        # De cette manière, à chaque requête de l'utilisateur, on pourra récupérer l'id dans le cookie session
        if error is None:
            session.clear()
            session['admin_id'] = admin['id_admin']
            # On redirige l'administrateur vers la page admin_home.html une fois qu'il s'est connecté
            return redirect(url_for('admin_bp.admin_show_home'))
        else:
            # En cas d'erreur, on ajoute l'erreur dans la session et on redirige l'utilisateur vers le formulaire de login
            flash(error)
            return redirect(url_for('admin_bp.login_admin'))
    else:
        return render_template('admin/admin_login.html')

# Route /auth/logout
@admin_bp.route('/logout')
def logout_admin():
    # Se déconnecter consiste simplement à supprimer le cookie session
    session.clear()

    # On redirige l'utilisateur vers la page principale une fois qu'il s'est déconnecté
    return redirect("/")

# Fonction automatiquement appelée à chaque requête (avant d'entrer dans la route) sur une route appartenant au blueprint 'auth_bp'
# La fonction permet d'ajouter un attribut 'user' représentant l'utilisateur connecté dans l'objet 'g'
@admin_bp.before_app_request
def load_logged_in_user():
    # On récupère l'id de l'administrateur stocké dans le cookie session
    admin_id = session.get('admin_id')

    # Si l'id de l'administrateur dans le cookie session est nul, cela signifie que l'administrateur n'est pas connecté
    # On met donc l'attribut 'user' de l'objet 'g' à None
    if admin_id is None:
        g.user = None
    # Si l'id de l'administrateur dans le cookie session n'est pas nul, on récupère l'administrateur correspondant et on stocke
    # l'administrateur comme un attribut de l'objet 'g'
    else:
        # On récupère la base de données et on récupère l'administrateur correspondant à l'id stocké dans le cookie session
        db = get_db()
        g.user = db.execute('SELECT * FROM admin WHERE id_admin = ?', (admin_id,)).fetchone()

    
# Route /admin/creation
@admin_bp.route('/creation', methods=('GET', 'POST'))
def creation():

    print("DATA RECEIVED")
    print(request.form)


    # Si des données de formulaire sont envoyées vers la route /creation (ce qui est le cas lorsque le formulaire d'inscription est envoyé)
    if request.method == 'POST':
        # On récupère les données de la course
        name = request.form['name']
        date = request.form['date']
        sport = request.form['sport']
        club = request.form['club']
        site_club = request.form['site_club']
        location = request.form['location']
        canton = request.form['canton']
        country = request.form['country']
        carte = request.files['carte'].read()

        # On récupère les données de chaque catérogie
        category_names = request.form.getlist('category_name[]')
        year = request.form.getlist('year[]')
        start_times = request.form.getlist('start_time[]')
        prices = request.form.getlist('price[]')
        distances = request.form.getlist('distance[]')
        ascent = request.form.getlist('ascent[]')
        descent = request.form.getlist('descent[]')
        
        print(category_names, year, start_times, prices, distances, ascent, descent)


        if not name or not date or not sport or not club or not location or not country :
            error = 'Veuillez remplir tous les champs.'
            flash(error)
            print("3")
            return redirect(url_for('admin_bp.creation'))
            

        # On récupère la base de données
        print("4")
        db = get_db()
        cursor = db.cursor()

        # Si le nom et la date ont bien une valeur,
        # on essaie d'insérer la course dans la base de données
        if name and date:
            print("5")
            try:
                cursor.execute("INSERT INTO course (name, date, sport, club, site_club, location, canton, country, carte) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, date, sport, club, site_club, location, canton, country, carte))
                # db.commit() permet de valider une modification de la base de données
                db.commit()
                print("6")

                # db.lastrowid permet de récupérer l'ID de la course récemment enregister pour l'attribuer aux catégories
                course_id = cursor.lastrowid

                for i in range(len(category_names)):
                    cursor.execute("INSERT INTO categorie (course_id, name, year, start_time, price, distance, ascent, descent) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (course_id, category_names[i], year[i], start_times[i], prices[i], distances[i], ascent[i], descent[i]))
                    db.commit()
                    print("7")

                return redirect(url_for("admin_bp.admin_show_home"))
            
            except Exception as e:
                print(e)
                print("9")
                error = "Une erreur s'est produite lors de la création de la course."
                flash(error)
                return redirect(url_for("admin_bp.creation"))
        else:
            print("10")
            error = "Veuillez fournir un nom et une date valides."
            flash(error)
            return redirect(url_for("admin_bp.creation"))

    else:
        print("11")
        # Si aucune donnée de formulaire n'est envoyée, on affiche le formulaire de création de course
        return render_template('admin/creation_course.html')
    
# Route /admin/liste
@admin_bp.route('/liste', methods=['GET', 'POST'])
def liste_page():
    return render_template('admin/participants_course.html')

# Route /admin/inscription
@admin_bp.route('/inscription', methods=['GET', 'POST'])
def inscription():
    return render_template('admin/inscription_course.html')

# Route /admin/paiement
@admin_bp.route('/paiement', methods=['GET', 'POST'])
def payment():
    return render_template('admin/payment.html')