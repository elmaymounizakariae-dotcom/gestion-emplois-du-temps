# -*- coding: utf-8 -*-
"""
Modèle Subject - Représente une matière/module.

Ce module définit la classe Subject qui encapsule les données et comportements
d'une matière enseignée dans le système.
"""


class Subject:
    """
    Classe représentant une matière/module.
    
    Attributes:
        id (int): Identifiant unique de la matière
        name (str): Nom de la matière
        code (str): Code unique (ex: AD51, M01)
        hours_total (int): Volume horaire total
        subject_type (str): Type de cours (CM, TD, TP, CM/TD, CM/TP)
        required_equipment (list): Équipements nécessaires
    """
    
    # Types de cours
    TYPE_CM = "CM"       # Cours Magistral
    TYPE_TD = "TD"       # Travaux Dirigés
    TYPE_TP = "TP"       # Travaux Pratiques
    TYPE_CM_TD = "CM/TD"
    TYPE_CM_TP = "CM/TP"
    
    def __init__(self, id, name, code, hours_total, subject_type, required_equipment=None):
        """
        Initialise une nouvelle matière.
        
        Args:
            id (int): Identifiant unique
            name (str): Nom de la matière
            code (str): Code unique
            hours_total (int): Volume horaire
            subject_type (str): Type de cours
            required_equipment (str, optional): Équipements requis (format CSV)
        """
        self.id = id
        self.name = name
        self.code = code
        self.hours_total = hours_total
        self.subject_type = subject_type
        
        # Conversion string vers liste si nécessaire
        if required_equipment and isinstance(required_equipment, str):
            self.required_equipment = required_equipment.split(",")
        elif required_equipment:
            self.required_equipment = required_equipment
        else:
            self.required_equipment = []

    def requires_lab(self):
        """
        Vérifie si la matière nécessite une salle de TP.
        
        Returns:
            bool: True si TP requis
        """
        return self.TYPE_TP in self.subject_type

    def requires_equipment(self, equipment):
        """
        Vérifie si la matière nécessite un équipement spécifique.
        
        Args:
            equipment (str): Nom de l'équipement
            
        Returns:
            bool: True si l'équipement est requis
        """
        return equipment in self.required_equipment

    def get_session_duration(self):
        """
        Retourne la durée typique d'une séance selon le type.
        
        Returns:
            int: Durée en heures (2 pour CM/TD, 3 pour TP)
        """
        if self.requires_lab():
            return 3  # Séances TP de 3 heures
        return 2  # Séances CM/TD de 2 heures

    def __str__(self):
        """Représentation textuelle de la matière."""
        return f"Subject({self.name}, {self.code}, {self.subject_type})"

    def __repr__(self):
        """Représentation technique de la matière."""
        return f"Subject(id={self.id}, code='{self.code}')"
