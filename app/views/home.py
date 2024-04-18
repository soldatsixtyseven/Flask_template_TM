from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, Response, Flask)
import sqlite3
from ..utils import get_all_courses
from email.message import EmailMessage
import smtplib

# Routes /...
home_bp = Blueprint('home', __name__)

# Route /
@home_bp.route('/', methods=('GET', 'POST'))
def landing_page():
    # Récupérez toutes les courses
    all_courses = get_all_courses()
    return render_template('home/index.html', all_courses=all_courses)


# Gestionnaire d'erreur 404 pour toutes les routes inconnues
@home_bp.route('/<path:text>', methods=['GET', 'POST'])
def not_found_error(text):
    return render_template('home/404.html'), 404

# Route /sports
@home_bp.route('/sports', methods=['GET', 'POST'])
def sports_page():
    # Récupérer toutes les courses
    all_courses = get_all_courses()

    # Classer toutes les courses dans des variables en fonction de leur sport
    athletisme = get_all_courses("athlétisme")
    course_a_pied = get_all_courses("course à pied")
    marche = get_all_courses("marche")
    hippisme = get_all_courses("hippisme")
    ski_alpin = get_all_courses("ski alpin")
    ski_nordique = get_all_courses("ski nordique")
    triathlon = get_all_courses("triathlon")
    vtt = get_all_courses("VTT")
    autres = get_all_courses("autres")

    # Envoyer toutes les données au template
    return render_template('home/sports.html', all_courses=all_courses,
                           athletisme=athletisme,
                           course_a_pied=course_a_pied, marche=marche,
                           hippisme=hippisme, ski_alpin=ski_alpin,
                           ski_nordique=ski_nordique, triathlon=triathlon,
                           vtt=vtt, autres=autres)


admin_email = "theo.frossard@studentfr.ch"

# Route /contact
@home_bp.route('/contact', methods=['GET', 'POST'])
def contact_page():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        user_email = request.form['email']
        telephone = request.form['telephone']
        complaint = request.form['complaint']

        # Création du mail le message
        message = f"""
        Nom: {last_name}
        Prénom: {first_name}
        Email: {user_email}
        Téléphone: {telephone}

        Demande:
        {complaint}
        """

        # Créer l'objet EmailMessage
        email_obj = EmailMessage()
        email_obj["From"] = user_email
        email_obj["To"] = admin_email
        email_obj["Subject"] = "Nouvelle demande depuis le site SportLog"

        # Ajouter le contenu au message
        email_obj.set_content(message)

        # Configurer le serveur SMTP
        smtp_server = "smtp-mail.outlook.com"
        smtp_port = 587

        # Établir une connexion sécurisée avec le serveur SMTP
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.send_message(email_obj)


        smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
        smtp.starttls()
        smtp.login(user_email, "my_outlook_password_123")
        smtp.sendmail(user_email, admin_email, email.as_string())
        smtp.quit()

        # Rediriger vers une page de confirmation
        return redirect(url_for('confirmation_page'))

    # Si la méthode est GET, afficher simplement le formulaire
    return render_template('home/contact.html')

# Route pour la page de confirmation
@home_bp.route('/confirmation')
def confirmation_page():
    return render_template('confirmation.html')

# Route /FAQ
@home_bp.route('/about', methods=['GET', 'POST'])
def about_page():
    return render_template('home/about.html')



