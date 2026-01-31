
import sqlite3

DB_NAME = 'university_schedule.db'

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def verify_export_logic():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Verify we have data.
    cursor.execute("SELECT count(*) as cnt FROM timetable")
    print(f"Total slots in DB: {cursor.fetchone()['cnt']}")
    
    # 2. Simulate Export Logic for "LST AD"
    filiere_name = "LST AD"
    
    # Updated time slots used in controller
    time_slots = ["08h00-09h30", "09h00-10h30", "10h45-12h15", "12h30-14h00", "14h15-15h45", "16h00-17h30"]
    days_list = ["LUNDI", "MARDI", "MERCREDI", "JEUDI", "VENDREDI", "SAMEDI"]
    SLOT_TO_HOUR = {"08h00-09h30": 8, "09h00-10h30": 9, "10h45-12h15": 10, "12h30-14h00": 12, "14h15-15h45": 14, "16h00-17h30": 16}
    DAYS_MAPPING = {"LUNDI": 1, "MARDI": 2, "MERCREDI": 3, "JEUDI": 4, "VENDREDI": 5, "SAMEDI": 6}

    found_slots = 0
    
    print(f"\nScanning for matches for filiere '{filiere_name}'...")
    
    for day_idx in range(1, 7): # 1 to 6
        for slot_label in time_slots:
            start_h = SLOT_TO_HOUR[slot_label]
            
            # The query from AdminController
            cursor.execute("""
                SELECT s.name as subject, r.name as room, g.name as group_name, t.start_hour
                FROM timetable t
                JOIN subjects s ON t.course_id = s.id
                JOIN rooms r ON t.room_id = r.id
                JOIN groups g ON t.group_id = g.id
                WHERE t.day = ? AND t.start_hour = ? AND UPPER(g.filiere) LIKE UPPER('%' || ? || '%')
                ORDER BY g.name
            """, (day_idx, start_h, filiere_name))
            
            rows = cursor.fetchall()
            if rows:
                print(f"  [Day {day_idx} | {slot_label} (start={start_h})] Found {len(rows)} classes:")
                for r in rows:
                    print(f"    - {r['subject']} ({r['group_name']}) in {r['room']}")
                    found_slots += 1
            else:
                 # Debug: Check if there's anything for this day/time without filiere filter to see if time slot mismatch logic persists
                 pass

    print(f"\nTotal matches found for export: {found_slots}")
    if found_slots > 0:
        print("VERIFICATION PASSED: Export logic matches DB data.")
    else:
        print("VERIFICATION FAILED: No data found for export.")

if __name__ == "__main__":
    verify_export_logic()
