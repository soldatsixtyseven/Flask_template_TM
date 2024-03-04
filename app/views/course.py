from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, Response, Flask)
import sqlite3
from ..utils import get_all_courses
from app.db.db import get_db

# Création d'un blueprint contenant les routes ayant le préfixe /course/...
course_bp = Blueprint('course_bp', __name__, url_prefix='/course')


@course_bp.route('/course/<int:id_course>/<string:name>')
def course_information(id_course, name):
    
        return render_template('course/information.html', id_course=id_course, name=name)
