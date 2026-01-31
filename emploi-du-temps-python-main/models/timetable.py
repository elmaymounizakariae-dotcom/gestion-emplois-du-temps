# -*- coding: utf-8 -*-
"""
Modèle TimetableSlot - Représente un créneau dans l'emploi du temps.

Ce module définit la classe TimetableSlot qui encapsule les données et comportements
d'un créneau de cours dans l'emploi du temps.
"""


# Jours de la semaine
DAYS = {1: "Lundi", 2: "Mardi", 3: "Mercredi", 4: "Jeudi", 5: "Vendredi"}


class TimetableSlot:
    """
    Classe représentant un créneau dans l'emploi du temps.
    
    Attributes:
        id (int): Identifiant unique du créneau
        course_id (int): ID de la matière
        instructor_id (int): ID de l'enseignant
        group_id (int): ID du groupe
        room_id (int): ID de la salle
        day (int): Jour de la semaine (1=Lundi, 5=Vendredi)
        start_hour (int): Heure de début (8-18)
        duration (int): Durée en heures
    """
    
    def __init__(self, id, course_id, instructor_id, group_id, room_id, day, start_hour, duration):
        """
        Initialise un nouveau créneau.
        
        Args:
            id (int): Identifiant unique
            course_id (int): ID de la matière
            instructor_id (int): ID de l'enseignant
            group_id (int): ID du groupe
            room_id (int): ID de la salle
            day (int): Jour de la semaine
            start_hour (int): Heure de début
            duration (int): Durée en heures
        """
        self.id = id
        self.course_id = course_id
        self.instructor_id = instructor_id
        self.group_id = group_id
        self.room_id = room_id
        self.day = day
        self.start_hour = start_hour
        self.duration = duration

    def get_end_hour(self):
        """
        Calcule l'heure de fin du créneau.
        
        Returns:
            int: Heure de fin
        """
        return self.start_hour + self.duration

    def get_day_name(self):
        """
        Retourne le nom du jour.
        
        Returns:
            str: Nom du jour (Lundi, Mardi, etc.)
        """
        return DAYS.get(self.day, "Inconnu")

    def get_time_slot_string(self):
        """
        Retourne une représentation du créneau horaire.
        
        Returns:
            str: Format "HHh-HHh"
        """
        return f"{self.start_hour:02d}h-{self.get_end_hour():02d}h"

    def overlaps_with(self, other):
        """
        Vérifie s'il y a chevauchement avec un autre créneau.
        
        Args:
            other (TimetableSlot): Autre créneau à comparer
            
        Returns:
            bool: True s'il y a chevauchement
        """
        if self.day != other.day:
            return False
            
        # Chevauchement si les intervalles se croisent
        return (self.start_hour < other.get_end_hour() and 
                other.start_hour < self.get_end_hour())

    def conflicts_with_room(self, other):
        """Vérifie un conflit de salle."""
        return self.room_id == other.room_id and self.overlaps_with(other)

    def conflicts_with_instructor(self, other):
        """Vérifie un conflit d'enseignant."""
        return self.instructor_id == other.instructor_id and self.overlaps_with(other)

    def conflicts_with_group(self, other):
        """Vérifie un conflit de groupe."""
        return self.group_id == other.group_id and self.overlaps_with(other)

    def has_any_conflict(self, other):
        """
        Vérifie tout type de conflit avec un autre créneau.
        
        Args:
            other (TimetableSlot): Autre créneau
            
        Returns:
            str or None: Description du conflit ou None
        """
        if self.conflicts_with_room(other):
            return "Conflit de salle"
        if self.conflicts_with_instructor(other):
            return "Conflit d'enseignant"
        if self.conflicts_with_group(other):
            return "Conflit de groupe"
        return None

    def __str__(self):
        """Représentation textuelle du créneau."""
        return f"Slot({self.get_day_name()} {self.get_time_slot_string()})"

    def __repr__(self):
        """Représentation technique du créneau."""
        return f"TimetableSlot(id={self.id}, day={self.day}, hour={self.start_hour})"
