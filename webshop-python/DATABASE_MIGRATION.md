# 🗄️ Datenbank-Migration: CSV → SQLite

Dein WebShop unterstützt jetzt zwei Speicher-Modi mit automatischem Fallback:

## Übersicht

### **Hybrid-Backend**
- **Primär**: SQLite (schneller, strukturiert)
- **Fallback**: CSV (Backup, wenn SQLite ausfällt)
- **Synchron**: Alle Daten werden in beide geschrieben

### Vorteile
✅ Bessere Performance mit SQLite
✅ Strukturierte Datenqueries möglich
✅ Automatisches Fallback zu CSV bei Fehlern
✅ Graduelle Migration möglich
✅ Keine Datenverluste

---

## 🚀 Schnellstart

### 1. Konfiguration (`.env`)

```bash
# Aktiviere SQLite-Backend
USE_DATABASE=true

# Optional: Custom Datenbank-Pfad
DATABASE_URL=sqlite:///path/to/webshop.db
```

### 2. Migration durchführen

```bash
cd src
python -m storage.migrate_csv_to_sqlite
```

Oder mit Custom-Pfaden:
```bash
python -m storage.migrate_csv_to_sqlite /path/to/csv /path/to/db.sqlite
```

### 3. App starten

```bash
python app.py
```

Die App verwendet jetzt automatisch:
1. **SQLite** als primäres Speichersystem
2. **CSV** als Fallback (wenn DB nicht verfügbar)
3. Alle neuen Operationen schreiben in beide

---

## 📊 Architektur

```
┌─────────────────────────────────┐
│      Flask App (app.py)          │
└────────────┬────────────────────┘
             │
      ┌──────▼──────┐
      │ HybridBackend│  ◄── Orchestriert beide Systeme
      └──────┬───────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐      ┌──────────┐
│ SQLite  │      │   CSV    │
│  (Fast) │      │ (Backup) │
└─────────┘      └──────────┘
```

---

## 🔄 Hybrid-Logik

### Lesezugriffe
```
1. Versuche SQLite
   ├─ Erfolgreich? → Rückgabe
   └─ Fehler? → 
2. Fallback zu CSV
   ├─ Erfolgreich? → Rückgabe + Log Fallback
   └─ Fehler? → Fehler werfen
```

### Schreibzugriffe
```
1. Schreibe in SQLite
   ├─ Erfolgreich? → Log
   └─ Fehler? → Log aber weiter
2. Schreibe AUCH in CSV
   ├─ Erfolgreich? → Abschluss
   └─ Fehler? → Warnung aber abschluss
```

### Fallback-Tracking
```python
# Alle Fallback-Ereignisse protokollieren
fallback_log = backend.get_fallback_log()
```

---

## 📋 Migrierte Daten

- ✅ **Benutzer** (name, email, password, rolle, consent-flags)
- ✅ **Produkte** (name, preis, beschreibung, bilder, bestand)
- ✅ **Bestellungen** (items, total, kunde, zahlung, status)
- ✅ **Consents** (privacy, marketing, analytics)
- ✅ **Audit-Logs** (event-typ, user, aktion, ressource, details)

---

## 🛡️ DSGVO-Features

Alle DSGVO-Features funktionieren automatisch:
- **Art. 15** - Datenexport (von SQLite oder CSV)
- **Art. 17** - Löschung (aus beiden Systemen)
- **Audit-Trail** - Vollständig protokolliert
- **Consent-Management** - In beiden Systemen

---

## 📖 Verwendung im Code

### Alte Weise (nur CSV)
```python
from storage.csv_backend import CSVBackend
backend = CSVBackend(csv_folder)
```

### Neue Weise (Hybrid mit Fallback)
```python
from storage.csv_backend import CSVBackend
from storage.sqlite_backend import SQLiteBackend
from storage.hybrid_backend import HybridBackend

csv = CSVBackend(csv_folder)
sqlite = SQLiteBackend(db_path)
backend = HybridBackend(csv, sqlite)

# Nutze normal - automatisches Fallback!
users = backend.get_all_users()
backend.create_user(name, email, password)
```

---

## 🧪 Debugging

### Fallback-Logbuch ansehen
```python
logs = backend.get_fallback_log()
for log in logs:
    print(f"Fallback in {log['method']}: {log['error']}")
```

### SQLite-DB direkt ansehen
```bash
sqlite3 data/webshop.db
sqlite> SELECT name FROM sqlite_master WHERE type='table';
sqlite> SELECT COUNT(*) FROM users;
```

### CSV-Backup verifizieren
```bash
head -5 data/csv/users.csv
head -5 data/csv/products.csv
```

---

## ⚠️ Häufige Probleme

### Problem: "SQLite Backend nicht initialisiert"
```
Lösung: USE_DATABASE=true in .env setzen und App neu starten
```

### Problem: "Datenbank gesperrt"
```
Lösung: Stelle sicher, nur eine App-Instanz läuft
```

### Problem: "Migration schlägt bei Audit-Logs fehl"
```
Lösung: Audit-Logs sind optional - Warnung ist normal
```

---

## 📝 Befehle

```bash
# Migration starten
python -m storage.migrate_csv_to_sqlite

# App mit SQLite
USE_DATABASE=true python app.py

# App mit nur CSV (Fallback)
USE_DATABASE=false python app.py

# Datenbank inspizieren
sqlite3 data/webshop.db ".tables"
sqlite3 data/webshop.db ".dump users"
```

---

## 🎯 Nächste Schritte

1. ✅ Migration durchgeführt
2. ✅ Hybrid-Backend aktiv
3. ⏭️ Monitoring/Logging für Fallbacks
4. ⏭️ Performance-Optimierung (Indizes)
5. ⏭️ Redundanz/Backups einrichten

---

**Fragen?** Siehe Hybrid-Backend-Dokumentation oder check app.py für Beispiele.
