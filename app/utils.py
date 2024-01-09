import functools
import sqlite3
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from app.db.db import get_db

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


# Cette fonction récupère toutes les courses

def get_all_courses():
    
    db = get_db()
    
    all_courses = db.execute('SELECT name, sport, date, location, canton, carte, description, categorie_id FROM course').fetchall()

    return all_courses