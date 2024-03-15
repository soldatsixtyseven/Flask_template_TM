import functools
import sqlite3
import locale
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.db.db import get_db
from datetime import datetime
from functools import wraps

# Ce décorateur est utilisé dans l'application Flask pour protéger certaines vues (routes)
# afin de s'assurer qu'un utilisateur est connecté avant d'accéder à une route 

def login_required(view):
    @functools.wraps(view)

    def wrapped_view(**kwargs):
    
        # Si l'utilisateur n'est pas connecté, il ne peut pas accéder à la route, il faut le rediriger vers la route auth.login
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view

# Ce décorateur est utilisé dans l'application Flask pour protéger certaines vues (routes)
# afin de s'assurer qu'un administrateur est connecté avant d'accéder à une route 

def login_required_admin(view):
    @wraps(view)
    def wrapped_view(**kwargs):

        # Si l'administrateur n'est pas connecté, il ne peut pas accéder à la route, il faut le rediriger vers la route admin.login
        if g.admin is None:
            return redirect(url_for('admin_bp.login_admin'))
        
        return view(**kwargs)
    
    return wrapped_view

# Cette fonction récupère l'id, le nom, la date et le lieu de toutes les courses
# Cette fonction est utilisée pour afficher toutes les courses
def get_all_courses(sport=None):
    db = get_db()
    cursor = db.cursor()
    
    # Requête pour récupérer les courses en fonction du sport si spécifié, sinon récupère toutes les courses
    if sport:
        cursor.execute("SELECT id_course, name, date, location, sport FROM course WHERE date >= CURRENT_DATE AND sport = ?", (sport,))
    else:
        cursor.execute("SELECT id_course, name, date, location, sport FROM course WHERE date >= CURRENT_DATE ORDER BY date ASC")
    
    courses = cursor.fetchall()

    # Création d'une liste avec les informations de toutes les courses
    all_courses = []
    for course in courses:
        # Récupération de tous les champs de donnée
        id_course = course['id_course']
        name = course['name']
        date_str = course['date']
        location = course['location']
        sport = course['sport']
        
        # Convertir la date en un objet datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Transformer la date en français
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
        formatted_date = date_obj.strftime("%d %B %Y").capitalize()
        
        # Transformer le premier lettre du mois en miniscule
        formatted_date = formatted_date[:3].lower() + formatted_date[3:]
        
        # Ajouter les informations de la course à la liste
        all_courses.append({
            'id_course': id_course,
            'name': name,
            'date': formatted_date,
            'location': location,
            'sport': sport
        })

    return all_courses if all_courses else []


# Cette fonction récupère toutes les données de toutes les courses
def get_course_details(id_course):
    db = get_db()
    cursor = db.cursor()

    # Création d'un dictionnaire, contenant les données de toutes les courses, attribué à l'id de la course 
    cursor.execute("SELECT * FROM course WHERE id_course = ?", (id_course,))
    course_details = cursor.fetchone()

    # Récupération de toutes les catégories liées à la course
    cursor.execute("""
        SELECT name, distance, start_time, price, ascent, descent, year_max, year_min
        FROM categorie
        WHERE course_id = ?
    """, (id_course,))
    categories = cursor.fetchall()

    # Récupération de tous les champs de donnée
    if course_details:
        # Récupération du nom de la course
        course_name = course_details['name']
        
        # Changement du format de la date de la base de donnée pour convertir en un objet datetime
        date_str = course_details['date']
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Transformer la date en français
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
        # Changement du format de la date
        formatted_date = date_obj.strftime("%d %B %Y").capitalize()
        
        
        # Transformer le premier lettre du mois en miniscule
        formatted_date = formatted_date[:3].lower() + formatted_date[3:]

        # Récupération de toutes les données liées à chaque catégorie
        course_categories = []
        for category in categories:
            category_details = {
                'name': category['name'],
                'distance': category['distance'],
                'start_time': category['start_time'],
                'price': category['price'],
                'ascent': category['ascent'],
                'descent': category['descent'],
                'year_max': category['year_max'],
                'year_min': category['year_min']
            }
            course_categories.append(category_details)

        return {
            'course_name': course_name,
            'club': course_details['club'],
            'date': formatted_date,
            'location': course_details['location'],
            'canton': course_details['canton'],
            'country': course_details['country'],
            'site_club': course_details['site_club'],
            'sport': course_details['sport'],
            'flyers': course_details['flyers'],
            'categories': course_categories
            
        }
    else:
        return None

# Cette fonction permet d'inscrire un utilisateur dans une catégorie
def add_user_in_categories(user_id, category_name):

    # On essaye d'attribué la clé étrangère de l'utilisateur à celle de la catégorie dans laquelle il veut s'inscire
    try:
        db = get_db()
        cursor = db.cursor()

        # Récupérer l'id de la catégorie en fonction de son nom
        cursor.execute("SELECT id_categorie FROM categorie WHERE name = ?", (category_name,))
        categorie_id = cursor.fetchone()

        if not categorie_id:
            raise ValueError("Catégorie introuvable")

        # Insérer l'utilisateur et la catégorie dans la table "inscription" avec les clés étrangères
        cursor.execute("INSERT INTO inscription (users_id, categorie_id) VALUES (?, ?)", (user_id, categorie_id[0]))
        db.commit()
        db.close()

    # S'il y a un problème, afficher un message d'erreur
    except Exception as e:
        print("Erreur lors de l'inscription", e)

# Fonction pour récupérer les informations de l'utilisateur à partir de son ID
def get_user_info(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_info = cursor.fetchone()
    return user_info


# Fonction pour récupérer l'année de naissance de l'utilisateur à partir de ses informations
def get_user_birth_year(user_info):
    # Récupération de la date de naissance de l'utilisateur depuis ses informations
    date_of_birth_str = user_info['age']
    
    # Convertir la date de naissance en un objet datetime
    date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d')

    # Récupération de l'année de naissance
    user_birth_year = date_of_birth.year
    return user_birth_year