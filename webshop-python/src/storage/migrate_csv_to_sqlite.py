"""
Migrations-Skript: CSV-Daten zu SQLite-Datenbank migrieren
Nutze dieses Skript, um alte CSV-Daten in die neue SQLite-Datenbank zu importieren.
"""

import json
from pathlib import Path
from storage.csv_backend import CSVBackend
from storage.sqlite_backend import SQLiteBackend


def migrate_csv_to_sqlite(csv_folder, db_path):
    """Migriere alle CSV-Daten zu SQLite"""
    print(f"🔄 Starte Migration von {csv_folder} zu {db_path}...")
    
    # Backends initialisieren
    csv = CSVBackend(csv_folder)
    sqlite = SQLiteBackend(db_path)
    
    # ===== USERS MIGRIEREN =====
    print("\n📝 Migriere Benutzer...")
    users = csv.get_all_users()
    for user in users:
        try:
            sqlite.create_user(
                name=user.get('name', ''),
                email=user.get('email', ''),
                password=user.get('password', ''),
                role=user.get('role', 'user'),
                privacy_accept=user.get('privacy_accept', 'False').lower() == 'true',
                marketing_consent=user.get('marketing_consent', 'False').lower() == 'true',
                analytics_consent=user.get('analytics_consent', 'False').lower() == 'true'
            )
            print(f"  ✓ Benutzer '{user.get('email')}' migriert")
        except Exception as e:
            print(f"  ✗ Fehler bei '{user.get('email')}': {e}")
    
    # ===== PRODUCTS MIGRIEREN =====
    print("\n📦 Migriere Produkte...")
    products = csv.get_all_products()
    for product in products:
        try:
            images = product.get('images', [])
            
            # Behandle leere/ungültige stock-Werte
            stock_str = str(product.get('stock', '0')).strip()
            stock = int(stock_str) if stock_str and stock_str.isdigit() else 0
            
            # Behandle leere/ungültige price-Werte
            price_str = str(product.get('price', '0')).strip()
            price = float(price_str) if price_str else 0.0
            
            sqlite.create_product(
                name=product.get('name', ''),
                category=product.get('category', ''),
                price=price,
                description=product.get('description', ''),
                images=images,
                stock=stock
            )
            print(f"  ✓ Produkt '{product.get('name')}' migriert")
        except Exception as e:
            print(f"  ✗ Fehler bei '{product.get('name')}': {e}")
    
    # ===== ORDERS MIGRIEREN =====
    print("\n📋 Migriere Bestellungen...")
    orders_raw = csv.read_csv('orders.csv')
    for order in orders_raw:
        try:
            items = json.loads(order.get('items', '[]')) if order.get('items') else []
            customer = json.loads(order.get('customer', '{}')) if order.get('customer') else {}
            
            # Behandle leere user_id - skip bei fehlend/leer
            user_id_str = str(order.get('user_id', '')).strip()
            if not user_id_str or not user_id_str.isdigit():
                print(f"  ⚠ Bestellung #{order.get('id')} übersprungen (keine user_id)")
                continue
            
            user_id = int(user_id_str)
            total = float(order.get('total', 0)) if order.get('total') else 0.0
            
            order_id = sqlite.create_order(
                user_id=user_id,
                items=items,
                total=total,
                customer=customer,
                payment_provider=order.get('payment_provider'),
                provider_id=order.get('provider_id')
            )
            
            # Update Status falls vorhanden
            if order.get('status'):
                sqlite.update_order_status(order_id, order.get('status'))
            
            print(f"  ✓ Bestellung #{order.get('id')} migriert")
        except Exception as e:
            print(f"  ✗ Fehler bei Bestellung #{order.get('id')}: {e}")
    
    # ===== USER CONSENTS MIGRIEREN =====
    print("\n🔐 Migriere Datenschutz-Einwilligungen...")
    consents = csv.read_csv('user_consents.csv')
    for consent in consents:
        try:
            sqlite.save_consent(
                user_id=int(consent.get('user_id', 0)),
                consent_type=consent.get('consent_type', ''),
                value=consent.get('value', 'False').lower() == 'true'
            )
            print(f"  ✓ Einwilligung für Benutzer {consent.get('user_id')} migriert")
        except Exception as e:
            print(f"  ✗ Fehler bei Einwilligung: {e}")
    
    # ===== AUDIT LOGS MIGRIEREN =====
    print("\n📊 Migriere Audit-Logs...")
    try:
        from utils.logging_service import audit_logger
        logs = audit_logger.get_all_logs(limit=10000)
        for log in logs:
            try:
                sqlite.log_audit(
                    event_type=log.get('event_type', ''),
                    user_id=log.get('user_id'),
                    user_email=log.get('user_email'),
                    action=log.get('action', ''),
                    resource_type=log.get('resource_type'),
                    resource_id=log.get('resource_id'),
                    details=log.get('details'),
                    ip_address=log.get('ip_address'),
                    status=log.get('status', 'success')
                )
            except Exception as e:
                print(f"  ✗ Fehler bei Log-Eintrag: {e}")
        print(f"  ✓ {len(logs)} Audit-Logs migriert")
    except Exception as e:
        print(f"  ⚠ Audit-Logs konnten nicht migriert werden: {e}")
    
    print("\n✅ Migration abgeschlossen!")
    sqlite.close()


if __name__ == '__main__':
    import sys
    from config import CSV_FOLDER_PATH, DB_PATH
    
    # Nutze Command-Line-Argumente oder Standard-Pfade
    csv_folder = sys.argv[1] if len(sys.argv) > 1 else str(CSV_FOLDER_PATH)
    db_path = sys.argv[2] if len(sys.argv) > 2 else str(DB_PATH)
    
    migrate_csv_to_sqlite(csv_folder, db_path)
