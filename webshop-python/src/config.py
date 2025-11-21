import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = (BASE_DIR.parent / "data" / "csv")
DATA_DIR.mkdir(parents=True, exist_ok=True)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# SMTP (für Bestätigungs-E-Mails)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

# Admin PIN
ADMIN_PIN = os.getenv("ADMIN_PIN", "1234")

# CSV Speicherort
CSV_FOLDER_PATH = DATA_DIR

# Stripe (Test keys)
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")

# PayPal (Sandbox)
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "")
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")

# PayPal Test Accounts (Sandbox credentials for reference)
PAYPAL_BUSINESS_EMAIL = os.getenv("PAYPAL_BUSINESS_EMAIL", "")
PAYPAL_BUSINESS_PASSWORD = os.getenv("PAYPAL_BUSINESS_PASSWORD", "")
PAYPAL_BUYER_EMAIL = os.getenv("PAYPAL_BUYER_EMAIL", "")
PAYPAL_BUYER_PASSWORD = os.getenv("PAYPAL_BUYER_PASSWORD", "")

# App URLs
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:5000")