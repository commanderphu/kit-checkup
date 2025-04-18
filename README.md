# PC/Notebook Inventory & Check-Up Tool

Dieses Projekt bietet ein einfaches Tool zur Durchführung von Hardware-Checks auf PCs/Notebooks, sammelt Systeminformationen, bewertet die Performance grob und exportiert die Daten in eine SQLite-Datenbank. Eine begleitende Webanwendung ermöglicht die Anzeige dieser Inventardaten in einer übersichtlichen Liste.

Das Tool ist konzipiert für den internen Gebrauch in Unternehmen, um schnell einen Überblick über die eingesetzte Hardware zu erhalten und eine einfache Inventarliste zu führen.

## Features

**Desktop Check-Up Tool (`system_check_gui.py`):**

* Grafische Benutzeroberfläche (GUI) mit Tkinter.
* Erkennung grundlegender Systemkomponenten (CPU, RAM, Speicher, OS, grundlegende GPU-Info).
* Anzeige einfacher Beschreibungen zu den erkannten Komponenten.
* Berechnung eines geschätzten Performance-Scores auf einer Skala von 1 bis 10.
* Möglichkeit zur Eingabe eines Kundenbezeichners pro Check-Up.
* Export der gesammelten Daten (inkl. Zeitstempel und Kundenbezeichner) in eine `checkups.db` SQLite-Datenbankdatei.

**Web Inventory Viewer (`app.py` & `templates/inventory.html`):**

* Einfache Webanwendung basierend auf Flask.
* Liest die Daten aus der `checkups.db` Datei.
* Zeigt alle Check-Up-Einträge in einer tabellarischen Liste an (Zeitstempel, Kunde, Hostname, Hardware-Details, Score).

## Projektstruktur
|── system_check_gui.py     # Das Desktop GUI Check-Up Tool
├── app.py                  # Die Flask Webanwendung
├── templates/              # Ordner für HTML-Vorlagen der Webapp
│   └── inventory.html      # HTML-Vorlage für die Inventarliste
└── checkups.db             # Die SQLite-Datenbankdatei (wird vom GUI-Tool erstellt)
## Anforderungen

* Python 3.6 oder höher
* Folgende Python-Bibliotheken:
    * `psutil`
    * `Flask`
    * (Optional für das Erstellen der .exe: `pyinstaller`)

## Installation

1.  Klone dieses Repository oder lade die Dateien herunter.
2.  Navigiere im Terminal oder in der Kommandozeile in das Projektverzeichnis.
3.  Installiere die benötigten Bibliotheken über pip:
    ```bash
    pip install psutil Flask
    ```
4.  Wenn du die Desktop-Anwendung als eigenständige `.exe` verteilen möchtest, installiere zusätzlich PyInstaller:
    ```bash
    pip install pyinstaller
    ```

## Verwendung

### 1. Einen PC/Notebook Check-Up durchführen

1.  Stelle sicher, dass du im Projektverzeichnis bist.
2.  Führe das Desktop-Tool aus:
    ```bash
    python system_check_gui.py
    ```
3.  Es öffnet sich ein Fenster. Gib einen **Kundenbezeichner** (z. B. Kundenname, ID oder Standort) in das entsprechende Feld ein.
4.  Klicke auf "Check-Up starten".
5.  Das Tool sammelt die Informationen, zeigt sie im Textfeld an und speichert sie automatisch in der Datei `checkups.db` im selben Verzeichnis.
6.  Schließe das Tool nach Abschluss.

Wenn die Datei `checkups.db` noch nicht existiert, wird sie beim ersten Export erstellt. Wenn du die Datenbankstruktur (z. B. durch Hinzufügen von Spalten) im Code geändert hast, musst du eine bestehende `checkups.db` möglicherweise löschen, damit die neue Struktur angewendet wird (oder die Datenbank manuell aktualisieren).

### 2. Die Inventarliste im Webbrowser ansehen

1.  Stelle sicher, dass die Datei `checkups.db` im selben Verzeichnis wie `app.py` liegt.
2.  Stelle sicher, dass du im Projektverzeichnis bist.
3.  Führe die Flask-Webanwendung aus:
    ```bash
    python app.py
    ```
4.  Die Konsole zeigt an, auf welcher lokalen Adresse der Server läuft (z. B. `http://127.0.0.1:5000/`).
5.  Öffne deinen Webbrowser und navigiere zu dieser Adresse.
6.  Du siehst nun eine Tabelle mit allen Check-Up-Einträgen aus der Datenbank.

Um die Webapp zu stoppen, drücke `Strg + C` im Terminal.

### 3. Desktop-Tool als .exe erstellen (Optional)

Um das Desktop-Tool als eigenständige ausführbare Datei zu verteilen, die kein Python auf dem Zielsystem benötigt:

1.  Stelle sicher, dass PyInstaller installiert ist (`pip install pyinstaller`).
2.  Öffne das Terminal im Projektverzeichnis.
3.  Führe den Befehl aus:
    ```bash
    pyinstaller --onefile --noconsole system_check_gui.py
    ```
4.  Nach Abschluss findest du die ausführbare Datei (`system_check_gui.exe` unter Windows) im Unterordner `dist`.
5.  Wenn du diese `.exe` auf einem anderen PC ausführst, wird die Datei `checkups.db` (oder aktualisierte Einträge darin) im selben Verzeichnis wie die `.exe` erstellt.

## Das Scoring-System (1-10)

Der im Check-Up-Tool berechnete Score ist eine **Schätzung** der Performance basierend auf grundlegenden, auslesbaren Spezifikationen wie der Anzahl der CPU-Kerne, der Größe des Arbeitsspeichers und der Größe der Festplatte(n). Er basiert auf einer einfachen Punktelogik, die in der Funktion `calculate_performance_score` definiert ist.

**Wichtiger Hinweis:** Dieser Score ersetzt keine echten Benchmarks und gibt keine präzise Auskunft über die tatsächliche Leistung des Systems unter spezifischen Workloads. Die Logik kann und sollte bei Bedarf an deine spezifischen Anforderungen und Prioritäten angepasst werden.

## Die Datenbank (`checkups.db`)

Die Datenbank ist eine einzelne SQLite-Datei namens `checkups.db`. Sie enthält die Tabelle `checkups` mit folgenden Spalten (ungefähre Struktur):

* `id`: Eindeutige ID (Primärschlüssel)
* `timestamp`: Datum und Uhrzeit des Checks (Format `JJJJ-MM-TT -- hh:mm:ss`)
* `hostname`: Name des Computers
* `customer_identifier`: Der vom Benutzer eingegebene Kundenname
* `os_system`, `os_release`, `os_version`, `os_machine`: Details zum Betriebssystem
* `cpu_processor`, `cpu_cores_total`, `cpu_frequency_max_mhz`: CPU-Informationen
* `ram_total_bytes`: Größe des Arbeitsspeichers in Bytes
* `gpu_info`: Grundlegende GPU-Information (oft generisch)
* `disks_info_json`: Details zu den Festplatten als JSON-String
* `performance_score`: Der berechnete Score
* `raw_system_info_json`: Die gesamten gesammelten Rohdaten als JSON-String (nützlich für erweiterte Analysen)

Du kannst diese Datei mit Tools wie "DB Browser for SQLite" öffnen, um die Daten direkt anzusehen oder zu bearbeiten.

## Zukünftige Erweiterungen

* **Erweiterte Kundenverwaltung:** Implementierung einer separaten Kundentabelle in der Datenbank und Funktionen in der Webapp zum Erstellen, Bearbeiten und Verwalten von Kunden.
* **Verknüpfung von Checks mit Kunden:** Möglichkeit, Check-Up-Einträge in der Webapp mit Einträgen aus der Kundentabelle zu verknüpfen.
* **Detailliertere Hardware-Erkennung:** Integration von spezifischeren Bibliotheken oder systemeigenen Tools zur besseren Erkennung von CPU-Modellen, GPU-Details etc. (insb. unter Windows mit WMI).
* **Verbessertes Scoring:** Verfeinerung der Scoring-Logik basierend auf spezifischeren Hardware-Modellen oder zusätzlichen Benchmarks.
* **Webapp-Funktionen:** Sortierung, Filterung und Suchfunktion für die Inventarliste. Detailansichten für einzelne Check-Up-Einträge. Export der Liste aus der Webapp (z. B. als CSV).
* **Benutzerverwaltung:** Absicherung der Webapp mit Login-Funktion.
* **Produktions-Deployment:** Anleitungen und Konfiguration für den Betrieb der Webapp auf einem produktiven Webserver (z. B. mit Gunicorn/uWSGI und Nginx/Apache).

## Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).

---