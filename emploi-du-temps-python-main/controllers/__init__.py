# -*- coding: utf-8 -*-
"""
Package des Contrôleurs de l'application.

Ce package contient les contrôleurs métier pour chaque profil utilisateur
de l'application de gestion des emplois du temps universitaires:

Contrôleurs principaux:
- AdminController: Gestion des emplois du temps, salles, réservations, génération automatique
- TeacherController: Consultation EDT, réservations ponctuelles, indisponibilités
- StudentController: Consultation EDT du groupe, recherche de salles libres

Modules utilitaires:
- auth_controller: Authentification des utilisateurs
- session: Gestion de la session utilisateur
"""

from .admin_controller import AdminController
from .teacher_controller import TeacherController
from .student_controller import StudentController
from .auth_controller import login
from .session import login_user, logout_user, get_current_user, is_logged_in

__all__ = [
    'AdminController',
    'TeacherController', 
    'StudentController',
    'login',
    'login_user',
    'logout_user',
    'get_current_user',
    'is_logged_in'
]
