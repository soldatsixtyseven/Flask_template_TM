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
def get_all_courses(sport=None):
    db = get_db()
    cursor = db.cursor()
    
    # Requête pour récupérer les courses en fonction du sport si spécifié, sinon récupère toutes les courses
    if sport:
        cursor.execute("SELECT id_course, name, date, location, sport FROM course WHERE date >= CURRENT_DATE AND sport = ?", (sport,))
    else:
        cursor.execute("SELECT id_course, name, date, location, sport FROM course WHERE date >= CURRENT_DATE ORDER BY date ASC")
    
    courses = cursor.fetchall()

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
    db.close()

    # Récupération de tous les champs de donnée
    if course_details:
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
            'club': course_details['club'],
            'date': formatted_date,
            'location': course_details['location'],
            'canton': course_details['canton'],
            'country': course_details['country'],
            'site_club': course_details['site_club'],
            'flyers': course_details['flyers'],
            'categories': course_categories
            
        }
    else:
        return None