# -*- coding: utf-8 -*-
"""
Modèle Room - Représente une salle de cours.

Ce module définit la classe Room qui encapsule les données et comportements
d'une salle (amphithéâtre, salle de TD, salle TP) dans le système.
"""


class Room:
    """
    Classe représentant une salle dans le système.
    
    Attributes:
        id (int): Identifiant unique de la salle
        name (str): Nom/numéro de la salle
        room_type (str): Type de salle (Amphithéâtre, Salle TD, Salle TP)
        capacity (int): Capacité maximale de la salle
        equipments (list): Liste des équipements disponibles
    """
    
    # Types de salles
    TYPE_AMPHI = "Amphithéâtre"
    TYPE_TD = "Salle TD"
    TYPE_TP = "Salle TP"
    TYPE_COURS = "Salle Cours"
    
    def __init__(self, id, name, room_type, capacity, equipments=None):
        """
        Initialise une nouvelle salle.
        
        Args:
            id (int): Identifiant unique
            name (str): Nom de la salle
            room_type (str): Type de salle
            capacity (int): Capacité
            equipments (str, optional): Équipements (format CSV)
        """
        self.id = id
        self.name = name
        self.room_type = room_type
        self.capacity = capacity
        
        # Conversion string vers liste si nécessaire
        if equipments and isinstance(equipments, str):
            self.equipments = equipments.split(",")
        elif equipments:
            self.equipments = equipments
        else:
            self.equipments = []

    def has_equipment(self, equipment):
        """
        Vérifie si la salle possède un équipement spécifique.
        
        Args:
            equipment (str): Nom de l'équipement recherché
            
        Returns:
            bool: True si la salle possède l'équipement
        """
        return equipment in self.equipments

    def is_suitable_for(self, student_count, required_equipment=None):
        """
        Vérifie si la salle convient pour un cours donné.
        
        Args:
            student_count (int): Nombre d'étudiants
            required_equipment (str, optional): Équipement requis
            
        Returns:
            bool: True si la salle convient
        """
        if self.capacity < student_count:
            return False
        
        if required_equipment and not self.has_equipment(required_equipment):
            return False
            
        return True

    def is_lab(self):
        """Vérifie si la salle est une salle de TP avec équipement informatique."""
        return "PC" in self.equipments or "TP" in self.room_type

    def __str__(self):
        """Représentation textuelle de la salle."""
        return f"Room({self.name}, {self.room_type}, capacity={self.capacity})"

    def __repr__(self):
        """Représentation technique de la salle."""
        return f"Room(id={self.id}, name='{self.name}')"
