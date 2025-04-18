import os

from flask import Flask, render_template, g
import sqlite3
import json
import datetime # Auch hier importieren, falls raw_system_info geparst wird

app = Flask(__name__)

DATABASE = 'checkups.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row # Gibt Zeilen als Objekte zurück, auf die per Spaltenname zugegriffen werden kann
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def inventory_list():
    db = get_db()
    records = []
    error_message = None

    try:
        cursor = db.cursor()
        # Wähle alle Spalten aus (inklusive der neuen 'customer_identifier')
        cursor.execute("SELECT * FROM checkups ORDER BY timestamp DESC")
        records = cursor.fetchall()

        processed_records = []
        for record in records:
            processed_record = dict(record) # Konvertiere sqlite3.Row zu einem Dictionary

            # Parse die Disks-Information
            try:
                processed_record['disks_info'] = json.loads(record['disks_info_json'])
            except (json.JSONDecodeError, TypeError):
                processed_record['disks_info'] = []

            # Parse die rohen Systeminfos (falls nötig für Anzeige bestimmter Details wie 'Total RAM')
            try:
                 processed_record['raw_system_info'] = json.loads(record['raw_system_info_json'])
            except (json.JSONDecodeError, TypeError):
                 processed_record['raw_system_info'] = {}

            # Entferne die ursprünglichen JSON-Strings
            del processed_record['disks_info_json']
            del processed_record['raw_system_info_json']

            processed_records.append(processed_record)

    except sqlite3.OperationalError as e:
        # Spezifischer Fehler, wenn die Tabelle oder Spalte fehlt (z.B. 'no such column: customer_identifier')
        error_message = f"Fehler beim Lesen der Datenbank: {e}. Stelle sicher, dass die Datenbank '{DATABASE}' die erwartete Struktur (inkl. customer_identifier) hat und zugreifbar ist."
        print(f"Database Operational Error: {e}")
    except sqlite3.Error as e:
        error_message = f"Ein Datenbankfehler ist aufgetreten: {e}"
        print(f"Database Error: {e}")
    except Exception as e:
         error_message = f"Ein unerwarteter Fehler ist aufgetreten: {e}"
         print(f"General Error: {e}")


    # Füge den Datenbankpfad zur Anzeige in der Vorlage hinzu (optional)
    # app.root_path gibt den Pfad zum Verzeichnis der App-Datei zurück
    database_full_path = os.path.join(app.root_path, DATABASE)


    return render_template('inventory.html', records=processed_records, error=error_message, database_path=database_full_path)

# Hauptausführung
if __name__ == '__main__':
    app.run(debug=True)