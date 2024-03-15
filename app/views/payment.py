from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, Response, Flask)
import sqlite3
from ..utils import get_course_details

# Création d'un blueprint contenant les routes ayant le préfixe /paiement/...
payment_bp = Blueprint('payment_bp', __name__, url_prefix='/paiement')

@payment_bp.route('/twint/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
def twint_payment(id_course, course_name, category_name, category_price):
    # Logique de traitement pour le paiement TWINT
    return render_template('payment/twint_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

@payment_bp.route('/postfinance/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
def postfinance_payment(id_course, course_name, category_name, category_price):
    # Logique de traitement pour le paiement PostFinance
    return render_template('payment/postfinance_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

@payment_bp.route('/paypal/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
def paypal_payment(id_course, course_name, category_name, category_price):
    # Logique de traitement pour le paiement PayPal
    return render_template('payment/paypal_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

@payment_bp.route('/carte_bancaire/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
def bank_card_payment(id_course, course_name, category_name, category_price):
    # Logique de traitement pour le paiement par Carte bancaire
    return render_template('payment/bank_card_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

@payment_bp.route('/twint/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
def twint_manual_payment(id_course, course_name, category_name, category_price):
    return render_template('payment/twint_manual_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

@payment_bp.route('/paypal/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
def paypal_manual_payment(id_course, course_name, category_name, category_price):
    return render_template('payment/paypal_manual_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

@payment_bp.route('/cash/<int:id_course>/<string:course_name>/<string:category_name>/<string:category_price>', methods=['GET'])
def cash_manual_payment(id_course, course_name, category_name, category_price):
    return render_template('payment/cash_manual_payment.html', id_course=id_course, course_name=course_name, category_name=category_name, category_price=category_price)

@payment_bp.route('/confirmation', methods=['GET'])
def confirmation():
    return render_template('payment/confirmation.html')