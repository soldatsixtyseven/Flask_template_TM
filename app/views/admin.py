from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.utils import *
from app.db.db import get_db

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

@admin_bp.route('/home', methods=('GET', 'POST'))
@login_required 
def show_home():
    return render_template('admin/admin_home.html')

# Route /admin
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
            return redirect(url_for('admin_bp.show_home'))
        else:
            # En cas d'erreur, on ajoute l'erreur dans la session et on redirige l'utilisateur vers le formulaire de login
            flash(error)
            return redirect(url_for('auth.login'))
    else:
        return render_template('admin/admin.html')