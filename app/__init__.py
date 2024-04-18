import os
from flask import Flask
from app.utils import *

# Importation des blueprints de l'application
# Chaque blueprint contient des routes pour l'application
from app.views.home import home_bp
from app.views.auth import auth_bp
from app.views.admin import admin_bp
from app.views.user import user_bp
from app.views.course import course_bp
from app.views.payment import payment_bp

# Fonction automatiquement appelée par le framework Flask lors de l'exécution de la commande python -m flask run permettant de lancer le projet
# La fonction retourne une instance de l'application créée
def create_app():

    # Crée l'application Flask
    app = Flask(__name__)

    # Chargement des variables de configuration stockées dans le fichier config.py
    app.config.from_pyfile(os.path.join(os.path.dirname(__file__), "config.py"))

    # Enregistrement des blueprints de l'application.
    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(payment_bp)

    # On retourne l'instance de l'application Flask
    return app