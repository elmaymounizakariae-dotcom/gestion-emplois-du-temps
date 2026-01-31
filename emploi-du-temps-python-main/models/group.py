# -*- coding: utf-8 -*-
"""
Modèle Group - Représente un groupe d'étudiants.

Ce module définit la classe Group qui encapsule les données et comportements
d'un groupe/filière dans le système de gestion des emplois du temps.
"""


class Group:
    """
    Classe représentant un groupe d'étudiants.
    
    Attributes:
        id (int): Identifiant unique du groupe
        name (str): Nom du groupe (ex: LST AD, IDAI G1)
        student_count (int): Nombre d'étudiants dans le groupe
        filiere (str): Nom de la filière associée
    """
    
    def __init__(self, id, name, student_count, filiere):
        """
        Initialise un nouveau groupe.
        
        Args:
            id (int): Identifiant unique
            name (str): Nom du groupe
            student_count (int): Nombre d'étudiants
            filiere (str): Filière associée
        """
        self.id = id
        self.name = name
        self.student_count = student_count
        self.filiere = filiere

    def requires_room_capacity(self):
        """
        Retourne la capacité minimale de salle requise.
        
        Returns:
            int: Capacité minimale (nombre d'étudiants)
        """
        return self.student_count

    def is_same_filiere(self, other_group):
        """
        Vérifie si deux groupes appartiennent à la même filière.
        
        Args:
            other_group (Group): Autre groupe à comparer
            
        Returns:
            bool: True si même filière
        """
        return self.filiere == other_group.filiere

    def __str__(self):
        """Représentation textuelle du groupe."""
        return f"Group({self.name}, {self.filiere}, {self.student_count} étudiants)"

    def __repr__(self):
        """Représentation technique du groupe."""
        return f"Group(id={self.id}, name='{self.name}')"
