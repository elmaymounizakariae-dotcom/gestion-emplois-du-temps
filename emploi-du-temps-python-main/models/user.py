# -*- coding: utf-8 -*-
"""
Modèle User - Représente un utilisateur du système.

Ce module définit la classe User qui encapsule les données et comportements
d'un utilisateur de l'application (administrateur, enseignant ou étudiant).
"""


class User:
    """
    Classe représentant un utilisateur du système.
    
    Attributes:
        id (int): Identifiant unique de l'utilisateur
        username (str): Nom d'utilisateur pour la connexion
        role (str): Rôle de l'utilisateur ('admin', 'enseignant', 'etudiant')
        full_name (str): Nom complet de l'utilisateur
    """
    
    # Constantes de rôles possibles
    ROLE_ADMIN = "admin"
    ROLE_TEACHER = "enseignant"
    ROLE_STUDENT = "etudiant"
    
    def __init__(self, id, username, role, full_name):
        """
        Initialise un nouvel utilisateur.
        
        Args:
            id (int): Identifiant unique
            username (str): Nom d'utilisateur
            role (str): Rôle de l'utilisateur
            full_name (str): Nom complet
        """
        self.id = id
        self.username = username
        self.role = role
        self.full_name = full_name

    def is_admin(self):
        """Vérifie si l'utilisateur est administrateur."""
        return self.role == self.ROLE_ADMIN

    def is_teacher(self):
        """Vérifie si l'utilisateur est enseignant."""
        return self.role == self.ROLE_TEACHER

    def is_student(self):
        """Vérifie si l'utilisateur est étudiant."""
        return self.role == self.ROLE_STUDENT

    def __str__(self):
        """Représentation textuelle de l'utilisateur."""
        return f"User({self.username}, {self.role}, {self.full_name})"

    def __repr__(self):
        """Représentation technique de l'utilisateur."""
        return f"User(id={self.id}, username='{self.username}', role='{self.role}')"
