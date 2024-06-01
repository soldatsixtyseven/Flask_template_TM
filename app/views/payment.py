from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, Response, Flask)
import sqlite3
from werkzeug.security import check_password_hash
from app.db.db import get_db
from ..utils import get_course_details, add_user_in_categories, add_participant_in_categories, login_required, login_required_admin

# Création d'un blueprint contenant les routes ayant le préfixe /paiement/...
payment_bp = Blueprint('payment_bp', __name__, url_prefix='/paiement')

# Création d'un URL dynamique pour les utilisateurs qui choississent le moyen de paiement en ligne "twint"
@payment_bp.route('/twint/user/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
@login_required
def twint_payment_user(id_course, course_name, category_name, category_price):
    session['payment_method'] = 'twint'

    # Rediriger vers la page twint_payment.html
    return render_template('payment/twint_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

# Création d'un URL dynamique pour les utilisateurs qui choississent le moyen de paiement en ligne "postfinance"
@payment_bp.route('/postfinance/user/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
@login_required
def postfinance_payment_user(id_course, course_name, category_name, category_price):
    session['payment_method'] = 'postfinance'

    # Rediriger vers la page postfinance_payment.html
    return render_template('payment/postfinance_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

# Création d'un URL dynamique pour les utilisateurs qui choississent le moyen de paiement en ligne "paypal"
@payment_bp.route('/paypal/user/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
@login_required
def paypal_payment_user(id_course, course_name, category_name, category_price):
    session['payment_method'] = 'paypal'

    # Rediriger vers la page paypal_payment.html
    return render_template('payment/paypal_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

# Création d'un URL dynamique pour les utilisateurs qui choississent le moyen de paiement en ligne "carte_bancaire"
@payment_bp.route('/carte_bancaire/user/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
@login_required
def bank_card_payment_user(id_course, course_name, category_name, category_price):
    session['payment_method'] = 'carte bancaire'
    
    # ORediriger vers la page bank_card_payment.html avec les informations nécessaires
    return render_template('payment/bank_card_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

# Création d'un URL dynamique pour inscrire l'utilisateur dans la catégorie choisie après paiement
# Cette route est dédié aux user qui s'inscrire en ligne
@payment_bp.route('/paiement/inscription/confirmation/user/<int:id_course>/<string:course_name>/<string:category_name>', methods=['GET'])
@login_required
def confirmation(id_course, course_name, category_name):
    # Récupération de l'id de l'utilisateur
    user_id = session.get('user_id')
    payment_method = session.get('payment_method')
    
    # Contrôle si l'id de l'utilisateur est toujours disponible
    if user_id is None:
        flash("Erreur: Utilisateur non identifié.")
        return redirect(url_for('course_bp.course_information', id_course=id_course, course_name=course_name))
    
    # Si l'id de l'utilisateur est toujours disponible, on essaye d'inscrire l'utilisateur
    try:
        # Appele de la fonction pour inscrire l'utilisateur dans sa catégorie
        add_user_in_categories(user_id, category_name, payment_method)
        flash("Inscription réussie", "success")
        return render_template('payment/confirmation.html')
    
    # S'il y a un problème, on renvoie l'utilisateur vers la page de paiement
    except Exception as e:
        flash("Une erreur s'est produite lors de l'inscription", "error")
        return redirect(url_for('course_bp.user_payment', id_course=id_course, course_name=course_name, category_name=category_name))

# Création d'un URL dynamique pour les utilisateurs qui choississent le moyen de paiement sur place "twint"
@payment_bp.route('/twint/manual/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
@login_required_admin
def twint_manual_payment(id_course, course_name, category_name, category_price):
    session['payment_method'] = 'twint'

    # Rediriger vers la page payment_manual_payment.html avec les informations nécessaires
    return render_template('payment/twint_manual_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

# Création d'un URL dynamique pour les utilisateurs qui choississent le moyen de paiement sur place "paypal"
@payment_bp.route('/paypal/manual/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
@login_required_admin
def paypal_manual_payment(id_course, course_name, category_name, category_price):
    session['payment_method'] = 'paypal'

    # Rediriger vers la page paypal_manual_payment.html avec les informations nécessaires
    return render_template('payment/paypal_manual_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

# Création d'un URL dynamique pour les utilisateurs qui choississent le moyen de paiement sur place "cash"
@payment_bp.route('/cash/manual/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
@login_required_admin
def cash_manual_payment(id_course, course_name, category_name, category_price):
    session['payment_method'] = 'cash'

    # Rediriger vers la page cash_manual_payment.html avec les informations nécessaires
    return render_template('payment/cash_manual_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

# Création d'un URL dynamique pour les utilisateurs qui sont invités
@payment_bp.route('/cash/manual/<int:id_course>/<string:course_name>/<string:category_name>', methods=['GET'])
@login_required_admin
def invited_payment(id_course, course_name, category_name):
    session['payment_method'] = 'invited'

        # Si des données de formulaire sont envoyées vers la route /admin (ce qui est le cas lorsque le formulaire de login est envoyé)
    if request.method == 'POST':
        # On récupère le champs'password' de la requête HTTP
        password = request.form['password']

        # On récupère l'id de l'administrateur stocké dans la session
        admin_id = session.get('admin_id')

        if admin_id is None:
            flash('ID administrateur manquant dans la session.')
            return render_template('payment/invited_payment.html', id_course=id_course, course_name=course_name, category_name=category_name)
        
        # On récupère la base de données
        db = get_db()

        # On récupère l'administrateur avec l'id_admin spécifié
        admin = db.execute('SELECT * FROM admin WHERE id_admin = ?', (admin_id,)).fetchone()

        error = None
        if not admin or not check_password_hash(admin['mdp'], password):
            error = 'Mot de passe incorrect.'
            flash(error)
            # Rediriger vers la page invited_payment.html avec les informations nécessaires
            return render_template('payment/invited_payment.html', id_course=id_course, course_name=course_name, category_name=category_name)

        # S'il n'y a pas d'erreur, on ajoute l'id de l'administrateur dans une variable de session
        # De cette manière, à chaque requête de l'utilisateur, on pourra récupérer l'id dans le cookie session
        if error is None:
            session.clear()
            session['admin_id'] = admin['id_admin']
            # On redirige l'administrateur vers la page admin_home.html une fois qu'il s'est connecté
            return redirect(url_for('course_bp.manual_confirmation'))
        else:
            # En cas d'erreur, on ajoute l'erreur dans la session et on redirige l'utilisateur vers le formulaire de login
            flash(error)

            # Rediriger vers la page invited_payment.html avec les informations nécessaires
            return render_template('payment/invited_payment.html', id_course=id_course, course_name=course_name, category_name=category_name)
    
    else:
        # Rediriger vers la page invited_payment.html avec les informations nécessaires
        return render_template('payment/invited_payment.html', id_course=id_course, course_name=course_name, category_name=category_name)
    

# Création d'un URL dynamique pour inscrire l'utilisateur dans la catégorie choisie après paiement
# Cette route est dédié aux participants qui s'inscrivent sur place
@payment_bp.route('/paiement/inscription/confirmation/<int:id_course>/<string:course_name>/<string:category_name>', methods=['GET'])
@login_required_admin
def manual_confirmation(id_course, course_name, category_name):
    # Récupération de l'id de l'utilisateur
    participant_id = session.get('participant_id')
    payment_method = session.get('payment_method')
    
    # Contrôle si l'id de l'utilisateur est toujours disponible
    if participant_id is None:
        flash("Erreur: Utilisateur non identifié.")
        return redirect(url_for('course_bp.manual_registration', id_course=id_course, course_name=course_name))

    # Si l'id de l'utilisateur est toujours disponible, on essaye d'inscrire l'utilisateur
    try:
        # Appele de la fonction pour inscrire l'utilisateur dans sa catégorie
        add_participant_in_categories(participant_id, category_name, payment_method)
        flash("Inscription réussie", "success")
        return render_template('payment/manual_confirmation.html')
    
    # S'il y a un problème, on renvoie l'utilisateur vers la page de paiement
    except Exception as e:
        flash("Une erreur s'est produite lors de l'inscription", "error")
        return redirect(url_for('course_bp.manual_payment', id_course=id_course, course_name=course_name, category_name=category_name))
