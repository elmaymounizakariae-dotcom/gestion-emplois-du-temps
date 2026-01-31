# -*- coding: utf-8 -*-
"""
Contrôleur d'Authentification

Ce module gère l'authentification des utilisateurs dans le système.
"""

import bcrypt
from database import getConnection
from models.user import User


def login(username, password):
    """
    Authentifie un utilisateur avec son nom d'utilisateur et mot de passe.
    
    Args:
        username (str): Nom d'utilisateur
        password (str): Mot de passe en clair
        
    Returns:
        User or None: Objet User si authentification réussie, None sinon
    """
    conn = getConnection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, password, role, full_name FROM users WHERE username = ?",
        (username,)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None  # Utilisateur non trouvé

    if not bcrypt.checkpw(password.encode("utf-8"), row["password"]):
        return None  # Mot de passe incorrect

    # Création de l'objet User
    user = User(
        id=row["id"],
        username=row["username"],
        role=row["role"],
        full_name=row["full_name"]
    )

    return user
