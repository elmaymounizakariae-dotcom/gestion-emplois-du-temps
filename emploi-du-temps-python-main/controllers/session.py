# -*- coding: utf-8 -*-
"""
Gestion de la session utilisateur

Ce module maintient l'état de la session de l'utilisateur connecté.
"""

# Variable globale pour stocker l'utilisateur actuellement connecté
current_user = None


def login_user(user):
    """
    Enregistre l'utilisateur dans la session.
    
    Args:
        user (User): Objet utilisateur à enregistrer
    """
    global current_user
    current_user = user


def logout_user():
    """
    Déconnecte l'utilisateur actuel en vidant la session.
    """
    global current_user
    current_user = None


def get_current_user():
    """
    Récupère l'utilisateur actuellement connecté.
    
    Returns:
        User or None: L'utilisateur connecté ou None
    """
    return current_user


def is_logged_in():
    """
    Vérifie si un utilisateur est connecté.
    
    Returns:
        bool: True si connecté, False sinon
    """
    return current_user is not None
