# Hausverwaltung - Entwicklung-Workflow

**Stand:** 2026-02-28  
**Autor:** Max & Clawbert

---

## 🚀 Schnellstart

### Projekt öffnen (VS Code Remote)

```bash
# 1. Terminal öffnen und verbinden
ssh clawbert@192.168.178.118

# 2. In Projektordner wechseln
cd ~/.openclaw/workspace/hausverwaltung

# 3. Virtual Environment aktivieren
source venv/bin/activate

# 4. VS Code öffnen (optional, falls nicht schon verbunden)
code .
```

### Python-Interpreter in VS Code wählen

1. `Cmd+Shift+P` (oder `Strg+Shift+P`)
2. "Python: Select Interpreter" eingeben
3. Wählen: `./venv/bin/python`

---

## 📋 Täglicher Workflow

### 1. Projekt starten

```bash
# Terminal im Projektordner
cd ~/.openclaw/workspace/hausverwaltung

# Venv aktivieren
source venv/bin/activate

# Anwendung starten
python main.py
```

### 2. Neue Features entwickeln

```bash
# 1. Neuen Branch erstellen
git checkout -b feature/mein-neues-feature

# 2. Code schreiben...

# 3. Änderungen prüfen
git status
git diff

# 4. Commiten
git add .
git commit -m "feat: Mein neues Feature"

# 5. Pushen
git push origin feature/mein-neues-feature
```

### 3. Tests ausführen

```bash
# Alle Tests
pytest

# Mit Coverage
pytest --cov=.

# Spezifische Test-Datei
pytest test.py -v
```

### 4. Datenbank-Operationen

```bash
# Datenbank neu initialisieren (VORSICHT: Löscht alle Daten!)
python main.py --init-db --force-db

# Datenbank sichern
cp hausverwaltung.db backups/hausverwaltung_$(date +%Y%m%d).db

# Datenbank anzeigen (SQLite)
sqlite3 hausverwaltung.db ".tables"
sqlite3 hausverwaltung.db "SELECT * FROM properties;"
```

---

## 🛠️ Entwicklung

### Neue Abhängigkeiten hinzufügen

```bash
# 1. Paket installieren
pip install paket-name

# 2. requirements.txt updaten
pip freeze > requirements.txt

# 3. Commiten
git add requirements.txt
git commit -m "chore: Add paket-name to dependencies"
```

### Neue Module erstellen

```bash
# Beispiel: Neues Modul "export"
mkdir export
touch export/__init__.py
touch export/export.py
touch export/README.md
```

### Code-Formatierung

```bash
# Mit Black (falls installiert)
black .

# Mit autopep8
autopep8 --in-place --aggressive --aggressive .
```

---

## 📝 Git Best Practices

### Commit-Messages

```
feat: Neue Funktion hinzugefügt
fix: Bug behoben
refactor: Code umstrukturiert
docs: Dokumentation aktualisiert
test: Tests hinzugefügt
chore: Wartung (dependencies, config)
style: Formatierung (keine Code-Änderung)
```

### Branch-Namen

```
feature/beschreibung      # Neue Features
fix/beschreibung          # Bugfixes
refactor/beschreibung     # Refactoring
docs/beschreibung         # Dokumentation
```

### Vor jedem Push

```bash
# 1. Tests laufen lassen
pytest

# 2. Status prüfen
git status

# 3. Auf main wechseln und pullen
git checkout main
git pull origin main

# 4. Branch mergen (optional)
git merge feature/mein-feature

# 5. Pushen
git push origin main
```

---

## 🔧 Debugging

### Anwendung mit Debug-Output

```bash
# Mit Loguru (bereits installiert)
LOG_LEVEL=DEBUG python main.py
```

### Datenbank-Inspektion

```bash
# Tabellen anzeigen
sqlite3 hausverwaltung.db ".schema"

# Alle Properties
sqlite3 hausverwaltung.db "SELECT * FROM properties;"

# Alle Mieter
sqlite3 hausverwaltung.db "SELECT * FROM tenants;"
```

### Python-Debugger

```python
# Im Code
import pdb; pdb.set_trace()

# Oder mit breakpoint()
breakpoint()
```

---

## 📊 Anwendung nutzen

### Immobilien hinzufügen

```bash
python main.py --add-property
```

### Mieter hinzufügen

```bash
python main.py --add-tenant
```

### Dashboard anzeigen

```bash
python main.py --dashboard
```

---

## 🧹 Wartung

### Regelmäßige Tasks

| Task | Frequenz | Befehl |
|------|----------|--------|
| DB Backup | Täglich | `cp hausverwaltung.db backups/` |
| Tests | Vor jedem Push | `pytest` |
| Git Pull | Vor jedem Start | `git pull origin main` |
| Requirements update | Nach pip install | `pip freeze > requirements.txt` |

### Aufräumen

```bash
# Python Cache löschen
find . -type d -name "__pycache__" -exec rm -rf {} +

# Alte Logs löschen
rm logs/*.log

# Alte Backups löschen (älter als 30 Tage)
find backups/ -name "*.db" -mtime +30 -delete
```

---

## 🚨 Häufige Probleme

### "ModuleNotFoundError: No module named 'config'"

```bash
# Virtual Environment aktivieren!
source venv/bin/activate
```

### "unable to open database file"

```bash
# Prüfen ob DB als Verzeichnis erstellt wurde
ls -la hausverwaltung.db

# Falls Verzeichnis: Löschen und neu initialisieren
rm -rf hausverwaltung.db
python main.py --init-db
```

### "Permission denied"

```bash
# Ausführungsrechte geben
chmod +x main.py
```

---

## 📚 Nützliche Befehle

### Git

```bash
git status              # Status
git log --oneline       # Kurzes Log
git diff                # Änderungen
git stash               # Änderungen zwischenspeichern
git stash pop           # Stash wiederherstellen
```

### Python

```bash
python -m venv venv     # Venv erstellen
pip install -r requirements.txt  # Dependencies installieren
pip freeze              # Installierte Pakete anzeigen
```

### SQLite

```bash
sqlite3 db.db ".tables"           # Tabellen anzeigen
sqlite3 db.db ".schema table"     # Schema anzeigen
sqlite3 db.db ".mode column"      # Bessere Ausgabe
```

---

## 🔗 Links

- **GitHub:** https://github.com/blindidiotscout/hausverwaltung
- **VS Code Remote:** `ssh clawbert@192.168.178.118`
- **Projektpfad:** `~/.openclaw/workspace/hausverwaltung`

---

*Erstellt mit Clawbert 🤖*