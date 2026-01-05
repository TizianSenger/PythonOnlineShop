# 🛒 PythonOnlineShop

Ein vollständiges Online-Shop-System entwickelt mit Python und Flask, inklusive Admin-Panel, Warenkorbfunktionalität, Bestellverwaltung und DSGVO-konformen Datenschutzfunktionen.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Inhaltsverzeichnis

- [Features](#-features)
- [Technologie-Stack](#-technologie-stack)
- [Installation](#-installation)
- [Konfiguration](#-konfiguration)
- [Verwendung](#-verwendung)
- [Projektstruktur](#-projektstruktur)
- [DSGVO-Compliance](#-dsgvo-compliance)
- [API-Endpunkte](#-api-endpunkte)
- [Datenbank](#-datenbank)
- [Tests](#-tests)
- [Screenshots](#-screenshots)
- [Mitwirkende](#-mitwirkende)
- [Lizenz](#-lizenz)

## ✨ Features

### 🛍️ Shop-Funktionen
- **Produktkatalog** mit Kategorien, Preisen und Bildern
- **Erweiterte Suche** und Filterung nach Kategorie, Preis und Suchbegriff
- **Multi-Image-Support** für Produkte (bis zu 20 Bilder pro Produkt)
- **Warenkorb-System** mit Mengenänderung und Produktentfernung
- **Bestellverwaltung** mit Statusverfolgung
- **Responsive Design** für Desktop und Mobile

### 👨‍💼 Admin-Features
- **Admin-Dashboard** zur Produktverwaltung
- **Produkte hinzufügen, bearbeiten und löschen**
- **Bestandsverwaltung** (Stock Management)
- **Bestellübersicht** mit Statusaktualisierung
- **Inventarwertberechnung**
- **Bilderverwaltung** mit Upload-Funktion

### 🔐 Benutzer & Authentifizierung
- **Registrierung** mit Rollen (User/Admin)
- **Login/Logout-System**
- **Passwort-Hashing** mit Werkzeug Security
- **Session-Management**
- **Admin-PIN-Schutz** für Admin-Registrierung

### 📦 Checkout & Zahlungen
- **Checkout-Prozess** mit Kundeninformationen
- **Payment-Provider-Integration** (Stripe, PayPal vorbereitet)
- **Bestellbestätigungs-E-Mails**
- **Bestellstatusanzeige** (pending, paid, in_bearbeitung, vorbereitung_transport, abgeschickt, zugestellt)

### 🛡️ DSGVO-Compliance
- **Cookie-Consent-Banner**
- **Datenschutzerklärung** und Impressum
- **AGB** (Allgemeine Geschäftsbedingungen)
- **Betroffenenrechte** (Art. 12-22 DSGVO)
- **Datenexport** (JSON/CSV)
- **Recht auf Vergessenwerden** (Account-Löschung)
- **Einwilligungsverwaltung**
- **Audit-Logging** für wichtige Aktionen

### 💾 Datenspeicherung
- **Hybrid-Backend**:  SQLite + CSV-Fallback
- **Flexible Storage-Layer** (leicht erweiterbar)
- **Datenmigration** zwischen Backends
- **Backup-Funktionalität**

## 🚀 Technologie-Stack

- **Backend**: Python 3.8+, Flask 2.0+
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap (angenommen)
- **Datenbank**: SQLite3 (Entwicklung), PostgreSQL/MySQL (Produktion möglich)
- **Daten-Fallback**: CSV-Backend
- **Session-Management**: Flask Session (Cookie-basiert)
- **Sicherheit**: Werkzeug Password Hashing
- **E-Mail**:  SMTP (Gmail)
- **Datei-Uploads**: Secure Filename (Werkzeug)
- **Logging**: Custom Audit Logger

## 📥 Installation

### Voraussetzungen

- Python 3.8 oder höher
- pip (Python Package Manager)
- Git

### Schritt-für-Schritt-Anleitung

1. **Repository klonen**
   ```bash
   git clone https://github.com/TizianSenger/PythonOnlineShop.git
   cd PythonOnlineShop/webshop-python
   ```

2. **Virtuelle Umgebung erstellen**
   ```bash
   python -m venv . venv
   
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Abhängigkeiten installieren**
   ```bash
   pip install -r requirements.txt
   ```

4. **Umgebungsvariablen konfigurieren**
   
   Erstelle eine `.env`-Datei im `webshop-python`-Verzeichnis:
   ```env
   SECRET_KEY=dein-sicherer-geheimer-schluessel
   SMTP_USER=deine-email@gmail.com
   SMTP_PASS=dein-app-passwort
   ADMIN_PIN=dein-admin-pin
   USE_DATABASE=True
   DB_PATH=data/webshop.db
   CSV_FOLDER_PATH=data/csv
   ```

5. **Datenbank initialisieren**
   ```bash
   python src/app.py
   ```

6. **Anwendung starten**
   ```bash
   python src/app. py
   ```

7. **Im Browser öffnen**
   ```
   http://127.0.0.1:5000
   ```

## ⚙️ Konfiguration

### Config-Datei (`src/config.py`)

```python
SECRET_KEY = "dein-geheimer-schluessel"
SMTP_USER = "email@example.com"
SMTP_PASS = "password"
ADMIN_PIN = "1234"  # Für Admin-Registrierung
USE_DATABASE = True  # True = SQLite, False = CSV
DB_PATH = "data/webshop.db"
CSV_FOLDER_PATH = "data/csv"
```

### E-Mail-Konfiguration

Für Gmail:
1. Gehe zu [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Erstelle ein App-Passwort für "Mail"
3. Verwende dieses Passwort in `SMTP_PASS`

## 🎮 Verwendung

### Als normaler Benutzer

1. **Registrieren**:  Erstelle ein Konto unter `/register`
2. **Einloggen**: Melde dich an unter `/login`
3. **Stöbern**: Durchsuche Produkte auf der Startseite
4. **In den Warenkorb**: Produkte hinzufügen
5. **Checkout**: Bestellung abschließen
6. **Bestellungen ansehen**: Deine Bestellungen unter `/orders`

### Als Admin

1. **Admin-Registrierung**: Registriere dich mit dem Admin-PIN
2. **Produkte verwalten**: Gehe zu `/admin/products`
3. **Produkte hinzufügen**:  Füge neue Produkte mit Bildern hinzu
4. **Bestellungen verwalten**: Ändere Bestellstatus
5. **Inventar überwachen**: Sieh Gesamtwert des Inventars

### DSGVO-Funktionen

- **Datenauskunft**: `/gdpr/data-export` - Sieh alle deine Daten
- **Datenexport**:  Exportiere als JSON oder CSV
- **Account löschen**: `/gdpr/delete-account` - Lösche alle Daten
- **Präferenzen**: `/preferences` - Verwalte Einwilligungen

## 📁 Projektstruktur

```
webshop-python/
├── src/
│   ├── app.py                    # Haupt-Flask-Anwendung
│   ├── config.py                 # Konfiguration
│   ├── models/                   # Datenmodelle
│   │   ├── product.py
│   │   ├── user.py
│   │   └── order.py
│   ├── storage/                  # Backend-Implementierungen
│   │   ├── csv_backend.py
│   │   ├── sqlite_backend. py
│   │   └── hybrid_backend.py
│   ├── api/                      # API-Routes
│   │   ├── routes.py
│   │   └── checkout_routes.py
│   ├── services/                 # Business Logic
│   │   ├── catalog. py
│   │   └── checkout.py
│   ├── utils/                    # Hilfsfunktionen
│   │   ├── helpers.py
│   │   └── logging_service.py
│   ├── templates/                # HTML-Templates
│   └── static/                   # CSS, JS, Bilder
│       └── uploads/              # Hochgeladene Produktbilder
├── data/
│   ├── csv/                      # CSV-Daten (Fallback)
│   └── webshop.db                # SQLite-Datenbank
├── tests/                        # Unit-Tests
├── requirements.txt
├── pyproject.toml
└── README.md
```

## 🔒 DSGVO-Compliance

Dieses Projekt implementiert wichtige DSGVO-Anforderungen:

### Rechtsgrundlagen
- ✅ **Art. 13/14 DSGVO**:  Informationspflichten (Datenschutzerklärung)
- ✅ **Art.  15 DSGVO**:  Auskunftsrecht (Datenexport)
- ✅ **Art. 16 DSGVO**:  Recht auf Berichtigung (Profil-Edit)
- ✅ **Art. 17 DSGVO**: Recht auf Vergessenwerden (Account-Löschung)
- ✅ **Art. 20 DSGVO**: Datenportabilität (JSON/CSV-Export)
- ✅ **Art.  30 DSGVO**: Verzeichnis von Verarbeitungstätigkeiten (Audit-Log)

### Implementierte Features
- Cookie-Consent-Management
- Einwilligungsverwaltung für Marketing und Analytics
- Audit-Logging aller wichtigen Aktionen
- Verschlüsselte Passwortspeicherung
- Session-Management mit Timeouts
- IP-Adressen-Logging (anonymisierbar)

## 🌐 API-Endpunkte

### Öffentliche Endpunkte
```
GET  /                          # Startseite mit Produkten
GET  /product/<product_id>      # Produktdetails
GET  /register                  # Registrierungsformular
POST /register                  # Registrierung absenden
GET  /login                     # Login-Formular
POST /login                     # Login absenden
GET  /logout                    # Logout
```

### Geschützte Endpunkte (Login erforderlich)
```
GET  /dashboard                 # Benutzer-Dashboard
GET  /cart                      # Warenkorb
POST /add-to-cart               # Produkt in Warenkorb
POST /remove-from-cart/<id>     # Produkt aus Warenkorb
POST /update-cart/<id>          # Warenkorb aktualisieren
GET  /orders                    # Bestellungen anzeigen
```

### Admin-Endpunkte
```
GET  /admin/products            # Produktverwaltung
POST /admin/products            # Neues Produkt erstellen
GET  /admin/edit-product/<id>  # Produkt bearbeiten
POST /admin/edit-product/<id>  # Produkt aktualisieren
POST /admin/delete-product/<id> # Produkt löschen
POST /admin/update-order-status/<id> # Bestellstatus ändern
POST /admin/delete-order/<id>   # Bestellung löschen
```

### DSGVO-Endpunkte
```
GET  /privacy-policy            # Datenschutzerklärung
GET  /impressum                 # Impressum
GET  /terms-of-service          # AGB
GET  /gdpr-rights               # Betroffenenrechte
GET  /gdpr/data-export          # Daten anzeigen
POST /gdpr/export-data          # Daten exportieren (JSON/CSV)
POST /gdpr/delete-account       # Account löschen
GET  /preferences               # Einstellungen
GET  /profile/edit              # Profil bearbeiten
```

## 💾 Datenbank

### SQLite-Schema

**Tabellen:**
- `users` - Benutzerkonten
- `products` - Produktkatalog
- `orders` - Bestellungen
- `order_items` - Bestellpositionen
- `consents` - DSGVO-Einwilligungen
- `audit_logs` - Audit-Trail

### Migration

Siehe [DATABASE_MIGRATION.md](webshop-python/DATABASE_MIGRATION.md) für Details zur Datenmigration zwischen CSV und SQLite.

## 🧪 Tests

Tests ausführen:
```bash
pytest tests/
```

Mit Coverage: 
```bash
pytest --cov=src tests/
```

## 🤝 Mitwirkende

- **Tizian Senger** - *Initial Work* - [@TizianSenger](https://github.com/TizianSenger)

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) für Details.

## 📞 Kontakt

Bei Fragen oder Problemen erstelle bitte ein [Issue](https://github.com/TizianSenger/PythonOnlineShop/issues).

---

**⚠️ Hinweis**: Dieses Projekt dient zu Lern- und Demonstrationszwecken. Für den Produktiveinsatz sollten zusätzliche Sicherheits- und Performance-Optimierungen vorgenommen werden. 
