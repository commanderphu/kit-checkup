import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from tkinter import ttk
import threading
import psutil
import platform
import os
import math
import sys
import sqlite3
import json
import datetime

# --- System Check Logik (unverändert) ---
# get_system_info, get_component_descriptions, calculate_performance_score bleiben gleich

def get_system_info():
    """Sammelt grundlegende Systeminformationen."""
    info = {}
    try: uname = platform.uname(); info['System'] = uname.system; info['Node Name'] = uname.node; info['Release'] = uname.release; info['Version'] = uname.version; info['Machine'] = uname.machine; info['Processor'] = uname.processor
    except Exception as e: info['OS Info Error'] = str(e)
    try:
        info['CPU Cores (Physical)'] = psutil.cpu_count(logical=False); info['CPU Cores (Total)'] = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        if cpu_freq: info['CPU Frequency (Current_Mhz)'] = cpu_freq.current; info['CPU Frequency (Max_Mhz)'] = cpu_freq.max; info['CPU Frequency (Current)'] = f"{cpu_freq.current:.2f} Mhz"; info['CPU Frequency (Max)'] = f"{cpu_freq.max:.2f} Mhz"
        if not info.get('Processor') or "unknown" in info.get('Processor', '').lower(): info['Processor'] = "Could not determine exact CPU name (Generic: " + info.get('Processor', 'Unknown') + ")"
    except Exception as e: info['CPU Info Error'] = str(e)
    try: svmem = psutil.virtual_memory(); info['Total RAM_Bytes'] = svmem.total; info['Available RAM_Bytes'] = svmem.available; info['Used RAM_Bytes'] = svmem.used; info['Total RAM'] = f"{svmem.total / (1024**3):.2f} GB"; info['Available RAM'] = f"{svmem.available / (1024**3):.2f} GB"; info['Used RAM'] = f"{svmem.used / (1024**3):.2f} GB"; info['RAM Usage (%)'] = f"{svmem.percent:.2f}%"
    except Exception as e: info['RAM Info Error'] = str(e)
    try:
        partitions = psutil.disk_partitions(); disk_info_list = []
        for p in partitions:
            if 'cdrom' in p.opts or p.fstype == '': continue
            try: usage = psutil.disk_usage(p.mountpoint); disk_info_list.append({'Device': p.device, 'Mountpoint': p.mountpoint, 'File System Type': p.fstype, 'Total Size_Bytes': usage.total, 'Used_Bytes': usage.used, 'Free_Bytes': usage.free, 'Total Size': f"{usage.total / (1024**3):.2f} GB", 'Used': f"{usage.used / (1024**3):.2f} GB", 'Free': f"{usage.free / (1024**3):.2f} GB", 'Usage (%)': f"{usage.percent:.2f}%"})
            except PermissionError: disk_info_list.append({'Device': p.device, 'Mountpoint': p.mountpoint, 'Error': 'Permission Denied'})
            except Exception as e: disk_info_list.append({'Device': p.device, 'Mountpoint': p.mountpoint, 'Error': str(e)})
        info['Disks'] = disk_info_list
    except Exception as e: info['Disk Info Error'] = str(e)
    info['GPU'] = "Could not determine exact GPU name (requires additional libraries/tools)"
    return info

def get_component_descriptions():
     return {'System': "Das Betriebssystem...", 'CPU': "Die CPU...", 'RAM': "RAM (Random Access Memory)...", 'Disks': "Festplatten...", 'GPU': "Die GPU..."}

def calculate_performance_score(system_info):
    """Berechnet einen einfachen Performance-Score (1-10) basierend auf den Infos."""
    score_points = 0
    max_possible_points = 0

    # Scoring Logik (Beispiel - Passe dies an deine Bedürfnisse an!)

    # CPU Punkte (basiert auf Kernanzahl)
    cpu_cores = system_info.get('CPU Cores (Total)', 0)
    max_cpu_points = 4 # Maximale Punkte für CPU
    # Korrigierte if/elif Struktur:
    if cpu_cores >= 12:
        score_points += 4
    elif cpu_cores >= 8:
        score_points += 3
    elif cpu_cores >= 6:
        score_points += 2.5
    elif cpu_cores >= 4:
        score_points += 1.5
    elif cpu_cores >= 2:
        score_points += 0.5
    max_possible_points += max_cpu_points

    # RAM Punkte (basiert auf Größe)
    ram_gb = system_info.get('Total RAM_Bytes', 0) / (1024**3) # Nutze die numerischen Bytes

    max_ram_points = 3 # Maximale Punkte für RAM
    # Korrigierte if/elif Struktur:
    if ram_gb >= 32:
        score_points += 3
    elif ram_gb >= 16:
        score_points += 2
    elif ram_gb >= 8:
        score_points += 1
    elif ram_gb >= 4:
        score_points += 0.5
    max_possible_points += max_ram_points

    # Festplatten Punkte (basiert auf Größe)
    max_disk_points = 3 # Maximale Punkte für Festplatte
    disks_info = system_info.get('Disks', [])
    if disks_info:
        main_disk_size_gb = disks_info[0].get('Total Size_Bytes', 0) / (1024**3) # Nutze die numerischen Bytes
        # Korrigierte if/elif Struktur:
        if main_disk_size_gb >= 1000:
            score_points += 2.5
        elif main_disk_size_gb >= 500:
            score_points += 1.5
        elif main_disk_size_gb >= 250:
            score_points += 0.5
        score_points += 0.5 # Grundpunkt für vorhandene Platte

    max_possible_points += max_disk_points # Füge max Punkte hinzu, auch wenn keine Platte erkannt wurde

    # GPU Punkte (Sehr schwierig ohne genauen Namen und Benchmark-Datenbank)
    max_gpu_points = 2 # Maximale Punkte für GPU
    score_points += 0.5 # Pauschal für integrierte/vorhandene Grafik
    max_possible_points += max_gpu_points


    # Gesamt-Score berechnen (Normalisieren auf 1-10)
    # Korrigierte if/else Struktur:
    if max_possible_points > 0:
        raw_score = (score_points / max_possible_points) * 9 + 1
        final_score = math.ceil(raw_score) # Runde auf die nächste ganze Zahl

        # Stelle sicher, dass der Score im Bereich 1-10 bleibt
        final_score = max(1, min(10, final_score))
    else:
        final_score = 1 # Kann keinen Score berechnen, gib 1 zurück

    return final_score

# --- Datenbank Export Funktion (angepasst) ---

def export_to_database(system_info, performance_score, customer_identifier):
    """Speichert die Systeminformationen und Kunden-ID in einer SQLite Datenbank."""
    db_file = "checkups.db"
    conn = None
    status_message = ""

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Tabelle erstellen, falls sie nicht existiert
        # HIER WIRD DIE NEUE SPALTE 'customer_identifier' HINZUGEFÜGT
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                hostname TEXT,
                customer_identifier TEXT, -- Neue Spalte für den Kunden
                os_system TEXT,
                os_release TEXT,
                os_version TEXT,
                os_machine TEXT,
                cpu_processor TEXT,
                cpu_cores_total INTEGER,
                cpu_frequency_max_mhz REAL,
                ram_total_bytes INTEGER,
                gpu_info TEXT,
                disks_info_json TEXT,
                performance_score INTEGER,
                raw_system_info_json TEXT
            )
        ''')

        # Daten für den Insert vorbereiten
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d -- %H:%M:%S")
        hostname = system_info.get('Node Name', 'N/A')
        # Kundenbezeichner aus dem Parameter verwenden
        customer_identifier_val = customer_identifier if customer_identifier else 'Kein Kunde angegeben' # Falls das Feld leer ist
        os_system = system_info.get('System', 'N/A')
        os_release = system_info.get('Release', 'N/A')
        os_version = system_info.get('Version', 'N/A')
        os_machine = system_info.get('Machine', 'N/A')
        cpu_processor = system_info.get('Processor', 'N/A')
        cpu_cores_total = system_info.get('CPU Cores (Total)', None)
        cpu_frequency_max_mhz = system_info.get('CPU Frequency (Max_Mhz)', None)
        ram_total_bytes = system_info.get('Total RAM_Bytes', None)
        gpu_info = system_info.get('GPU', 'N/A')
        disks_info_json = json.dumps(system_info.get('Disks', []))
        raw_system_info_json = json.dumps(system_info)

        # Daten in die Tabelle einfügen
        # HIER WIRD customer_identifier ZUM INSERT HINZUGEFÜGT
        cursor.execute('''
            INSERT INTO checkups (
                timestamp, hostname, customer_identifier, os_system, os_release, os_version, os_machine,
                cpu_processor, cpu_cores_total, cpu_frequency_max_mhz, ram_total_bytes,
                gpu_info, disks_info_json, performance_score, raw_system_info_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp, hostname, customer_identifier_val, os_system, os_release, os_version, os_machine,
            cpu_processor, cpu_cores_total, cpu_frequency_max_mhz, ram_total_bytes,
            gpu_info, disks_info_json, performance_score, raw_system_info_json
        ))

        conn.commit()
        status_message = f"Daten erfolgreich in '{db_file}' exportiert (Kunde: {customer_identifier_val})."

    except sqlite3.Error as e:
        status_message = f"Fehler beim Exportieren in die Datenbank: {e}"
        if conn: conn.rollback()
    except Exception as e:
         status_message = f"Ein unerwarteter Fehler ist beim Datenbankexport aufgetreten: {e}"
    finally:
        if conn: conn.close()

    return status_message

# --- GUI Implementierung (angepasst) ---

class SystemCheckGUI:
    def __init__(self, master):
        self.master = master
        master.title("PC/Notebook Check-Up Tool")

        self.main_frame = tk.Frame(master, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.title_label = tk.Label(self.main_frame, text="=== PC/Notebook Check-Up ===", font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=5)

        # --- NEUES FELD FÜR KUNDENBEZEICHNER ---
        self.customer_frame = tk.Frame(self.main_frame)
        self.customer_frame.pack(pady=5)

        self.customer_label = tk.Label(self.customer_frame, text="Ihr Name:")
        self.customer_label.pack(side=tk.LEFT, padx=5)

        self.customer_entry = tk.Entry(self.customer_frame, width=30)
        self.customer_entry.pack(side=tk.LEFT, padx=5)
        # --- ENDE NEUES FELD ---

        self.output_text = scrolledtext.ScrolledText(self.main_frame, wrap=tk.WORD, width=80, height=20, font=("Consolas", 10)) # Höhe angepasst
        self.output_text.pack(pady=10, fill=tk.BOTH, expand=True)
        self.output_text.tag_configure('bold', font=("Consolas", 10, "bold"))
        self.output_text.tag_configure('error', foreground="red")
        self.output_text.tag_configure('success', foreground="green")
        self.output_text.insert(tk.END, "Bitte Ihr Namen eingeben und 'Check-Up starten' klicken.\n")
        self.output_text.configure(state='disabled')

        self.progress_bar = ttk.Progressbar(self.main_frame, orient="horizontal", length=200, mode="indeterminate")

        self.start_button = tk.Button(self.main_frame, text="Check-Up starten", command=self.start_check)
        self.start_button.pack(pady=5)

        self.quit_button = tk.Button(self.main_frame, text="Beenden", command=master.quit)
        self.quit_button.pack(pady=5)

    def start_check(self):
        """Startet den System-Check und Export in einem separaten Thread."""
        # Hole den Kundenbezeichner aus dem Eingabefeld
        customer_identifier = self.customer_entry.get().strip() # .strip() entfernt Leerzeichen am Anfang/Ende

        self.output_text.configure(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Starte System Check für Kunde: {customer_identifier if customer_identifier else 'Keiner angegeben'}...\n")
        self.output_text.configure(state='disabled')

        self.start_button.config(state='disabled')
        # Optional: Kunden-Feld auch deaktivieren während des Checks
        self.customer_entry.config(state='disabled')

        self.progress_bar.pack(pady=5)
        self.progress_bar.start()

        # Starte die Logik inkl. Export im Thread
        # Übergebe den Kundenbezeichner an die Logik
        self.check_thread = threading.Thread(target=self.run_check_logic, args=(customer_identifier,))
        self.check_thread.start()

    def run_check_logic(self, customer_identifier):
        """Führt die System Check und Export Logik aus."""
        system_info = get_system_info()
        component_descriptions = get_component_descriptions()
        performance_score = calculate_performance_score(system_info)

        # Exportiere die Daten inkl. Kundenbezeichner in die Datenbank
        export_status_message = export_to_database(system_info, performance_score, customer_identifier)

        # Aktualisiere die GUI im Hauptthread nach Abschluss
        self.master.after(0, self.display_results, system_info, component_descriptions, performance_score, export_status_message)

    def display_results(self, system_info, component_descriptions, performance_score, export_status_message):
        """Zeigt die gesammelten Ergebnisse und den Exportstatus an."""
        self.output_text.configure(state='normal')

        self.output_text.insert(tk.END, "\n--- Ergebnisse ---\n", 'bold')

        # Informationen ausgeben
        display_order = ['System', 'Node Name', 'Machine', 'Processor', 'CPU Cores (Total)', 'CPU Frequency (Max)',
                         'Total RAM', 'Disks', 'GPU', 'Release', 'Version'] # Kunden-ID wird nicht hier ausgegeben, nur im Export-Status

        for key in display_order:
            if key in system_info:
                value = system_info[key]
                description = component_descriptions.get(key.split(' ')[0], "Keine Beschreibung verfügbar.")

                self.output_text.insert(tk.END, f"\nKomponente: {key}\n", 'bold')
                if key == 'Disks':
                    self.output_text.insert(tk.END, f"  Beschreibung: {component_descriptions.get('Disks', 'Keine Beschreibung verfügbar.')}\n")
                    if isinstance(value, list):
                        if value:
                            for i, disk in enumerate(value):
                                self.output_text.insert(tk.END, f"    Laufwerk {i+1}:\n")
                                disk_display_keys = ['Device', 'Mountpoint', 'File System Type', 'Total Size', 'Used', 'Free', 'Usage (%)', 'Error']
                                for d_key in disk_display_keys:
                                     if d_key in disk:
                                        self.output_text.insert(tk.END, f"      {d_key}: {disk[d_key]}\n")
                        else:
                             self.output_text.insert(tk.END, "    Keine Festplatteninformationen gefunden.\n")
                    else:
                         self.output_text.insert(tk.END, f"  Details: {value}\n")
            elif key == 'GPU':
                 self.output_text.insert(tk.END, f"\nKomponente: {key}\n", 'bold')
                 self.output_text.insert(tk.END, f"  Beschreibung: {component_descriptions.get(key, 'Keine Beschreibung verfügbar.')}\n")
                 self.output_text.insert(tk.END, f"  Details: {system_info.get('GPU', 'Informationen konnten nicht abgerufen werden.')}\n")
            elif key in component_descriptions:
                 if key not in system_info or not system_info[key]:
                     self.output_text.insert(tk.END, f"\nKomponente: {key}\n", 'bold')
                     self.output_text.insert(tk.END, f"  Beschreibung: {component_descriptions.get(key, 'Keine Beschreibung verfügbar.')}\n")
                     self.output_text.insert(tk.END, "  Details: Informationen nicht spezifisch aufgeführt.\n")


        # Performance Score anzeigen
        self.output_text.insert(tk.END, "\n" + "=" * 30 + "\n", 'bold')
        self.output_text.insert(tk.END, "=== Performance Bewertung ===\n", 'bold')
        self.output_text.insert(tk.END, f"Basierend auf den erkannten Komponenten ergibt sich ein Score von: {performance_score}/10\n", 'bold')
        self.output_text.insert(tk.END, "\nHinweis: Dieser Score ist eine Schätzung basierend auf grundlegenden Spezifikationen und kein genauer Benchmark.\n")
        self.output_text.insert(tk.END, "=" * 30 + "\n", 'bold')

        # Export Status anzeigen
        export_tag = 'success' if "erfolgreich" in export_status_message else 'error'
        self.output_text.insert(tk.END, f"\nDatenbank Export Status: {export_status_message}\n", export_tag)


        self.output_text.configure(state='disabled')
        self.start_button.config(state='normal')
        # Kunden-Feld wieder aktivieren
        self.customer_entry.config(state='normal')
        self.progress_bar.stop()
        self.progress_bar.pack_forget()


if __name__ == "__main__":
    root = tk.Tk()
    gui = SystemCheckGUI(root)
    root.mainloop()