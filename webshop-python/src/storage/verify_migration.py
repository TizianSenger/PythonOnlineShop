#!/usr/bin/env python3
"""Verifiziere die migrierten Daten in der SQLite-Datenbank"""

import sqlite3
from pathlib import Path

# Nutze den gleichen Pfad wie in config.py
db_path = Path(__file__).parent.parent.parent / 'data' / 'webshop.db'
print(f"📊 Verifiziere Daten in: {db_path}\n")

if not db_path.exists():
    print(f"❌ Datenbank-Datei nicht gefunden: {db_path}")
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Users
print("👥 Users in der Datenbank:")
cursor.execute('SELECT id, name, email FROM users')
users = cursor.fetchall()
for user_id, name, email in users:
    print(f"  ✓ ID {user_id}: {email}")
print(f"  Total: {len(users)} users\n")

# Products
print("📦 Products in der Datenbank:")
cursor.execute('SELECT id, name, category, price FROM products')
products = cursor.fetchall()
for product_id, name, category, price in products:
    print(f"  ✓ ID {product_id}: {name} ({category}) - €{price}")
print(f"  Total: {len(products)} products\n")

# Orders
print("📋 Orders in der Datenbank:")
cursor.execute('SELECT id, user_id, total, status FROM orders')
orders = cursor.fetchall()
for order_id, user_id, total, status in orders:
    print(f"  ✓ Bestellung #{order_id}: User {user_id}, €{total}, Status: {status}")
print(f"  Total: {len(orders)} orders\n")

# Audit Logs
print("📊 Audit Logs in der Datenbank:")
cursor.execute('SELECT COUNT(*) FROM audit_log')
log_count = cursor.fetchone()[0]
print(f"  ✓ Total: {log_count} audit logs\n")

# Summary
print("✅ Migration-Zusammenfassung:")
print(f"  • {len(users)} Benutzer migriert")
print(f"  • {len(products)} Produkte migriert")
print(f"  • {len(orders)} Bestellungen migriert")
print(f"  • {log_count} Audit Logs migriert")

conn.close()
