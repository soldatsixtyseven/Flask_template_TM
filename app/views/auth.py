from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db.db import get_db
from app.utils import login_required, check_session_expiration
import os

# Création d'un blueprint contenant les routes ayant le préfixe /auth/...
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Route /auth/register
@auth_bp.route('/register', methods=('GET', 'POST'))
def register():
    # Si des données de formulaire sont envoyées vers la route /register (ce qui est le cas lorsque le formulaire d'inscription est envoyé)
    if request.method == 'POST':
        # On récupère les données du formulaire
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        telephone = request.form['telephone']
        sexe = request.form['sexe']
        age = request.form['age']
        origin = request.form['origin']
        location = request.form['location']
        club = request.form['club']
        license = request.form['license']
        mdp = request.form['mdp']
        mdp_confirm = request.form['mdp_confirm']

        if not name or not surname or not email or not telephone or not sexe or not age or not origin or not location or not mdp or not mdp_confirm:
            error = 'Veuillez remplir tous les champs.'
            flash(error)
            return redirect(url_for('auth.register'))

        # Contrôle que les mots de passe sont identiques
        if mdp != mdp_confirm:
            error = 'Les mots de passe ne correspondent pas.'
            flash(error)
            return redirect(url_for('auth.register'))

        # On récupère la base de données
        db = get_db()

        # Si l'email et le mot de passe ont bien une valeur
        # on essaie d'insérer l'utilisateur dans la base de données
        if email and mdp:
            try:
                db.execute("INSERT INTO users (name, surname, email, telephone, sexe, age, origin, location, club, license, mdp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, surname, email, telephone, sexe, age, origin, location, club, license, generate_password_hash(mdp)))
                # db.commit() permet de valider une modification de la base de données
                db.commit()
            except db.IntegrityError:
                # La fonction flash dans Flask est utilisée pour stocker un message dans la session de l'utilisateur
                # dans le but de l'afficher ultérieurement, généralement sur la page suivante après une redirection
                error = f"L'utilisateur {email} est déjà enregistré."
                flash(error)
                return redirect(url_for("auth.register"))

            return redirect(url_for("auth.login"))
        else:
            error = "Email ou mot de passe invalide"
            flash(error)
            return redirect(url_for("auth.login"))
    else:
        # Si aucune donnée de formulaire n'est envoyée, on affiche le formulaire d'inscription
        return render_template('auth/register.html')

# Route /auth/login
@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    # Si des données de formulaire sont envoyées vers la route /login (ce qui est le cas lorsque le formulaire de login est envoyé)
    if request.method == 'POST':
        # On récupère les champs 'email' et 'password' de la requête HTTP
        email = request.form['email']  
        password = request.form['password']

        # On récupère la base de données
        db = get_db()

        # On récupère l'utilisateur avec l'email spécifié (une contrainte dans la db indique que le nom d'utilisateur est unique)
        # La virgule après email est utilisée pour créer un tuple contenant une valeur unique
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        # Si aucun utilisateur n'est trouvé ou si le mot de passe est incorrect
        # On crée une variable error
        error = None
        if user is None:
            error = 'Email incorrect.'
            flash(error)
            return redirect(url_for("auth.login"))
        
        if not check_password_hash(user['mdp'], password):
            error = 'Mot de passe incorrect.'
            flash(error)
            return redirect(url_for("auth.login"))
        
        # Si l'utilisateur n'a pas encore défini son mot de passe car il a été inscrit précédemment manuellement
        if not user['mdp']:
            session.clear()
            session['user_id'] = user['id']
            # On redirige vers la page de définition du mot de passe
            return redirect(url_for('auth_bp.set_password'))

        # S'il n'y a pas d'erreur, on ajoute l'id de l'utilisateur dans une variable de session
        # De cette manière, à chaque requête de l'utilisateur, on pourra récupérer l'id dans le cookie session
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            # On redirige l'utilisateur vers la page principale une fois qu'il s'est connecté
            return redirect("/")
        else:
            # En cas d'erreur, on ajoute l'erreur dans la session et on redirige l'utilisateur vers le formulaire de login
            flash(error)
            return redirect(url_for("auth.login"))
    else:
        return render_template('auth/login.html')
    
# Route /auth/logout
@auth_bp.route('/logout')
def logout():
    # Se déconnecter consiste simplement à supprimer le cookie session
    session.clear()

    # On redirige l'utilisateur vers la page principale une fois qu'il s'est déconnecté
    return redirect("/")

# Fonction automatiquement appelée à chaque requête (avant d'entrer dans la route) sur une route appartenant au blueprint 'auth_bp'
# La fonction permet d'ajouter un attribut 'user' représentant l'utilisateur connecté dans l'objet 'g' 
@auth_bp.before_app_request
def load_logged_in_user():

    # On récupère l'id de l'utilisateur stocké dans le cookie session
    user_id = session.get('user_id')

    #On contrôle que la session n'est pas expirée
    check_session_expiration()
    
    # Si l'id de l'utilisateur dans le cookie session est nul, cela signifie que l'utilisateur n'est pas connecté
    # On met donc l'attribut 'user' de l'objet 'g' à None
    if user_id is None:
        g.user = None

    else:
         # On récupère la base de données et on récupère l'utilisateur correspondant à l'id stocké dans le cookie session
        db = get_db()
        g.user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

# Route pour gérer les sessions expirées
@auth_bp.route('/session-expired')
def session_expired():
    return render_template('auth/session_expired.html')

# Route /mdp_oublié
@auth_bp.route('/mdp_oublié', methods=['GET', 'POST'])
def forgot_password_page():
    return render_template('auth/forgot_password.html')



