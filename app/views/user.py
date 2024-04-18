from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.db.db import get_db
from app.utils import login_required
from ..utils import get_user_info
import os

# Création d'un blueprint contenant les routes ayant le préfixe /admin/...
user_bp = Blueprint('user_bp', __name__, url_prefix='/user')

# Route /admin/home
@user_bp.route('/profil', methods=('GET', 'POST'))
@login_required
def profile_page():
    user_id = session.get('user_id')
    user_info = get_user_info(user_id)
    user_name = user_info['name']
    user_surname = user_info['surname']
    user_sexe = user_info['sexe']


    return render_template('user/profile.html', user_name=user_name, user_surname=user_surname, user_sexe=user_sexe)

# Route /informations-personnelles
@user_bp.route('/informations-personelles', methods=['GET', 'POST'])
def personal_information_page():
    return render_template('user/personal_information.html')

# Route /historique
@user_bp.route('/historique', methods=['GET', 'POST'])
def history_page():
    return render_template('user/history_course.html')