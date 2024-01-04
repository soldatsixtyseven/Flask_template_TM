from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.db.db import get_db
from app.utils import login_required
import os


admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

# Route /admin/home
@admin_bp.route('/home', methods=('GET', 'POST'))
@login_required 
def admin_show_home():
    return render_template('admin/home.html')

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
            session['admin_id'] = admin['id']
            # On redirige l'administrateur vers la page admin_home.html une fois qu'il s'est connecté
            return redirect(url_for('admin_bp.admin_show_home'))
        else:
            # En cas d'erreur, on ajoute l'erreur dans la session et on redirige l'utilisateur vers le formulaire de login
            flash(error)
            return redirect(url_for('admin_bp.login_admin'))
    else:
        return render_template('admin/admin.html')

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
        g.user = db.execute('SELECT * FROM admin WHERE id = ?', (admin_id,)).fetchone()

    
# Route /admin/creation
@admin_bp.route('/creation', methods=('GET', 'POST'))
def creation():
    # Si des données de formulaire sont envoyées vers la route /creation (ce qui est le cas lorsque le formulaire d'inscription est envoyé)
    if request.method == 'POST':
        # On récupère les données du formulaire
        club = request.form['club']
        name = request.form['name']
        date = request.form['date']
        sport = request.form['sport']
        location = request.form['location']
        origin = request.form['origin']
        image = request.form['image']
        course = request.form['course']

        if not name or not date or not sport or not location or not origin or not image or not course:
            error = 'Veuillez remplir tous les champs.'
            flash(error)
            return redirect(url_for('admin_bp.creation'))

        # On récupère la base de données
        db = get_db()

        # Si le nom et la date ont bien une valeur,
        # on essaie d'insérer la course dans la base de données
        if name and date:
            try:
                db.execute("INSERT INTO courses (name, date, sport, location, origin, image, course) VALUES (?, ?, ?, ?, ?, ?, ?)", (name, date, sport, location, origin, image, course))
                # db.commit() permet de valider une modification de la base de données
                db.commit()

                return redirect(url_for("admin_bp.admin_show_home"))
            except:
                error = "Une erreur s'est produite lors de la création de la course."
                flash(error)
                return redirect(url_for("admin_bp.creation"))
        else:
            error = "Veuillez fournir un nom et une date valides."
            flash(error)
            return redirect(url_for("admin_bp.creation"))
    else:
        # Si aucune donnée de formulaire n'est envoyée, on affiche le formulaire de création de course
        return render_template('admin/creation.html')
    
# Route /admin/liste
@admin_bp.route('/liste', methods=['GET', 'POST'])
def liste_page():
    return render_template('admin/liste.html')

# Route /admin/inscription
@admin_bp.route('/inscription', methods=['GET', 'POST'])
def inscription():
    return render_template('admin/inscritpion.html')