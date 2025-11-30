# 🚀 Schnelle Umstellung auf SQLite

Folge diesen einfachen Schritten, um deinen Shop auf SQLite mit automatischem CSV-Fallback umzustellen:

## Schritt 1️⃣: Konfiguration

Öffne `.env` und füge diese Zeile hinzu (oder ändere sie):

```bash
USE_DATABASE=true
```

## Schritt 2️⃣: Daten migrieren

Navigiere zur `src` Ordner und führe aus:

```bash
cd src
python -m storage.migrate_csv_to_sqlite
```

Du siehst:
```
🔄 Starte Migration von data/csv zu data/webshop.db...

📝 Migriere Benutzer...
  ✓ Benutzer 'max@example.com' migriert
  ✓ Benutzer 'anna@example.com' migriert

📦 Migriere Produkte...
  ✓ Produkt 'Laptop' migriert
  ✓ Produkt 'Mouse' migriert

... etc ...

✅ Migration abgeschlossen!
```

## Schritt 3️⃣: App starten

```bash
python app.py
```

Die App lädt jetzt beide Backends:
- **SQLite** ist die primäre Datenbank
- **CSV** als Fallback (falls SQLite ausfällt)

---

## ✅ Fertig!

Dein Shop nutzt jetzt:
- ⚡ **SQLite** für schnelle Datenbankabfragen
- 🛡️ **Automatisches Fallback** zu CSV bei Problemen
- 🔄 **Duale Synchronisierung** - alles in beide geschrieben
- 📊 **Vollständige DSGVO-Unterstützung** in beiden Systemen

---

## 📊 Wie es funktioniert

```
┌─────────────────────────────┐
│     Your Flask App          │
└──────────────┬──────────────┘
               │
         ┌─────▼─────┐
         │  Hybrid   │ ← Automatisch!
         │  Backend  │
         └─────┬─────┘
               │
        ┌──────┴──────┐
        │             │
    ┌───▼─┐      ┌────▼──┐
    │ 💾 │      │ 📄 │
    │SQLite│      │ CSV  │
    │(FAST)│      │(Safe)│
    └──────┘      └──────┘
```

**Lesezugriffe**: SQLite → falls Fehler → CSV
**Schreibzugriffe**: In beide Systeme gleichzeitig

---

## 🎯 Wichtige Commands

```bash
# Migration durchführen
cd src && python -m storage.migrate_csv_to_sqlite

# App starten
python app.py

# SQLite Datenbank inspizieren
sqlite3 data/webshop.db ".tables"
sqlite3 data/webshop.db "SELECT COUNT(*) FROM users;"

# Alte CSV-Backups anschauen (als Fallback noch da!)
head -5 data/csv/users.csv
head -5 data/csv/products.csv
```

---

## ❓ Häufige Fragen

**F: Was passiert mit meinen alten CSV-Dateien?**
A: Sie bleiben als Backup erhalten! Das Hybrid-Backend nutzt sie automatisch als Fallback.

**F: Kann ich zurück zu nur CSV?**
A: Ja! Setze einfach `USE_DATABASE=false` in `.env`

**F: Wird alles doppelt gespeichert?**
A: Ja - Schreibzugriffe gehen in beide Systeme. Das ist sicher & redundant!

**F: Wie schnell ist es?**
A: SQLite ist 10-100x schneller als CSV bei vielen Produkten/Benutzern.

**F: Was ist mit DSGVO?**
A: Alle DSGVO-Features funktionieren gleich - Export, Löschung, Audit-Logs etc.

---

## 🚨 Falls was schiefgeht

1. **App startet nicht**: Check `.env` Datei und DB-Pfad
2. **Daten fehlen**: CSV-Fallback ist still da, migration erneut durchführen
3. **Datenbank gesperrt**: Nur eine App-Instanz gleichzeitig!

```bash
# Fallback-Logs ansehen:
# (In Python Console)
from storage.hybrid_backend import HybridBackend
logs = backend.get_fallback_log()
for log in logs:
    print(log)
```

---

## 📚 Mehr Infos

Siehe `DATABASE_MIGRATION.md` für vollständige Dokumentation.

---

**Happy Coding! 🎉**
