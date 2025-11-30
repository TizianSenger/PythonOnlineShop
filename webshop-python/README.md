# Webshop Python Project

This project is a simple webshop application built with Python. It provides functionalities for managing products, users, and orders, with data stored either in CSV files or an SQLite database.

## Project Structure

```
webshop-python/
│
├── 📋 Dokumentation & Konfiguration
│   ├── README.md                          # Projekt-Übersicht
│   ├── DATABASE_MIGRATION.md              # Datenbank-Migrationsleitfaden
│   ├── IMPLEMENTATION_SUMMARY.md          # Implementierungs-Zusammenfassung
│   ├── QUICK_START_DATABASE.md            # Schnellstart für Datenbank
│   ├── pyproject.toml                     # Python-Projekt-Konfiguration
│   └── requirements.txt                   # Python-Dependencies
│
├── 📁 data/                               # Datenspeicherung
│   ├── csv/                               # CSV-Dateien (Legacy-Speicher)
│   │   ├── orders.csv                     # Bestellungen
│   │   ├── products.csv                   # Produkte
│   │   ├── user_consents.csv              # Benutzer-Zustimmungen (GDPR)
│   │   └── users.csv                      # Benutzer
│   └── logs/
│       └── audit_log.csv                  # Audit-Log
│
├── 📁 src/                                # Hauptanwendung
│   ├── app.py                             # Flask-Hauptanwendung
│   ├── config.py                          # Konfigurationseinstellungen
│   │
│   ├── 📁 api/                            # API-Endpoints
│   │   ├── __init__.py
│   │   └── checkout_routes.py             # Checkout-Logik
│   │
│   ├── 📁 services/                       # Business-Logik
│   │   ├── checkout.py                    # Checkout-Service
│   │   └── __pycache__/
│   │
│   ├── 📁 storage/                        # Datenspeicher-Layer
│   │   ├── __init__.py
│   │   ├── csv_backend.py                 # CSV-Speicher
│   │   ├── sqlite_backend.py              # SQLite-Speicher
│   │   ├── hybrid_backend.py              # Hybrid (CSV + SQLite)
│   │   ├── init_database.py               # DB-Initialisierung
│   │   ├── migrate_csv_to_sqlite.py       # Migration CSV → SQLite
│   │   ├── verify_migration.py            # Migrationsprüfung
│   │   └── __pycache__/
│   │
│   ├── 📁 utils/                          # Hilfsfunktionen
│   │   ├── helpers.py                     # Allgemeine Helper
│   │   ├── logging_service.py             # Logging-Service
│   │   └── __pycache__/
│   │
│   ├── 📁 static/                         # Statische Assets
│   │   ├── style.css                      # CSS-Stylesheet
│   │   └── uploads/                       # Produkt-Bilder
│   │
│   └── 📁 templates/                      # HTML-Templates (Jinja2)
│       ├── base.html                      # Base-Template
│       ├── index.html                     # Homepage/Shop
│       ├── product_detail.html            # Produktdetails
│       ├── cart.html                      # Warenkorb
│       ├── checkout.html                  # Checkout
│       ├── confirmation.html              # Bestellbestätigung
│       ├── login.html                     # Login
│       ├── register.html                  # Registrierung
│       ├── profile_edit.html              # Profilbearbeitung
│       ├── dashboard.html                 # Benutzer-Dashboard
│       ├── orders.html                    # Bestellungsübersicht (Admin)
│       ├── admin_products.html            # Produktverwaltung (Admin)
│       ├── edit_product.html              # Produktbearbeitung (Admin)
│       ├── gdpr_rights.html               # GDPR-Rechte
│       ├── gdpr_data_view.html            # GDPR-Datenansicht
│       ├── privacy_policy.html            # Datenschutzerklärung
│       ├── terms_of_service.html          # AGB
│       ├── impressum.html                 # Impressum
│       ├── preferences.html               # Einstellungen
│       ├── cookie_banner.html             # Cookie-Banner
│       └── __pycache__/
│
└── 📁 tests/                              # Unit-Tests
    ├── test_catalog.py                    # Katalog-Tests
    └── test_storage.py                    # Speicher-Tests
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd webshop-python
   ```

2. **Install dependencies**:
   It is recommended to use a virtual environment. You can create one using:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
   Then install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. **Run the application**:
   Start the application by running:
   ```
   python src/app.py
   ```

## Usage

- Access the webshop through the provided API endpoints.
- Use the CSV files in the `data/csv` directory for initial data or switch to the SQLite backend for a more robust solution.

## Testing

Run the tests using:
```
pytest tests/
```

## License

This project is licensed under the MIT License.
