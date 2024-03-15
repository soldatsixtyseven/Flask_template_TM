from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, Response, Flask)
import sqlite3
from ..utils import get_course_details, add_user_in_categories

# Création d'un blueprint contenant les routes ayant le préfixe /paiement/...
payment_bp = Blueprint('payment_bp', __name__, url_prefix='/paiement')

# Création d'un URL dynamique pour les utilisateurs qui choississent le moyen de paiement en ligne "twint"
@payment_bp.route('/twint/user/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
def twint_payment_user(id_course, course_name, category_name, category_price):

    # Rediriger vers la page twint_payment.html
    return render_template('payment/twint_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

# Création d'un URL dynamique pour les utilisateurs qui choississent le moyen de paiement en ligne "postfinance"
@payment_bp.route('/postfinance/user/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
def postfinance_payment_user(id_course, course_name, category_name, category_price):

    # Rediriger vers la page postfinance_payment.html
    return render_template('payment/postfinance_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

# Création d'un URL dynamique pour les utilisateurs qui choississent le moyen de paiement en ligne "paypal"
@payment_bp.route('/paypal/user/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
def paypal_payment_user(id_course, course_name, category_name, category_price):

    # Rediriger vers la page paypal_payment.html
    return render_template('payment/paypal_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

# Création d'un URL dynamique pour les utilisateurs qui choississent le moyen de paiement en ligne "carte_bancaire"
@payment_bp.route('/carte_bancaire/user/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
def bank_card_payment_user(id_course, course_name, category_name, category_price):
    
    # ORediriger vers la page bank_card_payment.html avec les informations nécessaires
    return render_template('payment/bank_card_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

# Création d'un URL dynamique pour les utilisateurs qui choississent le moyen de paiement sur place "twint"
@payment_bp.route('/twint/manual/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
def twint_manual_payment(id_course, course_name, category_name, category_price):

    # Rediriger vers la page payment_manual_payment.html avec les informations nécessaires
    return render_template('payment/twint_manual_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

# Création d'un URL dynamique pour les utilisateurs qui choississent le moyen de paiement sur place "paypal"
@payment_bp.route('/paypal/manual/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
def paypal_manual_payment(id_course, course_name, category_name, category_price):

    # Rediriger vers la page paypal_manual_payment.html avec les informations nécessaires
    return render_template('payment/paypal_manual_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

# Création d'un URL dynamique pour les utilisateurs qui choississent le moyen de paiement sur place "cash"
@payment_bp.route('/cash/manual/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
def cash_manual_payment(id_course, course_name, category_name, category_price):

    # Rediriger vers la page cash_manual_payment.html avec les informations nécessaires
    return render_template('payment/cash_manual_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

# Création d'un URL dynamique pour inscrire l'utilisateur dans la catégorie choisie après paiement
# Cette route est dédié aux user qui s'inscrire en ligne
@payment_bp.route('/paiement/inscription/confirmation/user/<int:id_course>/<string:course_name>/<string:category_name>', methods=['GET'])
def confirmation(id_course, course_name, category_name):
    # Récupération de l'id de l'utilisateur
    user_id = session.get('user_id')
    
    # Contrôle si l'id de l'utilisateur est toujours disponible
    if user_id is None:
        flash("Erreur: Utilisateur non identifié.")
        return redirect(url_for('course_bp.course_information', id_course=id_course, course_name=course_name))
    
    # Si l'id de l'utilisateur est toujours disponible, on essaye d'inscrire l'utilisateur
    try:
        # Appele de la fonction pour inscrire l'utilisateur dans sa catégorie
        add_user_in_categories(user_id, category_name)
        flash("Inscription réussie", "success")
        return render_template('payment/confirmation.html')
    
    # S'il y a un problème, on renvoie l'utilisateur vers la page de paiement
    except Exception as e:
        flash("Une erreur s'est produite lors de l'inscription", "error")
        return redirect(url_for('course_bp.user_payment', id_course=id_course, course_name=course_name, category_name=category_name))

# Création d'un URL dynamique pour inscrire l'utilisateur dans la catégorie choisie après paiement
# Cette route est dédié aux participants qui s'inscrivent sur place
@payment_bp.route('/paiement/inscription/confirmation/<int:id_course>/<string:course_name>/<string:category_name>', methods=['GET'])
def manual_confirmation(id_course, course_name, category_name):
    # Récupération de l'id de l'utilisateur
    user_id = session.get('user_id')
    
    # Contrôle si l'id de l'utilisateur est toujours disponible
    if user_id is None:
        flash("Erreur: Utilisateur non identifié.")
        return redirect(url_for('course_bp.manual_registration', id_course=id_course, course_name=course_name))

    # Si l'id de l'utilisateur est toujours disponible, on essaye d'inscrire l'utilisateur
    try:
        # Appele de la fonction pour inscrire l'utilisateur dans sa catégorie
        add_user_in_categories(user_id, category_name)
        flash("Inscription réussie", "success")
        return render_template('payment/manual_confirmation.html')
    
    # S'il y a un problème, on renvoie l'utilisateur vers la page de paiement
    except Exception as e:
        flash("Une erreur s'est produite lors de l'inscription", "error")
        return redirect(url_for('course_bp.manual_payment', id_course=id_course, course_name=course_name, category_name=category_name))
