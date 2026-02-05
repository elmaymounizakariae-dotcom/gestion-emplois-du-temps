import tkinter as tk
from tkinter import ttk, messagebox
import bcrypt
import sqlite3
from datetime import datetime
from database import getConnection, DAYS

# Import controllers (Corrected paths)
from controllers.admin_controller import AdminController
from controllers.teacher_controller import TeacherController
from controllers.student_controller import StudentController

# Color Palette
BG_COLOR = "#f0f2f5"
SIDEBAR_COLOR = "#2c3e50"
ACCENT_COLOR = "#1abc9c"
TEXT_COLOR = "#2c3e50"
WHITE = "#ffffff"
ERROR_COLOR = "#e74c3c"
SUCCESS_COLOR = "#2ecc71"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestion d'Emploi du Temps Universitaire")
        self.geometry("1400x900")
        self.configure(bg=BG_COLOR)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure("TFrame", background=BG_COLOR)
        self.style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("Segoe UI", 11))
        self.style.configure("Header.TLabel", font=("Segoe UI", 24, "bold"), foreground=SIDEBAR_COLOR)
        self.style.configure("Card.TFrame", background=WHITE, relief="solid", borderwidth=1)
        self.style.configure("Card.TLabel", background=WHITE, foreground=TEXT_COLOR)
        
        self.style.configure("TButton", 
                             font=("Segoe UI", 11), 
                             background=ACCENT_COLOR, 
                             foreground=WHITE, 
                             borderwidth=0, 
                             focuscolor="none")
        self.style.map("TButton", background=[('active', '#16a085')])
        
        self.style.configure("Delete.TButton", background=ERROR_COLOR)
        self.style.map("Delete.TButton", background=[('active', '#c0392b')])
        
        self.style.configure("TEntry", fieldbackground=WHITE, font=("Segoe UI", 11))
        self.style.configure("TCombobox", fieldbackground=WHITE, font=("Segoe UI", 11))
        
        # Treeview Style
        self.style.configure("Treeview", 
                             background=WHITE,
                             foreground=TEXT_COLOR,
                             rowheight=30,
                             fieldbackground=WHITE,
                             font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        
        self.current_user = None
        self.current_frame = None
        
        self.show_login()

    def switch_frame(self, frame_class, *args, **kwargs):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self, *args, **kwargs)
        self.current_frame.pack(fill="both", expand=True)

    def show_login(self):
        self.switch_frame(LoginFrame)

    def login_success(self, user):
        self.current_user = user
        if user['role'] == 'admin':
            self.switch_frame(AdminDashboard)
        elif user['role'] == 'enseignant':
            self.switch_frame(TeacherDashboard)
        elif user['role'] == 'etudiant':
            self.switch_frame(StudentDashboard)

    def logout(self):
        self.current_user = None
        self.show_login()

# --- HELPER FUNCTIONS FOR DB DROPDOWNS ---
def get_all(table, columns="id, name"):
    conn = getConnection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT {columns} FROM {table}")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_days_combo():
    return [(k, v) for k, v in DAYS.items()]

# --- LOGIN ---
class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=BG_COLOR)
        self.master = master
        self.place_widgets()

    def place_widgets(self):
        container = tk.Frame(self, bg=WHITE, padx=60, pady=60)
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        ttk.Label(container, text="Connexion", style="Header.TLabel", background=WHITE).pack(pady=(0, 30))
        
        ttk.Label(container, text="Nom d'utilisateur", background=WHITE).pack(anchor="w")
        self.username_entry = ttk.Entry(container, width=35)
        self.username_entry.pack(pady=(5, 20))
        
        ttk.Label(container, text="Mot de passe", background=WHITE).pack(anchor="w")
        self.password_entry = ttk.Entry(container, width=35, show="*")
        self.password_entry.pack(pady=(5, 30))
        
        ttk.Button(container, text="Se connecter", command=self.login).pack(fill="x", pady=10)
        
        self.username_entry.focus()
        self.master.bind('<Return>', lambda e: self.login())

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        conn = getConnection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password, role, full_name FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        conn.close()
        
        if user_data:
            try:
                if bcrypt.checkpw(password.encode('utf-8'), user_data['password']):
                    user = {
                        'id': user_data['id'],
                        'username': user_data['username'],
                        'role': user_data['role'],
                        'full_name': user_data['full_name']
                    }
                    self.master.unbind('<Return>')
                    self.master.login_success(user)
                    return
            except ValueError: pass
        
        messagebox.showerror("Erreur", "Identifiants incorrects")

# --- BASE DASHBOARD ---
class DashboardFrame(tk.Frame):
    def __init__(self, master, title, role_color="#2c3e50"):
        super().__init__(master, bg=BG_COLOR)
        self.master = master
        self.sidebar_color = role_color
        
        self.setup_layout(title)

    def setup_layout(self, title):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=self.sidebar_color, width=280)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        tk.Label(self.sidebar, text="Univ Schedule", bg=self.sidebar_color, fg=WHITE, 
                 font=("Segoe UI", 20, "bold")).pack(pady=40)
        
        self.sidebar_buttons = tk.Frame(self.sidebar, bg=self.sidebar_color)
        self.sidebar_buttons.pack(fill="both", expand=True)
        
        # Logout
        tk.Button(self.sidebar, text="Déconnexion", command=self.master.logout,
                  bg="#c0392b", fg=WHITE, relief="flat", font=("Segoe UI", 11),
                  padx=20, pady=15).pack(side="bottom", fill="x")

        # Main Content
        self.main_area = tk.Frame(self, bg=BG_COLOR)
        self.main_area.pack(side="right", fill="both", expand=True)
        
        # Header
        header = tk.Frame(self.main_area, bg=WHITE, height=70)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text=title, bg=WHITE, fg=TEXT_COLOR, font=("Segoe UI", 16, "bold")).pack(side="left", padx=30)
        tk.Label(header, text=f"{self.master.current_user['full_name']}", 
                 bg=WHITE, fg="#7f8c8d", font=("Segoe UI", 12)).pack(side="right", padx=30)
        
        # Content Container
        self.content_area = tk.Frame(self.main_area, bg=BG_COLOR)
        self.content_area.pack(fill="both", expand=True, padx=30, pady=30)

    def add_sidebar_button(self, text, command):
        btn = tk.Button(self.sidebar_buttons, text=text, command=command,
                        bg=self.sidebar_color, fg=WHITE, relief="flat", 
                        font=("Segoe UI", 12), padx=30, pady=15, anchor="w")
        btn.pack(fill="x")
        
        def on_enter(e): e.widget['bg'] = "#34495e"
        def on_leave(e): e.widget['bg'] = self.sidebar_color
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

# --- ADMIN DASHBOARD ---
class AdminDashboard(DashboardFrame):
    def __init__(self, master):
        super().__init__(master, "Tableau de bord Administrateur", role_color="#2c3e50")
        self.controller = AdminController(self.master.current_user['id'])
        self.setup_menu()
        self.show_stats()

    def setup_menu(self):
        self.add_sidebar_button("📊 Statistiques", self.show_stats)
        self.add_sidebar_button("🏫 Salles & Occupation", self.show_room_stats)
        self.add_sidebar_button("📅 Créer un Cours (Manuel)", self.show_add_slot)
        self.add_sidebar_button("🤖 Génération Auto", self.show_auto_assign)
        self.add_sidebar_button("✅ Valider Réservations", self.show_validations)
        self.add_sidebar_button("📥 Exporter Données", self.show_export)

    def show_stats(self):
        self.clear_content()
        tk.Label(self.content_area, text="Aperçu Général", font=("Segoe UI", 20, "bold"), bg=BG_COLOR).pack(anchor="w", pady=(0, 20))
        
        stats_frame = tk.Frame(self.content_area, bg=BG_COLOR)
        stats_frame.pack(fill="x")
        
        # Fetch stats directly for dashboard display
        conn = getConnection()
        nb_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        nb_creneaux = conn.execute("SELECT COUNT(*) FROM timetable").fetchone()[0]
        nb_pending = conn.execute("SELECT COUNT(*) FROM reservations WHERE status='PENDING'").fetchone()[0]
        conn.close()

        self.create_stat_card(stats_frame, "Utilisateurs", str(nb_users), 0, click_action=self.show_users_list)
        self.create_stat_card(stats_frame, "Cours Planifiés", str(nb_creneaux), 1, click_action=self.show_full_schedule)
        self.create_stat_card(stats_frame, "Réservations en attente", str(nb_pending), 2, 
                              color=ERROR_COLOR if nb_pending > 0 else ACCENT_COLOR, 
                              click_action=self.show_validations)

    def create_stat_card(self, parent, title, value, col, color=ACCENT_COLOR, click_action=None):
        card = tk.Frame(parent, bg=WHITE, padx=20, pady=20, cursor="hand2")
        card.grid(row=0, column=col, padx=(0, 20), sticky="nsew")
        
        lbl_title = tk.Label(card, text=title, bg=WHITE, fg="#95a5a6", font=("Segoe UI", 12))
        lbl_title.pack(anchor="w")
        
        lbl_val = tk.Label(card, text=value, bg=WHITE, fg=color, font=("Segoe UI", 28, "bold"))
        lbl_val.pack(anchor="w", pady=(10, 0))
        
        if click_action:
            card.bind("<Button-1>", lambda e: click_action())
            lbl_title.bind("<Button-1>", lambda e: click_action())
            lbl_val.bind("<Button-1>", lambda e: click_action())
            
    def show_users_list(self):
        self.clear_content()
        tk.Label(self.content_area, text="Liste des Utilisateurs", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 20))
        
        cols = ("ID", "Nom complet", "Rôle", "Nom d'utilisateur")
        tree = ttk.Treeview(self.content_area, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c)
        tree.pack(fill="both", expand=True)
        
        results = get_all("users", "id, full_name, role, username")
        for r in results:
            tree.insert("", "end", values=tuple(r))
            
        ttk.Button(self.content_area, text="Retour", command=self.show_stats).pack(pady=20)

    def show_full_schedule(self):
        self.clear_content()
        tk.Label(self.content_area, text="Liste Complète des Cours", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 20))
        
        cols = ("Jour", "H", "Durée", "Matière", "Enseignant", "Groupe", "Salle")
        tree = ttk.Treeview(self.content_area, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c)
        tree.column("H", width=50); tree.column("Durée", width=50)
        tree.pack(fill="both", expand=True)
        
        conn = getConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.day, t.start_hour, t.duration, s.name, i.name, g.name, r.name
            FROM timetable t
            JOIN subjects s ON t.course_id = s.id
            JOIN instructors i ON t.instructor_id = i.id
            JOIN groups g ON t.group_id = g.id
            JOIN rooms r ON t.room_id = r.id
            ORDER BY t.day, t.start_hour
        """)
        for r in cursor.fetchall():
              tree.insert("", "end", values=(DAYS.get(r[0], r[0]), r[1], r[2], r[3], r[4], r[5], r[6]))
        conn.close()
        
        ttk.Button(self.content_area, text="Retour", command=self.show_stats).pack(pady=20)

        ttk.Button(self.content_area, text="Retour", command=self.show_stats).pack(pady=20)

    def show_room_stats(self):
        self.clear_content()
        tk.Label(self.content_area, text="Occupation des Salles (Temps Réel & Stats)", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 20))
        
        # --- Section Temps Réel ---
        from datetime import datetime
        now_str = datetime.now().strftime("%d/%m %H:%M")
        
        tk.Label(self.content_area, text=f"🔴 État Actuel ({now_str})", font=("Segoe UI", 14, "bold"), fg=ACCENT_COLOR).pack(anchor="w", pady=(10, 5))
        
        realtime = self.controller.get_realtime_room_status()
        
        rt_frame = tk.Frame(self.content_area, bg=WHITE)
        rt_frame.pack(fill="x", pady=10)
        
        if not realtime["is_working_hour"]:
             tk.Label(rt_frame, text="Hors créneaux de cours (Campus fermé ou pause)", bg=WHITE, fg="grey").pack(anchor="w")
        else:
             # Grid view of rooms
             rooms = realtime["rooms"]
             # Create a grid with max 5 columns
             cols = 5
             for i, r in enumerate(rooms):
                 row = i // cols
                 col = i % cols
                 
                 bg_color = "#2ecc71" if r['status'] == 'Free' else "#e74c3c" # Green or Red
                 fg_color = "white"
                 
                 card = tk.Frame(rt_frame, bg=bg_color, padx=5, pady=5, width=120, height=60)
                 card.grid_propagate(False) # fixed size
                 card.grid(row=row, column=col, padx=5, pady=5)
                 
                 tk.Label(card, text=r['name'], bg=bg_color, fg=fg_color, font=("Segoe UI", 10, "bold")).pack()
                 tk.Label(card, text=r['info'], bg=bg_color, fg=fg_color, font=("Segoe UI", 8)).pack()

        # --- Section Stats Tableau ---
        tk.Label(self.content_area, text="📊 Taux d'Occupation Hebdomadaire", font=("Segoe UI", 14, "bold"), fg=ACCENT_COLOR).pack(anchor="w", pady=(20, 5))
        
        cols = ("Salle", "Capacité", "Créneaux occupés /30", "Taux %", "Statut")
        tree = ttk.Treeview(self.content_area, columns=cols, show="headings", height=10)
        for c in cols: tree.heading(c, text=c)
        tree.column("Salle", width=80)
        tree.column("Capacité", width=80)
        tree.column("Créneaux occupés /30", width=120)
        tree.column("Taux %", width=80)
        tree.column("Statut", width=100)
        tree.pack(fill="x")
        
        stats = self.controller.get_room_occupancy_stats()
        for s in stats:
            tree.insert("", "end", values=(s['room'], s['capacity'], s['occupied'], f"{s['rate']}%", s['status']))

    def show_add_slot(self):
        self.clear_content()
        tk.Label(self.content_area, text="Ajouter un créneau de cours", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 20))
        
        form_frame = tk.Frame(self.content_area, bg=WHITE, padx=30, pady=30)
        form_frame.pack(fill="both")
        
        # Load Data
        subjects = get_all("subjects", "id, name, code")
        teachers = get_all("instructors", "id, name") # user_id is different from instructor_id? No, instructors table has own id.
        groups = get_all("groups", "id, name")
        rooms = get_all("rooms", "id, name, capacity")
        
        # UI Helpers
        def create_combo(label, values_list):
            f = tk.Frame(form_frame, bg=WHITE)
            f.pack(fill="x", pady=10)
            tk.Label(f, text=label, bg=WHITE, width=15, anchor="w").pack(side="left")
            cb = ttk.Combobox(f, values=[f"{v[1]} (ID:{v[0]})" for v in values_list], state="readonly", width=40)
            cb.pack(side="left", fill="x", expand=True)
            return cb, values_list

        cb_sub, list_sub = create_combo("Matière:", subjects)
        cb_teach, list_teach = create_combo("Enseignant:", teachers)
        cb_group, list_group = create_combo("Groupe:", groups)
        cb_room, list_room = create_combo("Salle:", rooms)
        
        # Day & Time
        f_dt = tk.Frame(form_frame, bg=WHITE)
        f_dt.pack(fill="x", pady=10)
        tk.Label(f_dt, text="Jour:", bg=WHITE, width=15, anchor="w").pack(side="left")
        cb_day = ttk.Combobox(f_dt, values=[d[1] for d in get_days_combo()], state="readonly", width=15)
        cb_day.pack(side="left")
        
        tk.Label(f_dt, text="Heure (8-18):", bg=WHITE, width=12, anchor="e").pack(side="left", padx=10)
        sp_hour = ttk.Spinbox(f_dt, from_=8, to=18, width=5)
        sp_hour.set(8)
        sp_hour.pack(side="left")
        
        tk.Label(f_dt, text="Durée (h):", bg=WHITE, width=10, anchor="e").pack(side="left", padx=10)
        sp_dur = ttk.Spinbox(f_dt, from_=1, to=4, width=5)
        sp_dur.set(2)
        sp_dur.pack(side="left")

        def submit():
            try:
                s_idx = cb_sub.current()
                t_idx = cb_teach.current()
                g_idx = cb_group.current()
                r_idx = cb_room.current()
                d_idx = cb_day.current()
                
                if any(x == -1 for x in [s_idx, t_idx, g_idx, r_idx, d_idx]):
                    messagebox.showwarning("Attention", "Veuillez remplir tous les champs.")
                    return

                course_id = list_sub[s_idx][0]
                instr_id = list_teach[t_idx][0]
                grp_id = list_group[g_idx][0]
                rm_id = list_room[r_idx][0]
                day = get_days_combo()[d_idx][0]
                hour = int(sp_hour.get())
                dur = int(sp_dur.get())
                
                if self.controller.creer_creneau(course_id, instr_id, grp_id, rm_id, day, hour, dur):
                    messagebox.showinfo("Succès", "Créneau ajouté avec succès !")
                else:
                    messagebox.showerror("Erreur", "Impossible d'ajouter le créneau (Conflit). Vérifiez la console.")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

        ttk.Button(form_frame, text="Ajouter le cours", command=submit).pack(pady=20)

    def show_auto_assign(self):
        self.clear_content()
        tk.Label(self.content_area, text="Génération & Affectation Intelligente", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 20))
        
        # --- SECTION 1: GÉNÉRATION COMPLÈTE (IA) ---
        f_gen = tk.Frame(self.content_area, bg=WHITE, padx=20, pady=20, relief="solid", borderwidth=1)
        f_gen.pack(fill="x", pady=(0, 30))
        
        tk.Label(f_gen, text="🚀 Génération Automatique Complète", font=("Segoe UI", 14, "bold"), bg=WHITE, fg="#d35400").pack(anchor="w")
        tk.Label(f_gen, text="L'algorithme génétique va optimiser l'emploi du temps pour toute l'université.", bg=WHITE).pack(anchor="w")
        tk.Label(f_gen, text="Attention: Cela effacera l'emploi du temps actuel.", bg=WHITE, fg="red").pack(anchor="w", pady=5)
        
        def run_full_gen():
            confirm = messagebox.askyesno("Confirmation", "Cela va effacer tout l'emploi du temps actuel et en générer un nouveau. Continuer ?")
            if confirm:
                # Afficher un message de chargement (simple print pour l'instant car GUI bloquant)
                self.master.update()
                msg = self.controller.generer_planning_complet()
                messagebox.showinfo("Résultat Génération", msg)
        
        ttk.Button(f_gen, text="Lancer la Génération Globale", command=run_full_gen).pack(pady=10)


        # --- SECTION 2: AFFECTATION ASSISTÉE (UNITAIRE) ---
        tk.Label(self.content_area, text="Affectation Assistée (Unitaire)", font=("Segoe UI", 14, "bold"), bg=BG_COLOR).pack(anchor="w", pady=(0, 10))
        
        form_frame = tk.Frame(self.content_area, bg=WHITE, padx=30, pady=30)
        form_frame.pack(fill="both")
        
        subjects = get_all("subjects", "id, name")
        groups = get_all("groups", "id, name")
        
        def create_combo(p, label, values_list):
            f = tk.Frame(p, bg=WHITE)
            f.pack(fill="x", pady=10)
            tk.Label(f, text=label, bg=WHITE, width=15, anchor="w").pack(side="left")
            cb = ttk.Combobox(f, values=[f"{v[1]}" for v in values_list], state="readonly", width=40)
            cb.pack(side="left", fill="x", expand=True)
            return cb, values_list

        cb_sub, list_sub = create_combo(form_frame, "Matière:", subjects)
        cb_grp, list_grp = create_combo(form_frame, "Groupe:", groups)
        
        f_dt = tk.Frame(form_frame, bg=WHITE)
        f_dt.pack(fill="x", pady=10)
        tk.Label(f_dt, text="Jour:", bg=WHITE, width=15, anchor="w").pack(side="left")
        cb_day = ttk.Combobox(f_dt, values=[d[1] for d in get_days_combo()], state="readonly", width=15)
        cb_day.pack(side="left")
        
        tk.Label(f_dt, text="Heure Début:", bg=WHITE, width=12, anchor="e").pack(side="left")
        sp_hour = ttk.Spinbox(f_dt, from_=8, to=18, width=5)
        sp_hour.set(8)
        sp_hour.pack(side="left")
        
        tk.Label(f_dt, text="Durée:", bg=WHITE, width=10, anchor="e").pack(side="left")
        sp_dur = ttk.Spinbox(f_dt, from_=1, to=4, width=5)
        sp_dur.set(2)
        sp_dur.pack(side="left")
        
        def run_auto():
            if cb_sub.current() == -1 or cb_grp.current() == -1 or cb_day.current() == -1:
                messagebox.showwarning("Oups", "Champs manquants")
                return
            
            sub_id = list_sub[cb_sub.current()][0]
            grp_id = list_grp[cb_grp.current()][0]
            day = get_days_combo()[cb_day.current()][0]
            
            res = self.controller.affecter_automatiquement(sub_id, grp_id, day, int(sp_hour.get()), int(sp_dur.get()))
            messagebox.showinfo("Résultat", res)

        ttk.Button(form_frame, text="Trouver et Assigner une Salle", command=run_auto).pack(pady=20)

    def show_validations(self):
        self.clear_content()
        tk.Label(self.content_area, text="Réservations en attente", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 20))
        
        cols = ("ID", "Enseignant", "Jour", "Heure", "Raison")
        tree = ttk.Treeview(self.content_area, columns=cols, show="headings", height=10)
        for c in cols: tree.heading(c, text=c)
        tree.column("ID", width=50)
        tree.pack(fill="both", expand=True)
        
        # Load pending
        conn = getConnection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, u.full_name, r.day, r.start_hour, r.reason 
            FROM reservations r
            JOIN instructors i ON r.instructor_id = i.id
            JOIN users u ON i.user_id = u.id
            WHERE r.status = 'PENDING'
        """)
        rows = cursor.fetchall()
        conn.close()
        
        for r in rows:
            tree.insert("", "end", values=(r[0], r[1], DAYS.get(r[2], r[2]), f"{r[3]}h", r[4]))
            
        def action(is_approve):
            sel = tree.selection()
            if not sel: 
                messagebox.showwarning("Sélection requise", "Veuillez sélectionner une réservation dans la liste.")
                return
            
            try:
                item = tree.item(sel[0])
                rid = int(item['values'][0]) # Ensure int conversion
                
                if is_approve:
                    self.controller.valider_reservation(rid)
                    messagebox.showinfo("Succès", f"Réservation #{rid} validée avec succès.")
                else:
                    self.controller.rejeter_reservation(rid)
                    messagebox.showinfo("Succès", f"Réservation #{rid} rejetée.")
                
                # Refresh list
                self.show_validations()
            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur est survenue : {str(e)}")

        btn_box = tk.Frame(self.content_area, bg=BG_COLOR)
        btn_box.pack(pady=10)
        ttk.Button(btn_box, text=" Valider la sélection", command=lambda: action(True)).pack(side="left", padx=10)
        ttk.Button(btn_box, text=" Rejeter la sélection", command=lambda: action(False), style="Delete.TButton").pack(side="left", padx=10)

    def show_export(self):
        """Affiche la vue d'exportation des données avec le nouveau bouton"""
        self.clear_content()

        # Titre principal
        title = tk.Label(
            self.content_area,
            text="Exporter les données",
            font=("Arial", 18, "bold"),
            bg=BG_COLOR,
            fg=TEXT_COLOR
        )
        title.pack(pady=(20, 10), padx=20, anchor="w")

        # Conteneur principal
        export_frame = tk.Frame(
            self.content_area,
            bg=WHITE,
            highlightthickness=1,
            highlightbackground="#ccc",
            bd=0
        )
        export_frame.pack(pady=20, padx=20, fill="both", expand=True)

        tk.Label(
            export_frame,
            text="Télécharger les rapports :",
            bg=WHITE,
            font=("Arial", 11)
        ).pack(pady=(20, 10), padx=20, anchor="w")

        # --- BOUTON 1: PLANNING OFFICIEL ---
        btn_planning = tk.Button(
            export_frame,
            text="📄 Exporter l'Emploi du Temps par Filière (PDF)",
            bg=ACCENT_COLOR,
            fg=WHITE,
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            height=2,
            command=self.prompt_filiere_export
        )
        btn_planning.pack(pady=10, padx=40, fill="x")

        # --- BOUTON 2: EDT EXCEL ---
        btn_planning_excel = tk.Button(
            export_frame,
            text="📊 Exporter l'Emploi du Temps par Filière (Excel)",
            bg="#27ae60",
            fg=WHITE,
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            height=2,
            command=self.prompt_filiere_export_excel
        )
        btn_planning_excel.pack(pady=10, padx=40, fill="x")

        # --- BOUTON 3: EDT IMAGE ---
        btn_planning_image = tk.Button(
            export_frame,
            text="🖼️ Exporter l'Emploi du Temps par Filière (Image PNG)",
            bg="#9b59b6",
            fg=WHITE,
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            height=2,
            command=self.prompt_filiere_export_image
        )
        btn_planning_image.pack(pady=10, padx=40, fill="x")

    def prompt_filiere_export(self):
        """Affiche une boîte de dialogue pour exporter en PDF"""
        from tkinter import simpledialog
        filiere = simpledialog.askstring("Export PDF", "Entrez le nom de la filière (ex: LST AD, IDAI...) ou 'all' pour tout :")
        if filiere:
            try:
                if filiere.lower() in ['all', 'tout']:
                     filename = "Planning_Global_FST.pdf"
                else:
                     filename = f"Planning_{filiere.replace(' ', '_')}.pdf"
                
                result = self.controller.exporter_planning_filiere_pdf(filiere, filename)
                messagebox.showinfo("Succès", f"Le planning de la filière {filiere} a été généré !\n{result}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'exportation : {str(e)}")

    def prompt_filiere_export_excel(self):
        """Affiche une boîte de dialogue pour exporter en Excel"""
        from tkinter import simpledialog
        filiere = simpledialog.askstring("Export Excel", "Entrez le nom de la filière (ex: LST AD...) ou 'all' pour tout :")
        if filiere:
            try:
                if filiere.lower() in ['all', 'tout']:
                     filename = "Planning_Global_FST.xlsx"
                else:
                     filename = f"Planning_{filiere.replace(' ', '_')}.xlsx"

                result = self.controller.exporter_planning_filiere_excel(filiere, filename)
                messagebox.showinfo("Succès", f"Le planning Excel de la filière {filiere} a été généré !\n{result}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'exportation : {str(e)}")

    def prompt_filiere_export_image(self):
        """Affiche une boîte de dialogue pour exporter en Image"""
        from tkinter import simpledialog
        filiere = simpledialog.askstring("Export Image", "Entrez le nom de la filière (ex: LST AD, IDAI, SSD, MID) :")
        if filiere:
            try:
                filename = f"Planning_{filiere.replace(' ', '_')}.png"
                result = self.controller.exporter_planning_filiere_image(filiere, filename)
                messagebox.showinfo("Succès", f"L'image du planning de la filière {filiere} a été générée !\n{result}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'exportation : {str(e)}")

# --- TEACHER DASHBOARD ---
class TeacherDashboard(DashboardFrame):
    def __init__(self, master):
        super().__init__(master, "Espace Enseignant", role_color="#2980b9")
        self.controller = TeacherController(self.master.current_user['id'])
        self.setup_menu()
        self.show_timetable()

    def setup_menu(self):
        self.add_sidebar_button("Mon Emploi du Temps", self.show_timetable)
        self.add_sidebar_button("Réserver une salle", self.show_reservation)
        self.add_sidebar_button("Chercher une salle", self.search_free)
        self.add_sidebar_button("Signaler Absence", self.show_unavail)
        self.add_sidebar_button("Exporter", self.show_export)

    def show_timetable(self):
        self.clear_content()
        tk.Label(self.content_area, text="Mon Planning Hebdomadaire", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 20))
        
        res = self.controller.get_teacher_timetable()
        if not res["success"]:
            tk.Label(self.content_area, text=res.get("error", "Erreur"), fg=ERROR_COLOR).pack()
            return

        cols = ("Jour", "Heure", "Matière", "Groupe", "Salle", "Type")
        tree = ttk.Treeview(self.content_area, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c)
        tree.pack(fill="both", expand=True)
        
        for day, slots in res["timetable"].items():
            for s in slots:
                tree.insert("", "end", values=(day, s['heure'], s['matiere'], s['groupe'], s['salle'], s['type_salle']))

    def show_reservation(self):
        self.clear_content()
        tk.Label(self.content_area, text="Nouvelle Demande de Réservation", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 20))
        
        f = tk.Frame(self.content_area, bg=WHITE, padx=20, pady=20)
        f.pack(fill="x")
        
        rooms = get_all("rooms", "name")
        groups = get_all("groups", "name")
        
        tk.Label(f, text="Salle:", bg=WHITE).grid(row=0, column=0, sticky="w", pady=5)
        cb_room = ttk.Combobox(f, values=[r[0] for r in rooms], state="readonly")
        cb_room.grid(row=0, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(f, text="Groupe:", bg=WHITE).grid(row=1, column=0, sticky="w", pady=5)
        cb_grp = ttk.Combobox(f, values=[g[0] for g in groups], state="readonly")
        cb_grp.grid(row=1, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(f, text="Jour:", bg=WHITE).grid(row=2, column=0, sticky="w", pady=5)
        cb_day = ttk.Combobox(f, values=[d[1] for d in get_days_combo()], state="readonly")
        cb_day.grid(row=2, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(f, text="Heure:", bg=WHITE).grid(row=3, column=0, sticky="w", pady=5)
        sp_h = ttk.Spinbox(f, from_=8, to=18)
        sp_h.set(8)
        sp_h.grid(row=3, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(f, text="Durée:", bg=WHITE).grid(row=4, column=0, sticky="w", pady=5)
        sp_d = ttk.Spinbox(f, from_=1, to=4)
        sp_d.set(1)
        sp_d.grid(row=4, column=1, sticky="ew", pady=5, padx=10)
        
        tk.Label(f, text="Motif:", bg=WHITE).grid(row=5, column=0, sticky="w", pady=5)
        e_reas = ttk.Entry(f)
        e_reas.grid(row=5, column=1, sticky="ew", pady=5, padx=10)
        
        def send():
            if cb_room.current() == -1 or cb_grp.current() == -1 or cb_day.current() == -1:
                return
            
            d_val = get_days_combo()[cb_day.current()][0]
            res = self.controller.submit_reservation(
                cb_room.get(), cb_grp.get(), d_val, int(sp_h.get()), int(sp_d.get()), e_reas.get()
            )
            if res["success"]:
                messagebox.showinfo("Envoyé", res["message"])
            else:
                messagebox.showerror("Erreur", res["message"])

        ttk.Button(f, text="Envoyer Demande", command=send).grid(row=6, column=1, pady=20)
        
        # Show status below
        tk.Label(self.content_area, text="Historique", font=("Segoe UI", 14, "bold"), bg=BG_COLOR).pack(anchor="w", pady=(20, 10))
        cols = ("Jour", "H", "Salle", "Motif", "Statut")
        tree = ttk.Treeview(self.content_area, columns=cols, show="headings", height=5)
        for c in cols: tree.heading(c, text=c)
        tree.pack(fill="x")
        
        st = self.controller.get_reservation_status()
        if st["success"]:
            for r in st["reservations"]:
                tree.insert("", "end", values=(r['jour'], r['horaire'], r['salle'], r['motif'], r['statut']))

    def search_free(self):
        self.clear_content()
        tk.Label(self.content_area, text="Rechercher Salle", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 20))
        
        f = tk.Frame(self.content_area, bg=WHITE, padx=20, pady=20)
        f.pack(fill="x")
        
        cb_day = ttk.Combobox(f, values=[d[1] for d in get_days_combo()], state="readonly")
        cb_day.pack(side="left", padx=5)
        cb_day.set("Lundi")
        
        sp_h = ttk.Spinbox(f, from_=8, to=18, width=5); sp_h.set(8); sp_h.pack(side="left", padx=5)
        sp_d = ttk.Spinbox(f, from_=1, to=4, width=5); sp_d.set(2); sp_d.pack(side="left", padx=5)
        
        res_frame = tk.Frame(self.content_area, bg=BG_COLOR)
        res_frame.pack(fill="both", expand=True, pady=10)
        
        def search():
            for w in res_frame.winfo_children(): w.destroy()
            if cb_day.current() == -1: return
            
            day = get_days_combo()[cb_day.current()][0]
            res = self.controller.search_available_room(day, int(sp_h.get()), int(sp_d.get()))
            
            if res["success"]:
                tk.Label(res_frame, text=f"{res['count']} salles trouvées:", font=("Segoe UI", 12, "bold")).pack(anchor="w")
                listbox = tk.Listbox(res_frame, font=("Segoe UI", 11), height=15)
                listbox.pack(fill="both", expand=True)
                for r in res["rooms"]:
                    listbox.insert("end", f"{r['nom']} ({r['type']}) - Cap: {r['capacité']}")
            else:
                tk.Label(res_frame, text="Erreur recherche").pack()

        ttk.Button(f, text="Chercher", command=search).pack(side="left", padx=20)

    def show_unavail(self):
        self.clear_content()
        tk.Label(self.content_area, text="Déclarer une Indisponibilité", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        
        f = tk.Frame(self.content_area, bg=WHITE, padx=20, pady=20)
        f.pack(fill="x", pady=20)
        
        cb_day = ttk.Combobox(f, values=[d[1] for d in get_days_combo()], state="readonly")
        cb_day.pack(side="left", padx=5)
        sp_h = ttk.Spinbox(f, from_=8, to=18, width=5); sp_h.set(8); sp_h.pack(side="left", padx=5)
        sp_d = ttk.Spinbox(f, from_=1, to=8, width=5); sp_d.set(2); sp_d.pack(side="left", padx=5)
        
        def save():
            if cb_day.current() == -1: return
            res = self.controller.declare_unavailability(get_days_combo()[cb_day.current()][0], int(sp_h.get()), int(sp_d.get()))
            messagebox.showinfo("Info", res["message"])
            
        ttk.Button(f, text="Enregistrer", command=save).pack(side="left", padx=20)

    def show_export(self):
        """Vue pour exporter son emploi du temps"""
        self.clear_content()
        tk.Label(self.content_area, text="Exporter mon Emploi du Temps", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 20))
        
        f = tk.Frame(self.content_area, bg="white", padx=20, pady=20)
        f.pack(fill="x", pady=10)
        
        ttk.Button(f, text="📄 Exporter en PDF", command=self.export_pdf).pack(fill="x", pady=5)
        ttk.Button(f, text="📊 Exporter en Excel", command=self.export_excel).pack(fill="x", pady=5)
        ttk.Button(f, text="🖼️ Exporter en Image", command=self.export_image).pack(fill="x", pady=5)

    def export_pdf(self):
        res = self.controller.export_my_timetable_pdf()
        messagebox.showinfo("Export PDF", res)

    def export_excel(self):
        res = self.controller.export_my_timetable_excel()
        messagebox.showinfo("Export Excel", res)

    def export_image(self):
        res = self.controller.export_my_timetable_image()
        messagebox.showinfo("Export Image", res)

# --- STUDENT DASHBOARD ---
class StudentDashboard(DashboardFrame):
    def __init__(self, master):
        super().__init__(master, "Espace Étudiant", role_color="#27ae60")
        self.controller = StudentController(self.master.current_user['id'])
        self.setup_menu()
        self.show_timetable()

    def setup_menu(self):
        self.add_sidebar_button("Mon Planning", self.show_timetable)
        self.add_sidebar_button("Cours Aujourd'hui", self.show_today)
        self.add_sidebar_button("Salles Libres", self.show_free_rooms)
        self.add_sidebar_button("Exporter", self.show_export)

    def show_timetable(self):
        self.clear_content()
        tk.Label(self.content_area, text="Emploi du Temps de ma Filière", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 20))
        
        res = self.controller.get_group_timetable()
        if not res["success"]:
            tk.Label(self.content_area, text="Erreur ou pas de groupe").pack(); return
        
        tk.Label(self.content_area, text=f"GROUPE: {res['groupe']}", font=("Segoe UI", 14), fg=ACCENT_COLOR).pack(anchor="w")

        cols = ("Jour", "Heure", "Matière", "Enseignant", "Salle")
        tree = ttk.Treeview(self.content_area, columns=cols, show="headings", height=20)
        for c in cols: tree.heading(c, text=c)
        tree.pack(fill="both", expand=True, pady=10)
        
        for day, slots in res["emploi_du_temps"].items():
            for s in slots:
                tree.insert("", "end", values=(day, s['horaire'], s['matiere'], s['enseignant'], s['salle']))

    def show_today(self):
        self.clear_content()
        tk.Label(self.content_area, text="Mes Cours d'Aujourd'hui", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        
        res = self.controller.get_today_schedule()
        if not res["success"]: return
        
        f = tk.Frame(self.content_area, bg=BG_COLOR)
        f.pack(fill="both", expand=True, pady=20)
        
        if not res['cours']:
            tk.Label(f, text="Pas de cours aujourd'hui! 🎉", font=("Segoe UI", 16)).pack(pady=50)
        else:
            for c in res['cours']:
                card = tk.Frame(f, bg=WHITE, padx=20, pady=15, relief="raised")
                card.pack(fill="x", pady=10)
                tk.Label(card, text=f"{c['horaire']}", font=("Segoe UI", 14, "bold"), bg=WHITE, fg=ACCENT_COLOR).pack(side="left")
                tk.Label(card, text=f"{c['matiere']}", font=("Segoe UI", 14), bg=WHITE).pack(side="left", padx=20)
                tk.Label(card, text=f"avec {c['enseignant']} en {c['salle']}", font=("Segoe UI", 12, "italic"), bg=WHITE).pack(side="right")

    def show_free_rooms(self):
        self.clear_content()
        tk.Label(self.content_area, text="Rechercher une salle libre", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 20))

        # --- Search Form ---
        form_frame = tk.Frame(self.content_area, bg=WHITE, padx=20, pady=20, relief="solid", borderwidth=1)
        form_frame.pack(fill="x", pady=(0, 20))

        # Defaults determination
        now = datetime.now()
        current_day_idx = now.weekday() + 1 # 1=Mon, 7=Sun
        current_hour = now.hour
        
        default_day_idx = 0 # Default to Monday
        default_hour = 8
        
        # If we are in a valid school slot (Mon-Fri, 8-18), pre-select current time
        if 1 <= current_day_idx <= 5:
             # Find index in combo (0-based) for the day
             # DAYS = {1: "Lundi", ...} matched by get_days_combo list
             # get_days_combo returns [(1, 'Lundi'), (2, 'Mardi')...]
             # So index is current_day_idx - 1
             default_day_idx = current_day_idx - 1
             
             if 8 <= current_hour < 18:
                 default_hour = current_hour

        # UI Elements
        f_controls = tk.Frame(form_frame, bg=WHITE)
        f_controls.pack(fill="x")

        tk.Label(f_controls, text="Jour:", bg=WHITE).pack(side="left")
        cb_day = ttk.Combobox(f_controls, values=[d[1] for d in get_days_combo()], state="readonly", width=15)
        cb_day.pack(side="left", padx=(5, 20))
        if 0 <= default_day_idx < len(get_days_combo()):
            cb_day.current(default_day_idx)
        else:
            cb_day.current(0)

        tk.Label(f_controls, text="Heure début:", bg=WHITE).pack(side="left")
        sp_hour = ttk.Spinbox(f_controls, from_=8, to=18, width=5)
        sp_hour.set(default_hour)
        sp_hour.pack(side="left", padx=(5, 20))

        tk.Label(f_controls, text="Durée (h):", bg=WHITE).pack(side="left")
        sp_dur = ttk.Spinbox(f_controls, from_=1, to=4, width=5)
        sp_dur.set(1) # Default 1 hour
        sp_dur.pack(side="left", padx=(5, 20))

        # Results area
        res_label = tk.Label(self.content_area, text="", font=("Segoe UI", 12, "italic"), bg=BG_COLOR, fg=SIDEBAR_COLOR)
        res_label.pack(anchor="w", pady=(10, 5))
        
        res_list = tk.Listbox(self.content_area, font=("Segoe UI", 11), bg=WHITE, relief="flat", borderwidth=0, highlightthickness=1)
        res_list.pack(fill="both", expand=True)

        def perform_search():
            res_list.delete(0, "end")
            res_label.config(text="Recherche en cours...")
            self.master.update()

            if cb_day.current() == -1:
                return

            selected_day_val = get_days_combo()[cb_day.current()][0]
            try:
                h = int(sp_hour.get())
                d = int(sp_dur.get())
            except ValueError:
                messagebox.showerror("Erreur", "Heure ou durée invalide")
                return

            # Call Controller
            res = self.controller.search_free_room(day=selected_day_val, start_hour=h, duration=d)

            day_name = cb_day.get()
            
            if res["success"]:
                count = len(res["rooms"])
                res_label.config(text=f"{count} salle(s) libre(s) le {day_name} de {h}h à {h+d}h :")
                if count == 0:
                    res_list.insert("end", "Aucune salle disponible pour ce créneau.")
                else:
                    for r in res["rooms"]:
                        room_text = f"✅ {r['nom']} ({r['type']}) - Cap: {r['capacité']}"
                        res_list.insert("end", room_text)
            else:
                 res_label.config(text="Erreur lors de la recherche.")
                 messagebox.showerror("Erreur", res.get("error", "Erreur inconnue"))

        ttk.Button(f_controls, text="🔍 Rechercher", command=perform_search).pack(side="left", padx=20)


    def show_export(self):
        """Vue pour exporter son emploi du temps"""
        self.clear_content()
        tk.Label(self.content_area, text="Exporter mon Emploi du Temps", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 20))
        
        f = tk.Frame(self.content_area, bg="white", padx=20, pady=20)
        f.pack(fill="x", pady=10)
        
        ttk.Button(f, text="📄 Exporter en PDF", command=self.export_pdf).pack(fill="x", pady=5)
        ttk.Button(f, text="📊 Exporter en Excel", command=self.export_excel).pack(fill="x", pady=5)
        ttk.Button(f, text="🖼️ Exporter en Image", command=self.export_image).pack(fill="x", pady=5)

    def export_pdf(self):
        res = self.controller.export_my_timetable_pdf()
        messagebox.showinfo("Export PDF", res)

    def export_excel(self):
        res = self.controller.export_my_timetable_excel()
        messagebox.showinfo("Export Excel", res)

    def export_image(self):
        res = self.controller.export_my_timetable_image()
        messagebox.showinfo("Export Image", res)


if __name__ == "__main__":
    app = App()
    app.mainloop()
