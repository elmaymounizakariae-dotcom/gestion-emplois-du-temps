# -*- coding: utf-8 -*-
"""
Modèle Instructor - Représente un enseignant.

Ce module définit la classe Instructor qui encapsule les données et comportements
d'un enseignant dans le système de gestion des emplois du temps.
"""


class Instructor:
    """
    Classe représentant un enseignant dans le système.
    
    Attributes:
        id (int): Identifiant unique de l'enseignant
        user_id (int): Référence vers l'utilisateur associé
        name (str): Nom complet de l'enseignant
        speciality (str): Spécialité/domaine d'expertise
        unavailable_slots (list): Liste des créneaux d'indisponibilité
    """
    
    def __init__(self, id, user_id, name, speciality, unavailable_slots=None):
        """
        Initialise un nouvel enseignant.
        
        Args:
            id (int): Identifiant unique
            user_id (int): ID de l'utilisateur associé
            name (str): Nom complet
            speciality (str): Spécialité
            unavailable_slots (str, optional): Créneaux indisponibles (format CSV)
        """
        self.id = id
        self.user_id = user_id
        self.name = name
        self.speciality = speciality
        
        # Conversion string vers liste si nécessaire
        if unavailable_slots and isinstance(unavailable_slots, str):
            self.unavailable_slots = unavailable_slots.split(",")
        elif unavailable_slots:
            self.unavailable_slots = unavailable_slots
        else:
            self.unavailable_slots = []

    def is_available(self, day, hour):
        """
        Vérifie si l'enseignant est disponible à un créneau donné.
        
        Args:
            day (str): Jour de la semaine
            hour (int): Heure du créneau
            
        Returns:
            bool: True si disponible, False sinon
        """
        slot = f"{day}_{hour}"
        return slot not in self.unavailable_slots

    def add_unavailability(self, day, hour):
        """
        Ajoute un créneau d'indisponibilité.
        
        Args:
            day (str): Jour de la semaine
            hour (int): Heure du créneau
        """
        slot = f"{day}_{hour}"
        if slot not in self.unavailable_slots:
            self.unavailable_slots.append(slot)

    def remove_unavailability(self, day, hour):
        """
        Supprime un créneau d'indisponibilité.
        
        Args:
            day (str): Jour de la semaine
            hour (int): Heure du créneau
        """
        slot = f"{day}_{hour}"
        if slot in self.unavailable_slots:
            self.unavailable_slots.remove(slot)

    def get_unavailable_slots_string(self):
        """Retourne les créneaux indisponibles sous forme de chaîne CSV."""
        return ",".join(self.unavailable_slots)

    def __str__(self):
        """Représentation textuelle de l'enseignant."""
        return f"Instructor({self.name}, {self.speciality})"

    def __repr__(self):
        """Représentation technique de l'enseignant."""
        return f"Instructor(id={self.id}, name='{self.name}')"
