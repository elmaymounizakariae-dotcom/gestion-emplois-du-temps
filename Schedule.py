
import copy
import random
from random import randint
from database import getConnection

# Configuration Globale
DAY_HOURS = 11  # 8h à 19h (18h fin de cours + 1h marge)
DAYS_NUM = 5    # Lundi à Vendredi

class CourseClass:
    """
    Représente un cours à planifier (Matière + Groupe + Enseignant).
    """
    def __init__(self, subject, group, instructor):
        self.subject = subject
        self.group = group
        self.instructor = instructor
        
        # Durée par défaut d'une séance (en heures)
        # Gestion des TP/TD vs CM
        if "TP" in subject['type'] or "Projet" in subject['type']:
            self.duration = 3
        else:
            self.duration = 2
            
    def GetDuration(self):
        return self.duration

    def GetProfessor(self):
        return self.instructor

    def GetGroups(self):
        # Retourne une liste pour compatibilité avec le code existant (un cours peut avoir plusieurs groupes)
        return [self.group]

    def GetSubject(self):
        return self.subject

    def IsLabRequired(self):
        return "TP" in self.subject['type']

    def GetNumberOfSeats(self):
        # Capacité nécessaire = taille du groupe
        return self.group['student_count']

    def ProfessorOverlaps(self, other_course):
        return self.instructor['id'] == other_course.instructor['id']

    def GroupsOverlap(self, other_course):
        return self.group['id'] == other_course.group['id']
    
    def __repr__(self):
        return f"Course({self.subject['name']}, {self.group['name']}, {self.instructor['name']})"


class Configuration:
    """
    Charge les données de la BD et sert de contexte pour l'algorithme génétique.
    Pattern Singleton simplifiée.
    """
    _instance = None

    def __init__(self):
        self.rooms = []
        self.course_classes = []
        self.load_data()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_data(self):
        self.rooms = []
        self.course_classes = []
        
        conn = getConnection()
        cursor = conn.cursor()

        # 1. Charger les Salles
        cursor.execute("SELECT * FROM rooms WHERE active=1")
        self.rooms = [dict(row) for row in cursor.fetchall()]

        # 2. Charger les Relations Matière-Groupe (Les cours à donner)
        # On suppose pour cet algo que chaque entrée dans subject_groups génère une nécessité de cours
        # Pour être plus réaliste, on devrait diviser le 'hours_total' par la durée d'une séance
        # pour savoir combien de créneaux générer.
        # Ici, on génère 2 créneaux par matière-groupe par semaine pour simplifier.
        
        cursor.execute("""
            SELECT s.id as s_id, s.name as s_name, s.code, s.type, s.required_equipment,
                   g.id as g_id, g.name as g_name, g.student_count
            FROM subject_groups sg
            JOIN subjects s ON sg.subject_id = s.id
            JOIN groups g ON sg.group_id = g.id
            WHERE g.active=1
        """)
        assignments = cursor.fetchall()

        for a in assignments:
            subject = {
                'id': a['s_id'], 'name': a['s_name'], 'code': a['code'], 
                'type': a['type'], 'required_equipment': a['required_equipment']
            }
            group = {'id': a['g_id'], 'name': a['g_name'], 'student_count': a['student_count']}
            
            # Trouver un prof qualifié
            cursor.execute("""
                SELECT i.id, i.name 
                FROM subject_instructors si
                JOIN instructors i ON si.instructor_id = i.id
                WHERE si.subject_id = ? AND i.active=1
                LIMIT 1
            """, (subject['id'],))
            
            instr_row = cursor.fetchone()
            if instr_row:
                instructor = {'id': instr_row['id'], 'name': instr_row['name']}
                
                # Créer le cours
                # On ajoute plusieurs séances selon le type
                # Si TP: 1 séance de 3h. Si CM/TD: 2 séances de 2h.
                nb_sessions = 1
                if "CM" in subject['type'] and "TD" in subject['type']:
                    nb_sessions = 2
                
                for _ in range(nb_sessions):
                    cc = CourseClass(subject, group, instructor)
                    self.course_classes.append(cc)
            else:
                print(f"Warning: No instructor found for subject {subject['name']}")

        conn.close()

    def GetNumberOfRooms(self):
        return len(self.rooms)

    def GetRoomById(self, index):
        if 0 <= index < len(self.rooms):
            class RoomWrapper:
                def __init__(self, data): self.data = data
                def GetNumberOfSeats(self): return self.data['capacity']
                def IsLab(self): return "PC" in (self.data['equipments'] or "")
                def GetId(self): return self.data['id']
                def wrapper_obj(self): return self.data
            return RoomWrapper(self.rooms[index])
        return None

    def GetCourseClasses(self):
        return self.course_classes

    def GetNumberOfCourseClasses(self):
        return len(self.course_classes)


class Schedule:
    def __init__(self, numberOfCrossoverPoints, mutationSize, crossoverProbability, mutationProbability):
        self.numberOfCrossoverPoints = numberOfCrossoverPoints
        self.mutationSize = mutationSize
        self.crossoverProbability = crossoverProbability
        self.mutationProbability = mutationProbability
        self.fitness = 0
        
        # Référence au Singleton Configuration
        self.config = Configuration.get_instance()
        
        # Slots: Liste plate représentant [Jour * Heure * Salle]
        # Taille = DAYS_NUM * DAY_HOURS * NbSalles
        self.slots = [None] * (DAYS_NUM * DAY_HOURS * self.config.GetNumberOfRooms())
        
        # Criteria: Drapeaux de satisfaction des contraintes
        self.criteria = [False] * (self.config.GetNumberOfCourseClasses() * 5)
        
        # Classes: Dictionnaire {CourseClass object : position_index}
        self.classes = {}

    def copy(self, setupOnly):
        # Création d'une nouvelle instance avec les mêmes paramètres génétiques
        c = Schedule(self.numberOfCrossoverPoints, self.mutationSize, self.crossoverProbability, self.mutationProbability)
        
        if not setupOnly:
            c.slots = copy.deepcopy(self.slots)
            # Attention: CourseClass est un objet, on veut copier la référence ou l'objet ?
            # Ici shallow copy de la dict est suffisant car CourseClass est immuable dans notre contexte
            c.classes = copy.copy(self.classes) 
            c.criteria = copy.copy(self.criteria)
            c.fitness = self.fitness
        return c

    def MakeNewFromPrototype(self):
        new_chromosome = self.copy(True) # setupOnly=True
        
        course_classes = self.config.GetCourseClasses()
        nr = self.config.GetNumberOfRooms()
        
        for cc in course_classes:
            # Essayer de placer le cours aléatoirement
            duration = cc.GetDuration()
            
            # Protection boucle infinie si pas de place
            for _ in range(50): 
                day = randint(0, DAYS_NUM - 1)
                room = randint(0, nr - 1)
                # S'assurer que le cours rentre dans la plage horaire du jour
                time = randint(0, DAY_HOURS - 1 - duration) 
                
                pos = day * nr * DAY_HOURS + room * DAY_HOURS + time
                
                # Vérifier si les slots sont libres (basic check pour initialisation rapide)
                free = True
                for i in range(duration):
                    if new_chromosome.slots[pos + i] is not None:
                        free = False
                        break
                
                if free:
                    for i in range(duration):
                        # On stocke une liste car théoriquement plusieurs cours pourraient être là (collision à résoudre)
                        # Mais pour l'init, on essaye d'éviter.
                        if new_chromosome.slots[pos + i] is None:
                            new_chromosome.slots[pos + i] = [cc]
                        else:
                            new_chromosome.slots[pos + i].append(cc)
                    
                    new_chromosome.classes[cc] = pos
                    break
            
            # Si on n'a pas trouvé de place après 50 essais, on place quand même (le fitness gérera)
            if cc not in new_chromosome.classes:
                 # Placement forcé au début
                 pos = 0 
                 new_chromosome.classes[cc] = pos
                 for i in range(duration):
                     if new_chromosome.slots[pos + i] is None:
                         new_chromosome.slots[pos + i] = [cc]
                     else:
                         new_chromosome.slots[pos + i].append(cc)

        new_chromosome.CalculateFitness()
        return new_chromosome

    def CalculateFitness(self):
        score = 0
        
        nr = self.config.GetNumberOfRooms()
        day_size = DAY_HOURS * nr
        
        ci = 0 # Criteria index
        
        for cc, pos in self.classes.items():
            # Conversion position -> (Jour, Salle, Heure)
            # pos = day * (nr * DAY_HOURS) + room * DAY_HOURS + time
            
            day = pos // day_size
            rem = pos % day_size
            room_idx = rem // DAY_HOURS
            time = rem % DAY_HOURS
            
            duration = cc.GetDuration()
            
            # 1. Vérifier overlapping salle (Soft/Hard collision dans la même salle)
            ro = False
            for i in range(duration):
                slot_content = self.slots[pos + i]
                if slot_content and len(slot_content) > 1:
                    ro = True
                    break
            
            if not ro: score += 1
            self.criteria[ci + 0] = not ro
            
            # 2. Salle assez grande ?
            room_obj = self.config.GetRoomById(room_idx)
            enough_seats = room_obj.GetNumberOfSeats() >= cc.GetNumberOfSeats()
            if enough_seats: score += 1
            self.criteria[ci + 1] = enough_seats
            
            # 3. Labo requis ?
            lab_ok = (not cc.IsLabRequired()) or (cc.IsLabRequired() and room_obj.IsLab())
            if lab_ok: score += 1
            self.criteria[ci + 2] = lab_ok
            
            # 4. & 5. Chevauchement Prof ou Groupe (Hard collision ailleurs)
            po = False # Prof overlap
            go = False # Group overlap
            
            # On doit vérifier tous les Autres cours qui ont lieu en même temps
            # Calcul de la plage de temps absolue: start = day*DAY_HOURS + time
            
            # Optimisation: Au lieu de scanner toute la grille, on regarde les slots parallèles
            # Pour chaque slot occupé par ce cours (pos + i)
            # On doit vérifier les autres salles (room_k) au même moment (time +i) le même jour
            
            for i in range(duration):
                current_time_slot = day * day_size + time + i # Ce n'est pas suffisant, il faut iterer sur les salles
                
                # Base de temps pour ce jour/heure précis
                base_time_absolute = day * nr * DAY_HOURS + (time + i)
                
                # Vérifier toutes les salles pour cet instant t
                for r in range(nr):
                    if r == room_idx: continue # On a déjà checké la salle courante en 1.
                    
                    other_pos = day * nr * DAY_HOURS + r * DAY_HOURS + (time + i)
                    slot_content = self.slots[other_pos]
                    
                    if slot_content:
                        for other_cc in slot_content:
                            if cc != other_cc:
                                if cc.ProfessorOverlaps(other_cc): po = True
                                if cc.GroupsOverlap(other_cc): go = True
            
            if not po: score += 1
            self.criteria[ci + 3] = not po
            
            if not go: score += 1
            self.criteria[ci + 4] = not go
            
            ci += 5
            
        # Normalisation du score (0 à 1)
        # Max score = 5 * nb_classes
        self.fitness = score / (self.config.GetNumberOfCourseClasses() * 5)


    def Mutation(self):
        if random.random() > self.mutationProbability:
            return

        classes_list = list(self.classes.keys())
        nr = self.config.GetNumberOfRooms()
        
        for _ in range(self.mutationSize):
            # Choisir un cours au hasard
            if not classes_list: break
            cc = random.choice(classes_list)
            
            # Retirer l'ancien emplacement
            old_pos = self.classes[cc]
            duration = cc.GetDuration()
            
            for i in range(duration):
                if self.slots[old_pos + i]:
                    # Safe remove
                    try:
                        self.slots[old_pos + i].remove(cc)
                    except ValueError:
                        pass
                    if not self.slots[old_pos + i]:
                        self.slots[old_pos + i] = None
            
            # Choisir un nouvel emplacement
            # Essayer de trouver une place libre
            found = False
            for _ in range(10): 
                day = randint(0, DAYS_NUM - 1)
                room = randint(0, nr - 1)
                time = randint(0, DAY_HOURS - 1 - duration)
                
                new_pos = day * nr * DAY_HOURS + room * DAY_HOURS + time
                
                free = True
                for i in range(duration):
                    if self.slots[new_pos + i] is not None:
                        free = False
                        break
                
                if free:
                    for i in range(duration):
                        if self.slots[new_pos + i] is None:
                            self.slots[new_pos + i] = [cc]
                        else:
                            self.slots[new_pos + i].append(cc)
                    self.classes[cc] = new_pos
                    found = True
                    break
            
            # Si pas trouvé de place "libre", on force aléatoirement (collision)
            if not found:
                day = randint(0, DAYS_NUM - 1)
                room = randint(0, nr - 1)
                time = randint(0, DAY_HOURS - 1 - duration)
                new_pos = day * nr * DAY_HOURS + room * DAY_HOURS + time
                
                for i in range(duration):
                    if self.slots[new_pos + i] is None:
                        self.slots[new_pos + i] = [cc]
                    else:
                        self.slots[new_pos + i].append(cc)
                self.classes[cc] = new_pos

        self.CalculateFitness()

    def Crossover(self, parent2):
        if random.random() > self.crossoverProbability:
            return self.copy(False)
            
        child = self.copy(True) # Setup only
        
        # Liste des cours (clés identiques pour les deux parents)
        keys = list(self.classes.keys())
        # Shuffle pour mixer
        random.shuffle(keys)
        
        # Split en deux sets
        cut = len(keys) // 2
        set1 = keys[:cut]
        set2 = keys[cut:]
        
        # Hériter du Parent 1
        for cc in set1:
            pos = self.classes[cc]
            child.classes[cc] = pos
            duration = cc.GetDuration()
            for i in range(duration):
                if child.slots[pos + i] is None:
                    child.slots[pos + i] = [cc]
                else:
                    child.slots[pos + i].append(cc)
                    
        # Hériter du Parent 2
        for cc in set2:
            pos = parent2.classes[cc]
            # Si le créneau est déjà très occupé ou conflit, on accepte quand même
            # La mutation et fitness régleront ça
            child.classes[cc] = pos
            duration = cc.GetDuration()
            for i in range(duration):
                if child.slots[pos + i] is None:
                    child.slots[pos + i] = [cc]
                else:
                    child.slots[pos + i].append(cc)
        
        child.CalculateFitness()
        return child

class GeneticAlgorithm:
    def __init__(self, population_size=10, mutation_size=2, crossover_prob=0.8, mutation_prob=0.2):
        self.config = Configuration.get_instance()
        self.population = []
        self.generation = 0
        
        # Init population
        prototype = Schedule(2, mutation_size, crossover_prob, mutation_prob)
        for _ in range(population_size):
            self.population.append(prototype.MakeNewFromPrototype())

    def evolve(self, max_generations=1, target_fitness=1.0):
        best_schedule = None
        
        for g in range(max_generations):
            self.generation += 1
            
            # Trier par fitness décroissant
            self.population.sort(key=lambda x: x.fitness, reverse=True)
            best = self.population[0]
            
            # print(f"Generation {self.generation} | Best Fitness: {best.fitness:.3f}")
            
            if best.fitness >= target_fitness:
                return best
            
            best_schedule = best
            
            # Sélection et Reproduction (Elitisme: on garde le meilleur)
            new_population = [best] 
            
            # On remplit le reste
            while len(new_population) < len(self.population):
                # Tournoi simple
                p1 = self.tournament_selection()
                p2 = self.tournament_selection()
                
                child = p1.Crossover(p2)
                child.Mutation()
                
                new_population.append(child)
            
            self.population = new_population
            
        return best_schedule

    def tournament_selection(self):
        # Prendre 3 au hasard et retourner le meilleur
        candidates = random.sample(self.population, 3)
        candidates.sort(key=lambda x: x.fitness, reverse=True)
        return candidates[0]
