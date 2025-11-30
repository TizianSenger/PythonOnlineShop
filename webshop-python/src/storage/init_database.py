#!/usr/bin/env python3
"""
Initialisiert die SQLite-Datenbank von Grund auf.
Löscht die alte Datei und erstellt neue Tabellen.
"""

import sqlite3
import os
import sys
from pathlib import Path

def init_database(db_path='webshop.db'):
    """Initialisiere die Datenbank"""
    
    # Konvertiere zu Path-Objekt
    db_path = Path(db_path)
    
    # Lösche alte Datei falls vorhanden
    if db_path.exists():
        try:
            db_path.unlink()
            print(f"✓ Alte Datenbank gelöscht: {db_path}")
        except Exception as e:
            print(f"✗ Fehler beim Löschen: {e}")
            return False
    
    # Stelle sicher, dass Parent-Verzeichnis existiert
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Verbinde zur neuen Datenbank
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    print(f"📁 Neue Datenbank erstellt: {db_path}")
    
    # Users Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            privacy_accept BOOLEAN DEFAULT 0,
            marketing_consent BOOLEAN DEFAULT 0,
            analytics_consent BOOLEAN DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✓ Tabelle 'users' erstellt")
    
    # Products Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL NOT NULL,
            description TEXT,
            images TEXT,
            stock INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✓ Tabelle 'products' erstellt")
    
    # Orders Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            items TEXT NOT NULL,
            total REAL NOT NULL,
            customer TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            payment_provider TEXT,
            provider_id TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("  ✓ Tabelle 'orders' erstellt")
    
    # User Consents Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_consents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            consent_type TEXT NOT NULL,
            value BOOLEAN NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("  ✓ Tabelle 'user_consents' erstellt")
    
    # Audit Log Tabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT NOT NULL,
            user_id INTEGER,
            user_email TEXT,
            action TEXT NOT NULL,
            resource_type TEXT,
            resource_id TEXT,
            details TEXT,
            ip_address TEXT,
            status TEXT DEFAULT 'success'
        )
    ''')
    print("  ✓ Tabelle 'audit_log' erstellt")
    
    conn.commit()
    conn.close()
    
    print("✅ Datenbank erfolgreich initialisiert!")
    return True

if __name__ == '__main__':
    # Bestimme den Datenbankpfad
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        # Verwende den Standardpfad relativ zum Skript
        base_path = Path(__file__).parent.parent.parent / 'data' / 'webshop.db'
        db_path = str(base_path)
    
    success = init_database(db_path)
    sys.exit(0 if success else 1)
