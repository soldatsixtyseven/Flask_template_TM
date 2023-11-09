from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)

# Routes /...
home_bp = Blueprint('home', __name__)



# Route /
@home_bp.route('/', methods=('GET', 'POST'))
def landing_page():
    # Affichage de la page principale de l'application
    return render_template('home/index.html')

# Gestionnaire d'erreur 404 pour toutes les routes inconnues
@home_bp.route('/<path:text>', methods=['GET', 'POST'])
def not_found_error(text):
    return render_template('home/404.html'), 404

# Route /sports
@home_bp.route('/sports', methods=['GET', 'POST'])
def sports_page():
    return render_template('home/sports.html')

# Route /contact
@home_bp.route('/contact', methods=['GET', 'POST'])
def contact_page():
    return render_template('home/contact.html')

# Route /connection
@home_bp.route('/connection', methods=['GET', 'POST'])
def connection_page():
    return render_template('home/connection.html')

# Route /connection/mdp_oublié
@home_bp.route('/connection/mdp_oublie', methods=['GET', 'POST'])
def mdp_oublie_page():
    return render_template('home/connection/mdp_oublie.html')