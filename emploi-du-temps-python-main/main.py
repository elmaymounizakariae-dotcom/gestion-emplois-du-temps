"""
main.py - Version complète avec tous les rôles
"""

print("Projet Python - Gestion d'emploi du temps")
print("========================================")

# Imports 
from database import setup, getConnection
from controllers.admin_controller import AdminController
from controllers.teacher_controller import TeacherController
from controllers.student_controller import StudentController
import bcrypt

def login():
    """Fonction de connexion simple"""
    print("\n=== CONNEXION ===")
    username = input("Nom d'utilisateur: ")
    password = input("Mot de passe: ")
    
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, username, password, role, full_name 
        FROM users WHERE username = ?
    """, (username,))
    
    user = cursor.fetchone()
    conn.close()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return {
            'id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'full_name': user['full_name']
        }
    else:
        print(" Identifiants incorrects!")
        return None

def menu_admin(user):
    admin = AdminController(admin_id=user['id'])
    print(f"\n=== MENU ADMIN - {user['full_name']} ===")
    
    while True:
        print("\n0. GENERER PLANNING AUTOMATIQUE (IA)")
        print("1. Créer un créneau")
        print("2. Valider une réservation")
        print("3. Rejeter une réservation")
        print("4. Voir les statistiques")
        print("5. Exporter statistiques (Excel)")
        print("6. Exporter statistiques (PDF)")
        print("7. Afficher détails réservation")
        print("8. Voir réservations en attente")
        print("9. Déconnexion")

        choix = input("Choix : ")

        if choix == "0":
            confirm = input("Cela va effacer tout l'emploi du temps actuel. Continuer ? (o/n) : ")
            if confirm.lower() == 'o':
                msg = admin.generer_planning_complet()
                print(f"\n>> {msg}")

        elif choix == "1":
            course_id = int(input("ID matière : "))
            instructor_id = int(input("ID enseignant : "))
            group_id = int(input("ID groupe : "))
            room_id = int(input("ID salle : "))
            day = int(input("Jour (1=Lundi...5=Vendredi) : "))
            start_hour = int(input("Heure début (ex: 8) : "))
            duration = int(input("Durée (en heures) : "))
            admin.creer_creneau(course_id, instructor_id, group_id, room_id, day, start_hour, duration)

        elif choix == "2":
            res_id = int(input("ID de la réservation à valider : "))
            confirm = input("Confirmer la validation ? (o/n) : ")
            if confirm.lower() == "o":
                admin.valider_reservation(res_id)

        elif choix == "3":
            res_id = int(input("ID de la réservation à rejeter : "))
            confirm = input("Confirmer le rejet ? (o/n) : ")
            if confirm.lower() == "o":
                admin.rejeter_reservation(res_id)

        elif choix == "4":
            admin.afficher_statistiques()

        elif choix == "5":
            admin.exporter_statistiques_excel()

        elif choix == "6":
            admin.exporter_statistiques_pdf()
            
        elif choix == "7":
            res_id = int(input("ID de la réservation : "))
            admin.afficher_details_reservation(res_id)
            
        elif choix == "8":
            admin.afficher_reservations_en_attente()
            
        elif choix == "9":
            break

def menu_teacher(user):
    teacher = TeacherController(user_id=user['id'])
    print(f"\n=== MENU ENSEIGNANT - {user['full_name']} ===")
    
    while True:
        print("\n1. Consulter mon emploi du temps")
        print("2. Soumettre une réservation")
        print("3. Déclarer une indisponibilité")
        print("4. Rechercher une salle disponible")
        print("5. Voir le statut de mes réservations")
        print("6. Déconnexion")

        choix = input("Choix : ")

        if choix == "1":
            result = teacher.get_teacher_timetable()
            if result["success"]:
                for day, slots in result["timetable"].items():
                    if slots:
                        print(f"\n{day}:")
                        for slot in slots:
                            print(f"  {slot['heure']} - {slot['matiere']} avec {slot['groupe']} en {slot['salle']}")

        elif choix == "2":
            room_id = int(input("ID de la salle : "))
            group_id = int(input("ID du groupe : "))
            day = int(input("Jour (1-5) : "))
            start_hour = int(input("Heure de début (8-18) : "))
            duration = int(input("Durée (en heures, 1-4) : "))
            reason = input("Raison (optionnel) : ")
            result = teacher.submit_reservation(room_id, group_id, day, start_hour, duration, reason)
            print(result["message"])

        elif choix == "3":
            day = int(input("Jour (1-5) : "))
            start_hour = int(input("Heure de début (8-18) : "))
            duration = int(input("Durée (en heures) : "))
            reason = input("Raison (optionnel) : ")
            result = teacher.declare_unavailability(day, start_hour, duration, reason)
            print(result["message"])

        elif choix == "4":
            day = int(input("Jour (1-5) : "))
            start_hour = int(input("Heure de début (8-18) : "))
            duration = int(input("Durée (en heures) : "))
            min_capacity = int(input("Capacité minimale (défaut: 30) : ") or 30)
            result = teacher.search_available_room(day, start_hour, duration, min_capacity)
            if result["success"]:
                if result["rooms"]:
                    for room in result["rooms"]:
                        print(f"  Salle {room['nom']} (type: {room['type']}, capacité: {room['capacité']})")
                else:
                    print("Aucune salle disponible correspondant aux critères.")

        elif choix == "5":
            result = teacher.get_reservation_status()
            if result["success"]:
                for res in result["reservations"]:
                    print(f"  Réservation {res['id']} : {res['jour']} {res['horaire']} - Statut: {res['statut']}")

        elif choix == "6":
            break

def menu_student(user):
    student = StudentController(user_id=user['id'])
    print(f"\n=== MENU ÉTUDIANT - {user['full_name']} ===")
    
    while True:
        print("\n1. Consulter l'emploi du temps de mon groupe")
        print("2. Rechercher une salle libre")
        print("3. Voir l'emploi du temps d'aujourd'hui")
        print("4. Déconnexion")

        choix = input("Choix : ")

        if choix == "1":
            result = student.get_group_timetable()
            if result["success"]:
                print(f"Emploi du temps du groupe {result['groupe']}:")
                for day, slots in result["emploi_du_temps"].items():
                    if slots:
                        print(f"\n{day}:")
                        for slot in slots:
                            print(f"  {slot['horaire']} - {slot['matiere']} avec {slot['enseignant']} en {slot['salle']}")

        elif choix == "2":
            print("Recherche de salle libre")
            day = input("Jour (1-5, laisser vide pour tous les jours) : ")
            start_hour = input("Heure de début (8-18, laisser vide pour toute la journée) : ")
            duration = input("Durée (en heures, défaut: 2) : ") or 2
            
            if day and start_hour:
                result = student.search_free_room(int(day), int(start_hour), int(duration))
                if result["success"] and result["rooms"]:
                    for room in result["rooms"]:
                        print(f"  Salle {room['nom']} (type: {room['type']}, capacité: {room['capacité']}) - Disponible à {room['horaire']}")
                else:
                    print("Aucune salle libre à ce créneau.")
            elif day:
                result = student.search_free_room(day=int(day))
                if result["success"] and result["rooms"]:
                    for room in result["rooms"]:
                        print(f"  Salle {room['nom']} (type: {room['type']}, capacité: {room['capacité']}) - Créneaux libres: {', '.join(room['creneaux_libres'])}")
            else:
                result = student.search_free_room()
                if result["success"] and result["rooms"]:
                    for room in result["rooms"]:
                        print(f"  Salle {room['nom']} (type: {room['type']}, capacité: {room['capacité']})")

        elif choix == "3":
            result = student.get_today_schedule()
            if result["success"]:
                print(f"Emploi du temps pour {result['jour']}:")
                if result["cours"]:
                    for course in result["cours"]:
                        print(f"  {course['horaire']} - {course['matiere']} avec {course['enseignant']} en {course['salle']}")
                else:
                    print("  Aucun cours aujourd'hui.")

        elif choix == "4":
            break

def main():
    # Initialisation de la base
    print("\nInitialisation de la base de données...")
    setup()
    print("Base de données prête!")
    
    # Peuplement des données de démonstration (optionnel)
    peupler = input("\nVoulez-vous peupler la base avec des données de démonstration ? (o/n): ")
    if peupler.lower() == 'o':
        from database import main as populate_db
        populate_db()
    
    while True:
        print("\n=== MENU PRINCIPAL ===")
        print("1. Se connecter")
        print("2. Quitter")
        
        choix = input("Choix : ")
        
        if choix == "1":
            user = login()
            if user:
                if user['role'] == 'admin':
                    menu_admin(user)
                elif user['role'] == 'enseignant':
                    menu_teacher(user)
                elif user['role'] == 'etudiant':
                    menu_student(user)
        
        elif choix == "2":
            print("À bientôt")
            break
        else:
            print("Choix invalide.")

if __name__ == "__main__":
    main()