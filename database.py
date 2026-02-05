import sqlite3
import bcrypt
import os

# Nom du fichier de la base de données
DB_NAME = 'university_schedule.db'

# Constante pour les jours de la semaine (pour l'affichage)
DAYS = {1: "Lundi", 2: "Mardi", 3: "Mercredi", 4: "Jeudi", 5: "Vendredi"}

# --- 1. FONCTIONS DE BASE ET SETUP ---

def setup():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Activer les clés étrangères
    cursor.execute("PRAGMA foreign_keys = ON;")

    # ------------------ TABLE UTILISATEURS ------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('admin', 'enseignant', 'etudiant')),
            full_name TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ------------------ TABLE ENSEIGNANTS ------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instructors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, 
            name TEXT NOT NULL, 
            speciality TEXT,
            unavailable_slots TEXT, 
            active BOOLEAN NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """)

    # ------------------ TABLE SALLES ------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            equipments TEXT,
            active BOOLEAN NOT NULL DEFAULT 1 CHECK (active IN (0,1)),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ------------------ TABLE MATIÈRES ------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code TEXT NOT NULL UNIQUE,
            hours_total INTEGER NOT NULL,
            type TEXT NOT NULL,
            required_equipment TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ------------------ TABLE GROUPES ------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            student_count INTEGER NOT NULL,
            filiere TEXT NOT NULL,
            active BOOLEAN NOT NULL DEFAULT 1 CHECK (active IN (0,1)),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # ------------------ TABLE EMPLOI DU TEMPS ------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS timetable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            instructor_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            day INTEGER NOT NULL,
            start_hour INTEGER NOT NULL,
            duration INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            FOREIGN KEY(course_id) REFERENCES subjects(id),
            FOREIGN KEY(instructor_id) REFERENCES instructors(id),
            FOREIGN KEY(group_id) REFERENCES groups(id),
            FOREIGN KEY(room_id) REFERENCES rooms(id),
            FOREIGN KEY(created_by) REFERENCES users(id)
        );
    """)

    # ------------------ TABLE INDISPONIBILITÉS ENSEIGNANTS ------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teacher_unavailability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instructor_id INTEGER NOT NULL,
            day INTEGER NOT NULL,
            start_hour INTEGER NOT NULL,
            duration INTEGER NOT NULL,
            reason TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(instructor_id) REFERENCES instructors(id)
        );
    """)

    # ------------------ TABLE RESERVATIONS ------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            instructor_id INTEGER NOT NULL,
            room_id INTEGER,
            group_id INTEGER,
            day INTEGER NOT NULL,
            start_hour INTEGER NOT NULL,
            duration INTEGER NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            approved_by INTEGER,
            approved_at DATETIME,
            FOREIGN KEY(instructor_id) REFERENCES instructors(id),
            FOREIGN KEY(room_id) REFERENCES rooms(id),
            FOREIGN KEY(group_id) REFERENCES groups(id),
            FOREIGN KEY(approved_by) REFERENCES users(id)
        );
    """)

    # ------------------ RELATION MATIÈRES ↔ GROUPES ------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subject_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(subject_id, group_id), 
            FOREIGN KEY(subject_id) REFERENCES subjects(id),
            FOREIGN KEY(group_id) REFERENCES groups(id)
        );
    """)

    # ------------------ RELATION MATIÈRES ↔ ENSEIGNANTS ------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subject_instructors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            instructor_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(subject_id, instructor_id), 
            FOREIGN KEY(subject_id) REFERENCES subjects(id),
            FOREIGN KEY(instructor_id) REFERENCES instructors(id)
        );
    """)

    # ------------------ RELATION ÉTUDIANTS ↔ GROUPES ------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, group_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(group_id) REFERENCES groups(id)
        );
    """)

    # ------------------ TRIGGERS POUR updated_at ------------------
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_users_timestamp 
        AFTER UPDATE ON users
        FOR EACH ROW
        BEGIN
            UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_instructors_timestamp 
        AFTER UPDATE ON instructors
        FOR EACH ROW
        BEGIN
            UPDATE instructors SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_rooms_timestamp 
        AFTER UPDATE ON rooms
        FOR EACH ROW
        BEGIN
            UPDATE rooms SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_subjects_timestamp 
        AFTER UPDATE ON subjects
        FOR EACH ROW
        BEGIN
            UPDATE subjects SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_groups_timestamp 
        AFTER UPDATE ON groups
        FOR EACH ROW
        BEGIN
            UPDATE groups SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_timetable_timestamp 
        AFTER UPDATE ON timetable
        FOR EACH ROW
        BEGIN
            UPDATE timetable SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_teacher_unavailability_timestamp 
        AFTER UPDATE ON teacher_unavailability
        FOR EACH ROW
        BEGIN
            UPDATE teacher_unavailability SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
    """)

    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_reservations_timestamp 
        AFTER UPDATE ON reservations
        FOR EACH ROW
        BEGIN
            UPDATE reservations SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
    """)


    # ------------------ ADMIN PAR DÉFAUT ------------------
    cursor.execute("SELECT count(*) FROM users WHERE role='admin'")
    if cursor.fetchone()[0] == 0:
        print("Création de l'administrateur par défaut...")
        password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
        cursor.execute("""
            INSERT INTO users (username, password, role, full_name)
            VALUES (?, ?, ?, ?)
        """, ("admin", password_hash, "admin", "Administrateur Système"))
        conn.commit()
    
    conn.close()
    print("Base de données initialisée avec succès (avec timestamps).")

def getConnection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row 
    return conn

# --- 2. FONCTIONS UTILITAIRES DE RÉCUPÉRATION D'ID ---

def get_user_id_by_username(username):
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    return result['id'] if result else None

def get_id_by_name(table, name_col, name_value):
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {table} WHERE {name_col} = ?", (name_value,))
    result = cursor.fetchone()
    conn.close()
    return result['id'] if result else None

# --- 3. FONCTIONS D'INSERTION SPÉCIFIQUES ---

# --- USERS ---
def insert_user_with_id(user_id, username, password, role, full_name=None):
    conn = getConnection()
    cursor = conn.cursor()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute("""
            INSERT INTO users (id, username, password, role, full_name)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, password_hash, role, full_name))
        conn.commit()
        return user_id
    except sqlite3.IntegrityError: return None
    finally: conn.close()

def populate_users():
    print("\n--- Remplissage des utilisateurs (Étudiants, Profs, Scolarité) ---")
    # Étudiants 
    insert_user_with_id(2601, "zelmaymouni", "pass123", "etudiant", "Zakariae El Maymouni")
    insert_user_with_id(2602, "rsaidi", "pass123", "etudiant", "Romaissae Saidi")
    insert_user_with_id(2603, "fkastit", "pass123", "etudiant", "Fatima Zahrae Kastit")
    insert_user_with_id(2604, "myassine", "pass123", "etudiant", "Mohamed Yassine")
    insert_user_with_id(2605, "yassine", "pass123", "etudiant", "Yassine")
    
    noms_ar = [
        (2606, "ssalman", "Salma Salman"), (2607, "imad", "Imad"), (2608, "ayman", "Ayman"),
        (2609, "janat", "Janat"), (2610, "yassmine", "Yassmine"), (2611, "houda", "Houda"),
        (2612, "badar", "Badar"), (2613, "houssam", "Houssam"), (2614, "ilyas", "Ilyas"),
        (2615, "hajar", "Hajar")
    ]
    for uid, uname, full in noms_ar:
        insert_user_with_id(uid, uname, "pass123", "etudiant", full)

    # Professeurs 
    insert_user_with_id(2207, "skhalissa", "prof123", "enseignant", "Sanae Khali Issa")
    insert_user_with_id(2208, "obaida", "prof123", "enseignant", "Ouafae Baida")
    insert_user_with_id(2209, "mezzeyanni", "prof123", "enseignant", "Mustapha Ezzeyanni")
    insert_user_with_id(2210, "maitlkbir", "prof123", "enseignant", "Mohamed Ait Lkbir")
    insert_user_with_id(2211, "srachafi", "prof123", "enseignant", "Said Rachafi")

    # les admins 
    insert_user_with_id(2001, "mdiani", "admin123", "admin", "Mustapha Diani")
    insert_user_with_id(2002, "mjebilo", "admin123", "admin", "Mohamed Jebilo")
    insert_user_with_id(2003, "ibtissame", "admin123", "admin", "Ibtissame")
    insert_user_with_id(2004, "rachid", "admin123", "admin", "Rachid")

# --- INSTRUCTORS ---
def insert_instructor(user_id, name, speciality, unavailable_slots="", active=1):
    conn = getConnection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO instructors (user_id, name, speciality, unavailable_slots, active)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, name, speciality, unavailable_slots, active))
        instructor_id = cursor.lastrowid
        conn.commit()
        print(f"Instructeur inséré: {name} (ID: {instructor_id})")
        return instructor_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def populate_instructors():
    print("\n--- Remplissage des instructeurs ---")
    # Utilisons les noms d'utilisateurs créés dans populate_users()
    user_sanae = get_user_id_by_username("skhalissa")
    user_ouafae = get_user_id_by_username("obaida")
    user_ezzey = get_user_id_by_username("mezzeyanni")
    
    if user_sanae: insert_instructor(user_sanae, "Sanae Khali Issa", "IA/ML")
    if user_ouafae: insert_instructor(user_ouafae, "Ouafae Baida", "Bases de Données")
    if user_ezzey: insert_instructor(user_ezzey, "Mustapha Ezzeyanni", "Informatique")

# --- ROOMS ---
def insert_room(name, room_type, capacity, equipments="", active=1):
    conn = getConnection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO rooms (name, type, capacity, equipments, active)
            VALUES (?, ?, ?, ?, ?)
        """, (name, room_type, capacity, equipments, active))
        room_id = cursor.lastrowid
        conn.commit()
        print(f"Salle insérée: {name} (Capacité: {capacity})")
        return room_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def populate_rooms():
    print("\n--- Remplissage des Amphis et Salles ---")
    # Amphis
    for i in range(1, 7):
        cap = 300 if i >= 5 else 200
        insert_room(f"Amphi {i}", "Amphithéâtre", cap)
    
    # Salles B (Math & Chimie)
    for i in range(1, 25):
        insert_room(f"B{i:02d}", "Salle Cours (Math/Chim)", 40)
    
    # Salles C (Math & Chimie)
    for i in range(1, 21):
        insert_room(f"C{i:02d}", "Salle Cours (Math/Chim)", 40)

    # Salles E (Informatique)
    for i in range(10, 25):
        insert_room(f"E{i}", "Salle TP (Informatique)", 30, "PC")

    # Salles F (Génie Civil / DEUST)
    for i in range(1, 15):
        insert_room(f"F{i:02d}", "Salle Cours (Civil/DEUST)", 50)

# --- SUBJECTS ---
def insert_subject(name, code, hours_total, subject_type, required_equipment=""):
    conn = getConnection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO subjects (name, code, hours_total, type, required_equipment)
            VALUES (?, ?, ?, ?, ?)
        """, (name, code, hours_total, subject_type, required_equipment))
        subject_id = cursor.lastrowid
        conn.commit()
        print(f"Matière insérée: {name} ({code})")
        return subject_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def populate_subjects():
    print("\n--- Remplissage des Modules ---")
    modules = [
        ("Machine Learning", "AD51", 40, "CM/TP"),
        ("Structure des Données", "AD52", 36, "CM/TD"),
        ("Bases de Données", "AD53", 36, "CM/TP"),
        ("Python", "AD54", 30, "TP"),
        ("Développement", "AD55", 40, "TP"),
        ("Soft Skills", "AD56", 20, "CM"),
        ("Analyse 1", "M01", 45, "CM/TD"),
        ("Analyse 2", "M02", 45, "CM/TD"),
        ("Algèbre", "M03", 45, "CM/TD"),
        ("Mécanique des Solides", "P01", 40, "CM/TD")
    ]
    for name, code, hours, stype in modules:
        insert_subject(name, code, hours, stype)

# --- GROUPS ---
def insert_group(name, student_count, filiere, active=1):
    conn = getConnection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO groups (name, student_count, filiere, active)
            VALUES (?, ?, ?, ?)
        """, (name, student_count, filiere, active))
        group_id = cursor.lastrowid
        conn.commit()
        print(f"Groupe inséré: {name}")
        return group_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def populate_groups():
    print("\n--- Remplissage des Filières ---")
    filieres = ["LST AD", "IDAI", "CIVIL", "TAC", "SSD", "MID", "MIPC", "BCG", "MIP", "GEGM"]
    for f in filieres:
        insert_group(f, 40, f)

# --- RELATIONS (JOINTURES) ---

def insert_subject_group(subject_id, group_id):
    """ Associe une matière à un groupe. """
    conn = getConnection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO subject_groups (subject_id, group_id)
            VALUES (?, ?)
        """, (subject_id, group_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False 
    finally:
        conn.close()

def populate_subject_groups():
    print("\n--- Remplissage des relations Matières ↔ Groupes ---")
    
    group_ad = get_id_by_name("groups", "name", "LST AD")
    sub_ml = get_id_by_name("subjects", "code", "AD51") # Code correct
    sub_db = get_id_by_name("subjects", "code", "AD53") # Code correct

    if sub_ml and group_ad: 
        insert_subject_group(sub_ml, group_ad)
        print("Lien ML <-> LST AD créé")

def insert_subject_instructor(subject_id, instructor_id):
    """ Associe un enseignant à une matière (expertise). """
    conn = getConnection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO subject_instructors (subject_id, instructor_id)
            VALUES (?, ?)
        """, (subject_id, instructor_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def populate_subject_instructors():
    print("\n--- Remplissage des relations Matières ↔ Enseignants ---")
    
    # Récupérer les ID des instructeurs créés
    inst_sanae = get_id_by_name("instructors", "name", "Sanae Khali Issa")
    inst_ouafae = get_id_by_name("instructors", "name", "Ouafae Baida")
    inst_ezzey = get_id_by_name("instructors", "name", "Mustapha Ezzeyanni")
    
    # Récupérer les ID des matières créées
    sub_ml = get_id_by_name("subjects", "code", "AD51")    # Machine Learning
    sub_struct = get_id_by_name("subjects", "code", "AD52") # Structure Données
    sub_bd = get_id_by_name("subjects", "code", "AD53")     # Bases de Données
    sub_py = get_id_by_name("subjects", "code", "AD54")     # Python
    sub_dev = get_id_by_name("subjects", "code", "AD55")    # Développement
    
    # Associer les compétences
    # Sanae -> ML
    if sub_ml and inst_sanae: insert_subject_instructor(sub_ml, inst_sanae)
    
    # Ouafae -> BD
    if sub_bd and inst_ouafae: insert_subject_instructor(sub_bd, inst_ouafae)
    
    # Mustapha -> Python, Dev, Structure Données
    if inst_ezzey:
        if sub_py: insert_subject_instructor(sub_py, inst_ezzey)
        if sub_dev: insert_subject_instructor(sub_dev, inst_ezzey)
        if sub_struct: insert_subject_instructor(sub_struct, inst_ezzey)
    
    print("--- Relations Matières ↔ Enseignants remplies correctement. ---")

# --- RELATION ÉTUDIANTS ↔ GROUPES ---

def insert_student_group(user_id, group_id):
    """ Associe un étudiant à un groupe. """
    conn = getConnection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO student_groups (user_id, group_id)
            VALUES (?, ?)
        """, (user_id, group_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def populate_student_groups():
    """Assigne les étudiants à leurs groupes respectifs."""
    print("\n--- Remplissage des relations Étudiants ↔ Groupes ---")
    
    # Récupérer les groupes
    group_ad = get_id_by_name("groups", "name", "LST AD")
    group_idai = get_id_by_name("groups", "name", "IDAI")
    group_mipc = get_id_by_name("groups", "name", "MIPC")
    group_ssd = get_id_by_name("groups", "name", "SSD")
    
    # Récupérer les étudiants par leur username
    students_ad = ["zelmaymouni", "rsaidi", "fkastit", "myassine", "yassine"]
    students_idai = ["ssalman", "imad", "ayman"]
    students_mipc = ["janat", "yassmine", "houda"]
    students_ssd = ["badar", "houssam", "ilyas", "hajar"]
    
    # Assigner les étudiants aux groupes
    for username in students_ad:
        user_id = get_user_id_by_username(username)
        if user_id and group_ad:
            insert_student_group(user_id, group_ad)
            print(f"Étudiant {username} -> LST AD")
    
    for username in students_idai:
        user_id = get_user_id_by_username(username)
        if user_id and group_idai:
            insert_student_group(user_id, group_idai)
            print(f"Étudiant {username} -> IDAI")
    
    for username in students_mipc:
        user_id = get_user_id_by_username(username)
        if user_id and group_mipc:
            insert_student_group(user_id, group_mipc)
            print(f"Étudiant {username} -> MIPC")
    
    for username in students_ssd:
        user_id = get_user_id_by_username(username)
        if user_id and group_ssd:
            insert_student_group(user_id, group_ssd)
            print(f"Étudiant {username} -> SSD")
    
    print("--- Relations Étudiants ↔ Groupes remplies correctement. ---")

# --- FONCTION CRITIQUE : VÉRIFICATION DE CONFLIT D'HORAIRE ---

def check_conflict(instructor_id, group_id, room_id, day, start_hour, duration):
    conn = getConnection()
    cursor = conn.cursor()
    end_hour = start_hour + duration
    
    # 1. Vérification des conflits dans la table 'timetable'
    # Conflit si un enregistrement existant chevauche la nouvelle plage [start_hour, end_hour]
    # (Existing_Start < New_End) AND (New_Start < Existing_End)
    
    query = """
    SELECT 
        'Enseignant' AS type, instructor_id AS entity_id 
    FROM timetable 
    WHERE day = ? AND instructor_id = ? 
    AND (start_hour < ?) AND (? < start_hour + duration)
    UNION ALL
    SELECT 
        'Groupe', group_id
    FROM timetable 
    WHERE day = ? AND group_id = ?
    AND (start_hour < ?) AND (? < start_hour + duration)
    UNION ALL
    SELECT 
        'Salle', room_id
    FROM timetable 
    WHERE day = ? AND room_id = ?
    AND (start_hour < ?) AND (? < start_hour + duration);
    """
    
    params = [
        day, instructor_id, end_hour, start_hour,
        day, group_id, end_hour, start_hour,
        day, room_id, end_hour, start_hour
    ]
    
    cursor.execute(query, params)
    conflict = cursor.fetchone()
    
    if conflict:
        conn.close()
        return f"Conflit d'horaire existant pour l'entité : {conflict['type']} (ID: {conflict['entity_id']})."

    # 2. Vérification des indisponibilités de l'enseignant (teacher_unavailability)
    unavail_query = """
    SELECT 
        id
    FROM teacher_unavailability 
    WHERE instructor_id = ? AND day = ? 
    AND (start_hour < ?) AND (? < start_hour + duration);
    """
    unavail_params = [instructor_id, day, end_hour, start_hour]
    
    cursor.execute(unavail_query, unavail_params)
    unavailability = cursor.fetchone()
    
    conn.close()
    
    if unavailability:
        return "L'enseignant est marqué comme indisponible sur cette plage horaire."
        
    return None # Aucun conflit détecté

# --- TIMETABLE (EMPLOI DU TEMPS) ---

def insert_schedule_slot(course_id, instructor_id, group_id, room_id, day, start_hour, duration, created_by=None):
    # D'abord, vérifier les conflits avant l'insertion
    conflict_message = check_conflict(instructor_id, group_id, room_id, day, start_hour, duration)
    
    if conflict_message:
        print(f"Échec de l'insertion : {conflict_message}")
        return False
        
    conn = getConnection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO timetable (course_id, instructor_id, group_id, room_id, day, start_hour, duration, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (course_id, instructor_id, group_id, room_id, day, start_hour, duration, created_by))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Erreur d'intégrité lors de l'insertion d'un créneau: {e}")
        return False
    finally:
        conn.close()

def populate_timetable():
    print("\n--- Remplissage de l'Emploi du Temps (timetable) ---")

    # 1. Récupération de l'ID Admin (Scolarité)
    admin_id = get_user_id_by_username("mdiani") # Utilise l'un des nouveaux IDs admin

    # 2. Récupération des IDs Enseignants
    prof_sanae = get_id_by_name("instructors", "name", "Sanae Khali Issa")
    prof_ouafae = get_id_by_name("instructors", "name", "Ouafae Baida")
    prof_ezzeyanni = get_id_by_name("instructors", "name", "Mustapha Ezzeyanni")
    prof_aitlkbir = get_id_by_name("instructors", "name", "Mohamed Ait Lkbir")

    # 3. Récupération des IDs Groupes (Filières)
    group_ad = get_id_by_name("groups", "name", "LST AD")
    group_mipc = get_id_by_name("groups", "name", "MIPC")
    group_idai = get_id_by_name("groups", "name", "IDAI")

    # 4. Récupération des IDs Modules
    sub_ml = get_id_by_name("subjects", "code", "AD51")     # Machine Learning
    sub_db = get_id_by_name("subjects", "code", "AD53")     # Bases de données
    sub_py = get_id_by_name("subjects", "code", "AD54")     # Python
    sub_m01 = get_id_by_name("subjects", "code", "M01")    # Analyse 1

    # 5. Récupération des IDs Salles/Amphis
    amphi_1 = get_id_by_name("rooms", "name", "Amphi 1")
    amphi_5 = get_id_by_name("rooms", "name", "Amphi 5")
    salle_e10 = get_id_by_name("rooms", "name", "E10")     # Informatique
    salle_b01 = get_id_by_name("rooms", "name", "B01")     # Math

    # --- PLANIFICATION DES COURS ---

    # LUNDI (Jour 1)
    if all([sub_ml, prof_sanae, group_ad, amphi_1]):
        # CM Machine Learning pour LST AD
        insert_schedule_slot(sub_ml, prof_sanae, group_ad, amphi_1, 1, 8, 2, admin_id)

    if all([sub_m01, prof_aitlkbir, group_mipc, amphi_5]):
        # CM Analyse 1 pour MIPC (Amphi 5 - Grande capacité)
        insert_schedule_slot(sub_m01, prof_aitlkbir, group_mipc, amphi_5, 1, 10, 2, admin_id)

    # MARDI (Jour 2)
    if all([sub_py, prof_ezzeyanni, group_ad, salle_e10]):
        # TP Python en salle informatique E10
        insert_schedule_slot(sub_py, prof_ezzeyanni, group_ad, salle_e10, 2, 14, 3, admin_id)

    # MERCREDI (Jour 3)
    if all([sub_db, prof_ouafae, group_idai, salle_e10]):
        # Bases de données pour IDAI
        insert_schedule_slot(sub_db, prof_ouafae, group_idai, salle_e10, 3, 9, 2, admin_id)

    # JEUDI (Jour 4)
    if all([sub_ml, prof_sanae, group_ad, salle_e10]):
        # Travaux Pratiques ML pour LST AD
        insert_schedule_slot(sub_ml, prof_sanae, group_ad, salle_e10, 4, 10, 2, admin_id)

    # --- TEST DE CONFLIT ---
    # On tente de mettre un cours dans l'Amphi 1 alors qu'il est déjà pris le Lundi à 8h
    if all([sub_db, prof_ouafae, group_ad, amphi_1]):
        print("\n--- Test de conflit de salle (Amphi 1 déjà occupé) ---")
        insert_schedule_slot(sub_db, prof_ouafae, group_ad, amphi_1, 1, 9, 2, admin_id)

    print("\n--- Emploi du Temps mis à jour avec les professeurs et modules réels. ---")

# --- 4. FONCTION MAIN ET EXÉCUTION ---

def main():
    """
    Fonction principale pour initialiser la BD et la remplir avec toutes les données de démonstration.
    """
    # Optionnel: Supprimer l'ancienne BD pour repartir de zéro à chaque exécution
    # Optionnel: Supprimer l'ancienne BD pour repartir de zéro à chaque exécution
    # if os.path.exists(DB_NAME):
    #    os.remove(DB_NAME)
    #    print(f"Ancien fichier {DB_NAME} supprimé.")

    # 1. Initialisation (Création des tables et Admin)
    setup() 
    
    # 2. Remplissage des tables principales 
    populate_users() 
    populate_instructors()
    populate_rooms()
    populate_subjects()
    populate_groups()

    # 3. Remplissage des tables de relations 
    populate_subject_groups()
    populate_subject_instructors()
    populate_student_groups()  # Association étudiants -> groupes
    
    # 4. Remplissage de l'Emploi du Temps (inclut désormais la vérification des conflits)
    populate_timetable()

    # --- VÉRIFICATION FINALE ---
    print("\n\n--- VÉRIFICATION FINALE DES DONNÉES EN BD ---")
    conn = getConnection()
    
    # Affichage des statistiques
    print(f"\nNombre total d'utilisateurs: {conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]}")
    print(f"Nombre total d'instructeurs: {conn.execute('SELECT COUNT(*) FROM instructors').fetchone()[0]}")
    print(f"Nombre total de matières: {conn.execute('SELECT COUNT(*) FROM subjects').fetchone()[0]}")
    print(f"Nombre total de créneaux dans l'emploi du temps: {conn.execute('SELECT COUNT(*) FROM timetable').fetchone()[0]}")
    
    # Affichage détaillé des créneaux avec timestamps
    print("\n--- Créneaux de l'Emploi du Temps Insérés (avec timestamps) ---")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            t.day, t.start_hour, t.duration,
            s.name AS subject_name, 
            i.name AS instructor_name,
            g.name AS group_name,
            r.name AS room_name,
            t.created_at,
            t.updated_at
        FROM timetable t
        JOIN subjects s ON t.course_id = s.id
        JOIN instructors i ON t.instructor_id = i.id
        JOIN groups g ON t.group_id = g.id
        JOIN rooms r ON t.room_id = r.id
        ORDER BY t.day, t.start_hour, g.name
    """)
    
    for row in cursor.fetchall():
        end_hour = row['start_hour'] + row['duration']
        day_name = DAYS.get(row['day'], 'Inconnu')
        print(f"**{day_name} {row['start_hour']:02d}h-{end_hour:02d}h** | Matière: {row['subject_name']} ({row['group_name']}) | Salle: {row['room_name']} | Enseignant: {row['instructor_name']} | Créé: {row['created_at']}")
    
    conn.close() 
    print("\nExécution du script de base de données terminée avec succès.")

if __name__ == "__main__":
    main()
