# ...existing code...
import os

# Geheimnis für Sessions (in Produktion als Umgebungsvariable setzen)
SECRET_KEY = os.environ.get("WEBSHOP_SECRET_KEY", "dev-secret-key-please-change")

# SMTP (für Gmail App-Passwort). In Produktion per ENV setzen:
SMTP_USER = os.environ.get("WEBSHOP_SMTP_USER", "tischenswebshop@gmail.com")
SMTP_PASS = os.environ.get("WEBSHOP_SMTP_PASS", "lrzz pcpo tcsl dmee")

# Admin PIN (default 1234). In Produktion per ENV ändern.
ADMIN_PIN = os.environ.get("WEBSHOP_ADMIN_PIN", "1234")

# Pfad zu CSV-Daten (data/csv)
CSV_FOLDER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "csv"))