# -*- coding: utf-8 -*-
"""
Script de peuplement de la base de données avec un emploi du temps complet
selon le format officiel FST Tanger (Université Abdelmalek Essaâdi)

Créneaux horaires:
- 09h00-10h30
- 10h45-12h15
- 12h30-14h00
- 14h15-15h45 (15h00-16h30 le Vendredi)
- 16h00-17h30
"""

import sqlite3
import bcrypt
import os

DB_NAME = 'university_schedule.db'

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def reset_and_setup_database():
    """Réinitialise et configure la base de données"""
    # Supprimer l'ancienne base pour une installation propre
    if os.path.exists(DB_NAME):
        try:
            os.remove(DB_NAME)
            print(f"Ancienne base de données {DB_NAME} supprimée.")
        except PermissionError:
            print("Attention: Impossible de supprimer le fichier de base de données (peut-être ouvert ?).")
    
    # Importer et exécuter le setup
    from database import setup
    setup()
    print("Base de données initialisée.")

def insert_users():
    """Insère les utilisateurs (admin, enseignants, étudiants)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    users = [
        # Admins
        (1, "admin", "admin123", "admin", "Administrateur Système"),
        (2001, "mdiani", "admin123", "admin", "Mustapha Diani"),
        
        # Enseignants (22xx)
        (2201, "abenali", "prof123", "enseignant", "Ahmed Benali"),
        (2202, "felrhazi", "prof123", "enseignant", "Fatima El Rhazi"),
        (2203, "mlahlou", "prof123", "enseignant", "Mohammed Lahlou"),
        (2204, "skhalissa", "prof123", "enseignant", "Sanae Khali Issa"),
        (2205, "obaida", "prof123", "enseignant", "Ouafae Baida"),
        (2206, "mezzeyanni", "prof123", "enseignant", "Mustapha Ezzeyanni"),
        (2207, "hbourzik", "prof123", "enseignant", "Hassan Bourzik"),
        (2208, "kbensouda", "prof123", "enseignant", "Karim Bensouda"),
        (2209, "nnassiri", "prof123", "enseignant", "Nadia Nassiri"),
        (2210, "yalamrani", "prof123", "enseignant", "Youssef Alamrani"),
        (2211, "hchaabi", "prof123", "enseignant", "Hicham Chaabi"),
        (2212, "lfassi", "prof123", "enseignant", "Latifa Fassi"),
        
        # Étudiants LST AD (26xx)
        (2601, "zelmaymouni", "pass123", "etudiant", "Zakariae El Maymouni"),
        (2602, "rsaidi", "pass123", "etudiant", "Romaissae Saidi"),
        (2603, "fkastit", "pass123", "etudiant", "Fatima Zahrae Kastit"),
        (2604, "myassine", "pass123", "etudiant", "Mohamed Yassine"),
        (2605, "ahoussam", "pass123", "etudiant", "Ahmed Houssam"),
        # Étudiants IDAI
        (2610, "imad", "pass123", "etudiant", "Imad Tazi"),
        (2611, "ayman", "pass123", "etudiant", "Ayman Chraibi"),
        (2612, "janat", "pass123", "etudiant", "Janat Berrada"),
        (2613, "yasmine", "pass123", "etudiant", "Yasmine Alaoui"),
        # Étudiants SSD
        (2620, "houda", "pass123", "etudiant", "Houda Bennani"),
        (2621, "badr", "pass123", "etudiant", "Badr Senhaji"),
        (2622, "ilyas", "pass123", "etudiant", "Ilyas Mouline"),
        (2623, "hajar", "pass123", "etudiant", "Hajar Ouazzani"),
        # Étudiants MID
        (2630, "karim", "pass123", "etudiant", "Karim Idrissi"),
        (2631, "salma", "pass123", "etudiant", "Salma Taibi"),
        (2632, "omar", "pass123", "etudiant", "Omar Kettani"),
        (2633, "rania", "pass123", "etudiant", "Rania Amrani"),
        # Étudiants Génie Civil
        (2640, "amine", "pass123", "etudiant", "Amine Benchekroun"),
        (2641, "sara", "pass123", "etudiant", "Sara Lahlou"),
        # Étudiants MIPC
        (2650, "mehdi", "pass123", "etudiant", "Mehdi Zniber"),
        (2651, "mariam", "pass123", "etudiant", "Mariam Filali"),
    ]
    
    for uid, username, password, role, full_name in users:
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("""
                INSERT INTO users (id, username, password, role, full_name)
                VALUES (?, ?, ?, ?, ?)
            """, (uid, username, password_hash, role, full_name))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()
    print(f"✓ {len(users)} utilisateurs insérés")

def insert_instructors():
    """Insère les enseignants"""
    conn = get_connection()
    cursor = conn.cursor()
    
    instructors = [
        (2201, "Ahmed Benali", "Mathématiques"),
        (2202, "Fatima El Rhazi", "Physique"),
        (2203, "Mohammed Lahlou", "Informatique"),
        (2204, "Sanae Khali Issa", "IA/ML"),
        (2205, "Ouafae Baida", "Bases de Données"),
        (2206, "Mustapha Ezzeyanni", "Programmation"),
        (2207, "Hassan Bourzik", "Génie Civil"),
        (2208, "Karim Bensouda", "Électronique"),
        (2209, "Nadia Nassiri", "Réseaux/Sécurité"),
        (2210, "Youssef Alamrani", "Systèmes Distribués"),
        (2211, "Hicham Chaabi", "Data Science"),
        (2212, "Latifa Fassi", "Cloud Computing"),
    ]
    
    for user_id, name, speciality in instructors:
        try:
            cursor.execute("""
                INSERT INTO instructors (user_id, name, speciality, active)
                VALUES (?, ?, ?, 1)
            """, (user_id, name, speciality))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()
    print(f"✓ {len(instructors)} enseignants insérés")

def insert_rooms():
    """Insère les salles et amphis"""
    conn = get_connection()
    cursor = conn.cursor()
    
    rooms = [
        # Amphithéâtres
        ("Amphi 1", "Amphithéâtre", 200, ""),
        ("Amphi 2", "Amphithéâtre", 200, ""),
        ("Amphi 3", "Amphithéâtre", 200, ""),
        ("Amphi 4", "Amphithéâtre", 200, ""),
        ("Amphi 5", "Amphithéâtre", 300, ""),
        ("Amphi 6", "Amphithéâtre", 300, ""),
        
        # Salles TP Informatique
        ("E10", "Salle TP Info", 30, "PC"),
        ("E11", "Salle TP Info", 30, "PC"),
        ("E12", "Salle TP Info", 30, "PC"),
        ("E13", "Salle TP Info", 30, "PC"),
        ("E14", "Salle TP Info", 30, "PC"),
        
        # Salles de cours
        ("B01", "Salle TD", 40, ""),
        ("B02", "Salle TD", 40, ""),
        ("B03", "Salle TD", 40, ""),
        ("C01", "Salle TD", 40, ""),
        ("C02", "Salle TD", 40, ""),
        
        # Salles Génie Civil
        ("F01", "Salle TP Civil", 50, "Labo"),
        ("F02", "Salle TP Civil", 50, "Labo"),
    ]
    
    for name, room_type, capacity, equipments in rooms:
        try:
            cursor.execute("""
                INSERT INTO rooms (name, type, capacity, equipments, active)
                VALUES (?, ?, ?, ?, 1)
            """, (name, room_type, capacity, equipments))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()
    print(f"✓ {len(rooms)} salles insérées")

def insert_subjects():
    """Insère les matières"""
    conn = get_connection()
    cursor = conn.cursor()
    
    subjects = [
        # Modules LST AD
        ("Machine Learning", "AD51", 40, "CM/TP", "PC"),
        ("Structure des Données", "AD52", 36, "CM/TD", ""),
        ("Bases de Données Avancées", "AD53", 36, "CM/TP", "PC"),
        ("Python pour Data Science", "AD54", 30, "TP", "PC"),
        ("Développement Web", "AD55", 40, "TP", "PC"),
        ("Big Data", "AD56", 30, "CM/TP", "PC"),
        
        # Modules IDAI (Intelligence Artificielle)
        ("Deep Learning", "ID51", 40, "CM/TP", "PC"),
        ("Vision par Ordinateur", "ID52", 36, "CM/TP", "PC"),
        ("NLP Traitement Langage", "ID53", 36, "CM/TP", "PC"),
        ("Robotique IA", "ID54", 30, "CM/TP", "PC"),
        
        # Modules SSD (Sécurité Systèmes Distribués)
        ("Sécurité Réseaux", "SS51", 40, "CM/TP", "PC"),
        ("Cryptographie", "SS52", 36, "CM/TD", ""),
        ("Systèmes Distribués", "SS53", 36, "CM/TP", "PC"),
        ("Cloud Security", "SS54", 30, "CM/TP", "PC"),
        
        # Modules MID (Management Informatique Décisionnel)
        ("Business Intelligence", "MI51", 40, "CM/TP", "PC"),
        ("Data Warehousing", "MI52", 36, "CM/TP", "PC"),
        ("Gestion de Projet IT", "MI53", 30, "CM/TD", ""),
        ("ERP et SI", "MI54", 30, "CM/TP", "PC"),
        
        # Modules Génie Civil
        ("Béton Armé", "GC51", 40, "CM/TD", ""),
        ("Mécanique des Sols", "GC52", 36, "CM/TP", "Labo"),
        ("Construction Métallique", "GC53", 36, "CM/TD", ""),
        
        # Modules MIPC
        ("Analyse Numérique", "M51", 45, "CM/TD", ""),
        ("Physique Quantique", "P51", 40, "CM/TD", ""),
        ("Algèbre Linéaire", "M52", 45, "CM/TD", ""),
        
        # Modules Communs
        ("Anglais Technique", "LG51", 20, "TD", ""),
        ("Communication", "LG52", 20, "TD", ""),
    ]
    
    for name, code, hours, stype, equipment in subjects:
        try:
            cursor.execute("""
                INSERT INTO subjects (name, code, hours_total, type, required_equipment)
                VALUES (?, ?, ?, ?, ?)
            """, (name, code, hours, stype, equipment))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()
    print(f"✓ {len(subjects)} matières insérées")

def insert_groups():
    """Insère les groupes/filières"""
    conn = get_connection()
    cursor = conn.cursor()
    
    groups = [
        # LST AD
        ("LST AD", 35, "LST AD"),
        ("LST AD - G1", 18, "LST AD"),
        ("LST AD - G2", 17, "LST AD"),
        # IDAI
        ("IDAI", 32, "IDAI"),
        ("IDAI - G1", 16, "IDAI"),
        ("IDAI - G2", 16, "IDAI"),
        # SSD
        ("SSD", 30, "SSD"),
        ("SSD - G1", 15, "SSD"),
        ("SSD - G2", 15, "SSD"),
        # MID
        ("MID", 28, "MID"),
        ("MID - G1", 14, "MID"),
        ("MID - G2", 14, "MID"),
        # Génie Civil
        ("Génie Civil", 40, "Génie Civil"),
        ("Génie Civil - G1", 20, "Génie Civil"),
        ("Génie Civil - G2", 20, "Génie Civil"),
        # MIPC
        ("MIPC S6", 45, "MIPC"),
        ("MIPC S6 - G1", 23, "MIPC"),
        ("MIPC S6 - G2", 22, "MIPC"),
    ]
    
    for name, student_count, filiere in groups:
        try:
            cursor.execute("""
                INSERT INTO groups (name, student_count, filiere, active)
                VALUES (?, ?, ?, 1)
            """, (name, student_count, filiere))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()
    print(f"✓ {len(groups)} groupes insérés")

def get_id(table, column, value):
    """Récupère l'ID d'un enregistrement"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {table} WHERE {column} = ?", (value,))
    result = cursor.fetchone()
    conn.close()
    return result['id'] if result else None

def insert_timetable_fst():
    """
    Insère l'emploi du temps selon le format FST Tanger
    
    Créneaux:
    - 09h = 09h00-10h30
    - 10h = 10h45-12h15  (représenté par start_hour=10)
    - 12h = 12h30-14h00
    - 14h = 14h15-15h45
    - 16h = 16h00-17h30
    
    Jours: 1=Lundi, 2=Mardi, 3=Mercredi, 4=Jeudi, 5=Vendredi, 6=Samedi
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Vider la table timetable
    cursor.execute("DELETE FROM timetable")
    conn.commit()
    
    # Récupérer les IDs
    # Enseignants
    prof_benali = get_id("instructors", "name", "Ahmed Benali")
    prof_elrhazi = get_id("instructors", "name", "Fatima El Rhazi")
    prof_lahlou = get_id("instructors", "name", "Mohammed Lahlou")
    prof_sanae = get_id("instructors", "name", "Sanae Khali Issa")
    prof_ouafae = get_id("instructors", "name", "Ouafae Baida")
    prof_ezzey = get_id("instructors", "name", "Mustapha Ezzeyanni")
    prof_bourzik = get_id("instructors", "name", "Hassan Bourzik")
    prof_bensouda = get_id("instructors", "name", "Karim Bensouda")
    
    # Groupes
    grp_ad = get_id("groups", "name", "LST AD")
    grp_ad_g1 = get_id("groups", "name", "LST AD - G1")
    grp_ad_g2 = get_id("groups", "name", "LST AD - G2")
    grp_gc = get_id("groups", "name", "Génie Civil")
    grp_gc_g1 = get_id("groups", "name", "Génie Civil - G1")
    grp_gc_g2 = get_id("groups", "name", "Génie Civil - G2")
    grp_mipc = get_id("groups", "name", "MIPC S6")
    grp_mipc_g1 = get_id("groups", "name", "MIPC S6 - G1")
    grp_mipc_g2 = get_id("groups", "name", "MIPC S6 - G2")
    
    # Matières
    sub_ml = get_id("subjects", "code", "AD51")
    sub_struct = get_id("subjects", "code", "AD52")
    sub_bd = get_id("subjects", "code", "AD53")
    sub_py = get_id("subjects", "code", "AD54")
    sub_web = get_id("subjects", "code", "AD55")
    sub_bigdata = get_id("subjects", "code", "AD56")
    sub_beton = get_id("subjects", "code", "GC51")
    sub_sols = get_id("subjects", "code", "GC52")
    sub_metal = get_id("subjects", "code", "GC53")
    sub_analyse = get_id("subjects", "code", "M51")
    sub_physique = get_id("subjects", "code", "P51")
    sub_algebre = get_id("subjects", "code", "M52")
    sub_anglais = get_id("subjects", "code", "LG51")
    sub_comm = get_id("subjects", "code", "LG52")
    
    # Salles
    amphi1 = get_id("rooms", "name", "Amphi 1")
    amphi2 = get_id("rooms", "name", "Amphi 2")
    amphi3 = get_id("rooms", "name", "Amphi 3")
    amphi5 = get_id("rooms", "name", "Amphi 5")
    e10 = get_id("rooms", "name", "E10")
    e11 = get_id("rooms", "name", "E11")
    e12 = get_id("rooms", "name", "E12")
    b01 = get_id("rooms", "name", "B01")
    b02 = get_id("rooms", "name", "B02")
    c01 = get_id("rooms", "name", "C01")
    f01 = get_id("rooms", "name", "F01")
    f02 = get_id("rooms", "name", "F02")
    
    admin_id = 1
    
    # ========================================
    # EMPLOI DU TEMPS LST AD (Semestre 6)
    # ========================================
    timetable_data = [
        # === LUNDI ===
        # 09h00-10h30: Machine Learning CM (Amphi)
        (sub_ml, prof_sanae, grp_ad, amphi1, 1, 9, 2),
        # 10h45-12h15: Structure des Données TD
        (sub_struct, prof_ezzey, grp_ad_g1, b01, 1, 11, 2),
        (sub_struct, prof_ezzey, grp_ad_g2, b02, 1, 11, 2),
        # 14h15-15h45: Bases de Données TP
        (sub_bd, prof_ouafae, grp_ad_g1, e10, 1, 14, 2),
        (sub_bd, prof_ouafae, grp_ad_g2, e11, 1, 14, 2),
        
        # === MARDI ===
        # 09h00-10h30: Python TP
        (sub_py, prof_lahlou, grp_ad_g1, e10, 2, 9, 2),
        (sub_py, prof_lahlou, grp_ad_g2, e11, 2, 9, 2),
        # 10h45-12h15: Big Data CM
        (sub_bigdata, prof_sanae, grp_ad, amphi2, 2, 11, 2),
        # 14h15-15h45: Développement Web TP
        (sub_web, prof_ezzey, grp_ad_g1, e12, 2, 14, 2),
        
        # === MERCREDI ===
        # 09h00-10h30: Machine Learning TP
        (sub_ml, prof_sanae, grp_ad_g1, e10, 3, 9, 2),
        (sub_ml, prof_sanae, grp_ad_g2, e11, 3, 9, 2),
        # 10h45-12h15: Anglais
        (sub_anglais, prof_benali, grp_ad, c01, 3, 11, 2),
        
        # === JEUDI ===
        # 09h00-10h30: Structure Données CM
        (sub_struct, prof_ezzey, grp_ad, amphi1, 4, 9, 2),
        # 10h45-12h15: Bases de Données CM
        (sub_bd, prof_ouafae, grp_ad, amphi1, 4, 11, 2),
        # 14h15-15h45: Python TP (suite)
        (sub_py, prof_lahlou, grp_ad_g2, e10, 4, 14, 2),
        
        # === VENDREDI ===
        # 09h00-10h30: Communication
        (sub_comm, prof_benali, grp_ad, c01, 5, 9, 2),
        # 10h45-12h15: Développement Web CM
        (sub_web, prof_ezzey, grp_ad, amphi2, 5, 11, 2),
        # 15h00-16h30: Big Data TP (Vendredi après-midi commence à 15h)
        (sub_bigdata, prof_sanae, grp_ad_g1, e10, 5, 15, 2),
        
        
        # EMPLOI DU TEMPS GÉNIE CIVIL
        
        # === LUNDI ===
        (sub_beton, prof_bourzik, grp_gc, amphi3, 1, 9, 2),
        (sub_sols, prof_bourzik, grp_gc_g1, f01, 1, 14, 2),
        
        # === MARDI ===
        (sub_metal, prof_bourzik, grp_gc, amphi3, 2, 9, 2),
        (sub_beton, prof_bourzik, grp_gc_g1, b01, 2, 10, 2),
        (sub_beton, prof_bourzik, grp_gc_g2, b02, 2, 10, 2),
        
        # === MERCREDI ===
        (sub_sols, prof_bourzik, grp_gc, amphi3, 3, 9, 2),
        (sub_metal, prof_bourzik, grp_gc_g1, f01, 3, 14, 2),
        (sub_metal, prof_bourzik, grp_gc_g2, f02, 3, 14, 2),
        
        # === JEUDI ===
        (sub_anglais, prof_benali, grp_gc, c01, 4, 9, 2),
        (sub_sols, prof_bourzik, grp_gc_g2, f01, 4, 14, 2),
        
        
        # EMPLOI DU TEMPS MIPC S6
        
        # === LUNDI ===
        (sub_analyse, prof_benali, grp_mipc, amphi5, 1, 9, 2),
        (sub_physique, prof_elrhazi, grp_mipc, amphi5, 1, 10, 2),
        
        # === MARDI ===
        (sub_algebre, prof_benali, grp_mipc, amphi5, 2, 9, 2),
        (sub_analyse, prof_benali, grp_mipc_g1, b01, 2, 14, 2),
        (sub_analyse, prof_benali, grp_mipc_g2, b02, 2, 14, 2),
        
        # === MERCREDI ===
        (sub_physique, prof_elrhazi, grp_mipc_g1, b01, 3, 10, 2),
        (sub_physique, prof_elrhazi, grp_mipc_g2, b02, 3, 10, 2),
        
        # === JEUDI ===
        (sub_algebre, prof_benali, grp_mipc_g1, b01, 4, 9, 2),
        (sub_algebre, prof_benali, grp_mipc_g2, b02, 4, 9, 2),
        (sub_anglais, prof_benali, grp_mipc, c01, 4, 10, 2),
        
        # === VENDREDI ===
        (sub_comm, prof_benali, grp_mipc, c01, 5, 9, 2),
        (sub_analyse, prof_benali, grp_mipc, amphi5, 5, 10, 2),
    ]
    
   
    # Get new IDs
    grp_idai = get_id("groups", "name", "IDAI")
    grp_idai_g1 = get_id("groups", "name", "IDAI - G1")
    grp_idai_g2 = get_id("groups", "name", "IDAI - G2")
    grp_ssd = get_id("groups", "name", "SSD")
    grp_ssd_g1 = get_id("groups", "name", "SSD - G1")
    grp_ssd_g2 = get_id("groups", "name", "SSD - G2")
    grp_mid = get_id("groups", "name", "MID")
    grp_mid_g1 = get_id("groups", "name", "MID - G1")
    grp_mid_g2 = get_id("groups", "name", "MID - G2")
    
    sub_deep = get_id("subjects", "code", "ID51")
    sub_vision = get_id("subjects", "code", "ID52")
    sub_nlp = get_id("subjects", "code", "ID53")
    sub_robot = get_id("subjects", "code", "ID54")
    sub_secres = get_id("subjects", "code", "SS51")
    sub_crypto = get_id("subjects", "code", "SS52")
    sub_distrib = get_id("subjects", "code", "SS53")
    sub_cloudsec = get_id("subjects", "code", "SS54")
    sub_bi = get_id("subjects", "code", "MI51")
    sub_dw = get_id("subjects", "code", "MI52")
    sub_gp = get_id("subjects", "code", "MI53")
    sub_erp = get_id("subjects", "code", "MI54")
    
    prof_nassiri = get_id("instructors", "name", "Nadia Nassiri")
    prof_alamrani = get_id("instructors", "name", "Youssef Alamrani")
    prof_chaabi = get_id("instructors", "name", "Hicham Chaabi")
    prof_fassi = get_id("instructors", "name", "Latifa Fassi")
    
    amphi4 = get_id("rooms", "name", "Amphi 4")
    amphi6 = get_id("rooms", "name", "Amphi 6")
    e13 = get_id("rooms", "name", "E13")
    e14 = get_id("rooms", "name", "E14")
    b03 = get_id("rooms", "name", "B03")
    c02 = get_id("rooms", "name", "C02")
    
    timetable_idai_ssd_mid = [
       
        # EMPLOI DU TEMPS IDAI
        
        (sub_deep, prof_sanae, grp_idai, amphi4, 1, 9, 2),
        (sub_vision, prof_chaabi, grp_idai_g1, e13, 1, 10, 2),
        (sub_vision, prof_chaabi, grp_idai_g2, e14, 1, 10, 2),
        (sub_nlp, prof_sanae, grp_idai, amphi4, 2, 9, 2),
        (sub_deep, prof_sanae, grp_idai_g1, e13, 2, 14, 2),
        (sub_robot, prof_chaabi, grp_idai, amphi4, 3, 9, 2),
        (sub_nlp, prof_sanae, grp_idai_g1, e13, 3, 14, 2),
        (sub_nlp, prof_sanae, grp_idai_g2, e14, 3, 14, 2),
        (sub_anglais, prof_benali, grp_idai, c02, 4, 9, 2),
        (sub_vision, prof_chaabi, grp_idai, amphi4, 4, 10, 2),
        (sub_comm, prof_benali, grp_idai, c02, 5, 9, 2),
        (sub_robot, prof_chaabi, grp_idai_g1, e13, 5, 15, 2),
        
        
        # EMPLOI DU TEMPS SSD
   
        (sub_secres, prof_nassiri, grp_ssd, amphi6, 1, 9, 2),
        (sub_crypto, prof_nassiri, grp_ssd, amphi6, 1, 10, 2),
        (sub_distrib, prof_alamrani, grp_ssd, amphi6, 2, 9, 2),
        (sub_secres, prof_nassiri, grp_ssd_g1, e13, 2, 14, 2),
        (sub_secres, prof_nassiri, grp_ssd_g2, e14, 2, 14, 2),
        (sub_cloudsec, prof_fassi, grp_ssd, amphi6, 3, 9, 2),
        (sub_distrib, prof_alamrani, grp_ssd_g1, e13, 3, 14, 2),
        (sub_crypto, prof_nassiri, grp_ssd_g1, b03, 4, 9, 2),
        (sub_crypto, prof_nassiri, grp_ssd_g2, c02, 4, 9, 2),
        (sub_anglais, prof_benali, grp_ssd, c02, 4, 10, 2),
        (sub_comm, prof_benali, grp_ssd, c02, 5, 9, 2),
        (sub_cloudsec, prof_fassi, grp_ssd_g1, e13, 5, 15, 2),
        
       
        # EMPLOI DU TEMPS MID
       
        (sub_bi, prof_chaabi, grp_mid, amphi2, 1, 9, 2),
        (sub_dw, prof_ouafae, grp_mid, amphi2, 1, 10, 2),
        (sub_gp, prof_fassi, grp_mid, b03, 2, 9, 2),
        (sub_bi, prof_chaabi, grp_mid_g1, e10, 2, 14, 2),
        (sub_bi, prof_chaabi, grp_mid_g2, e11, 2, 14, 2),
        (sub_erp, prof_fassi, grp_mid, amphi2, 3, 9, 2),
        (sub_dw, prof_ouafae, grp_mid_g1, e10, 3, 14, 2),
        (sub_dw, prof_ouafae, grp_mid_g2, e11, 3, 14, 2),
        (sub_anglais, prof_benali, grp_mid, c02, 4, 9, 2),
        (sub_gp, prof_fassi, grp_mid_g1, b03, 4, 10, 2),
        (sub_comm, prof_benali, grp_mid, c02, 5, 9, 2),
        (sub_erp, prof_fassi, grp_mid_g1, e10, 5, 15, 2),
    ]
    
    timetable_data.extend(timetable_idai_ssd_mid)
    
    count = 0
    for course_id, instructor_id, group_id, room_id, day, start_hour, duration in timetable_data:
        if all([course_id, instructor_id, group_id, room_id]):
            try:
                cursor.execute("""
                    INSERT INTO timetable (course_id, instructor_id, group_id, room_id, day, start_hour, duration, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (course_id, instructor_id, group_id, room_id, day, start_hour, duration, admin_id))
                count += 1
            except sqlite3.IntegrityError as e:
                print(f"Erreur insertion: {e}")
    
    conn.commit()
    conn.close()
    print(f"✓ {count} créneaux d'emploi du temps insérés")

def insert_subject_relations():
    """Insère les relations matières-groupes et matières-enseignants"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Relations matière-enseignant
    subject_instructors = [
        ("AD51", "Sanae Khali Issa"),
        ("AD52", "Mustapha Ezzeyanni"),
        ("AD53", "Ouafae Baida"),
        ("AD54", "Mohammed Lahlou"),
        ("AD55", "Mustapha Ezzeyanni"),
        ("AD56", "Sanae Khali Issa"),
        ("ID51", "Sanae Khali Issa"),
        ("ID52", "Hicham Chaabi"),
        ("ID53", "Sanae Khali Issa"),
        ("ID54", "Hicham Chaabi"),
        ("SS51", "Nadia Nassiri"),
        ("SS52", "Nadia Nassiri"),
        ("SS53", "Youssef Alamrani"),
        ("SS54", "Latifa Fassi"),
        ("MI51", "Hicham Chaabi"),
        ("MI52", "Ouafae Baida"),
        ("MI53", "Latifa Fassi"),
        ("MI54", "Latifa Fassi"),
        ("GC51", "Hassan Bourzik"),
        ("GC52", "Hassan Bourzik"),
        ("GC53", "Hassan Bourzik"),
        ("M51", "Ahmed Benali"),
        ("P51", "Fatima El Rhazi"),
        ("M52", "Ahmed Benali"),
        ("LG51", "Ahmed Benali"),
        ("LG52", "Ahmed Benali"),
    ]
    
    for code, name in subject_instructors:
        sub_id = get_id("subjects", "code", code)
        instr_id = get_id("instructors", "name", name)
        if sub_id and instr_id:
            try:
                cursor.execute("""
                    INSERT INTO subject_instructors (subject_id, instructor_id)
                    VALUES (?, ?)
                """, (sub_id, instr_id))
            except sqlite3.IntegrityError:
                pass
    
    conn.commit()
    conn.close()
    print("✓ Relations matières-enseignants insérées")

def insert_student_group_relations():
    """Associe les étudiants aux groupes pour qu'ils aient la bonne filière"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Mapping Etudiant -> Groupe (Nom partiel ou complet)
    # LST AD
    stu_ad = ["zelmaymouni", "rsaidi", "fkastit", "myassine", "ahoussam"]
    grp_ad = get_id("groups", "name", "LST AD")
    
    # IDAI
    stu_idai = ["imad", "ayman", "janat", "yasmine"]
    grp_idai = get_id("groups", "name", "IDAI")
    
    # SSD
    stu_ssd = ["houda", "badr", "ilyas", "hajar"]
    grp_ssd = get_id("groups", "name", "SSD")
    
    # MID
    stu_mid = ["karim", "salma", "omar", "rania"]
    grp_mid = get_id("groups", "name", "MID")
    
    # Génie Civil
    stu_gc = ["amine", "sara"]
    grp_gc = get_id("groups", "name", "Génie Civil")
    
    # MIPC
    stu_mipc = ["mehdi", "mariam"]
    grp_mipc = get_id("groups", "name", "MIPC S6")
    
    assignments = [
        (stu_ad, grp_ad, "LST AD"),
        (stu_idai, grp_idai, "IDAI"),
        (stu_ssd, grp_ssd, "SSD"),
        (stu_mid, grp_mid, "MID"),
        (stu_gc, grp_gc, "Génie Civil"),
        (stu_mipc, grp_mipc, "MIPC"),
    ]
    
    count = 0
    for students, group_id, group_name in assignments:
        if not group_id:
            print(f"⚠️ Groupe {group_name} introuvable, impossible d'assigner les étudiants.")
            continue
            
        for username in students:
            # Get user ID
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            res = cursor.fetchone()
            if res:
                user_id = res['id']
                try:
                    cursor.execute("""
                        INSERT INTO student_groups (user_id, group_id)
                        VALUES (?, ?)
                    """, (user_id, group_id))
                    count += 1
                except sqlite3.IntegrityError:
                    pass
    
    conn.commit()
    conn.close()
    print(f"✓ {count} étudiants assignés à leurs groupes respectifs")

def main():
    """Fonction principale de peuplement"""
    print("\n" + "="*60)
    print("   PEUPLEMENT BASE DE DONNÉES - FORMAT FST TANGER")
    print("="*60 + "\n")
    
    reset_and_setup_database()
    insert_users()
    insert_instructors()
    insert_rooms()
    insert_subjects()
    insert_groups()
    insert_subject_relations()
    insert_student_group_relations()
    insert_timetable_fst()
    
    print("\n" + "="*60)
    print("   PEUPLEMENT TERMINÉ AVEC SUCCÈS!")
    print("="*60)
    print("\nFilières disponibles pour l'export PDF:")
    print("  - LST AD")
    print("  - IDAI")
    print("  - SSD")
    print("  - MID")
    print("  - Génie Civil")
    print("  - MIPC")
    print("\nConnectez-vous avec: admin / admin123")
    print("Puis allez dans 'Exporter Données' pour générer les PDF.")

if __name__ == "__main__":
    main()
