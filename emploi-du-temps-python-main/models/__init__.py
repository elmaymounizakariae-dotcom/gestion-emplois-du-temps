# -*- coding: utf-8 -*-
"""
Package des Modèles de l'application.

Ce package contient les classes modèles représentant les entités principales
du système de gestion des emplois du temps universitaires:

- User: Utilisateur du système (admin, enseignant, étudiant)
- Instructor: Enseignant avec ses disponibilités
- Group: Groupe d'étudiants / Filière
- Room: Salle de cours (amphi, TD, TP)
- Subject: Matière / Module enseigné
- TimetableSlot: Créneau dans l'emploi du temps

Ces modèles suivent les principes de la Programmation Orientée Objet:
- Encapsulation des données
- Méthodes métier associées
- Documentation complète
"""

from .user import User
from .instructor import Instructor
from .group import Group
from .room import Room
from .subject import Subject
from .timetable import TimetableSlot

__all__ = [
    'User',
    'Instructor', 
    'Group',
    'Room',
    'Subject',
    'TimetableSlot'
]
