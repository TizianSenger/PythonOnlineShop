import sqlite3
import json
from datetime import datetime
from pathlib import Path

class SQLiteBackend:
    def __init__(self, db_path='webshop.db'):
        self.db_path = db_path
        self.connection = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Verbinde zur SQLite Datenbank"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def close(self):
        """Schließe die Datenbankverbindung"""
        if self.connection:
            self.connection.close()

    def create_tables(self):
        """Erstelle alle notwendigen Tabellen"""
        cursor = self.connection.cursor()
        
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
        
        self.connection.commit()

    # ===== USER OPERATIONS =====
    
    def get_user_by_id(self, user_id):
        """Hole einen Benutzer nach ID"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_user_by_email(self, email):
        """Hole einen Benutzer nach E-Mail"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_users(self):
        """Hole alle Benutzer"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM users')
        return [dict(row) for row in cursor.fetchall()]

    def create_user(self, name, email, password, role='user', privacy_accept=False, marketing_consent=False, analytics_consent=False):
        """Erstelle einen neuen Benutzer"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO users (name, email, password, role, privacy_accept, marketing_consent, analytics_consent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, email, password, role, privacy_accept, marketing_consent, analytics_consent))
        self.connection.commit()
        return cursor.lastrowid

    def update_user(self, user_id, **kwargs):
        """Aktualisiere einen Benutzer"""
        cursor = self.connection.cursor()
        allowed_fields = {'name', 'email', 'password', 'role', 'privacy_accept', 'marketing_consent', 'analytics_consent'}
        fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not fields:
            return False
        
        set_clause = ', '.join(f'{k} = ?' for k in fields.keys())
        values = list(fields.values()) + [user_id]
        
        cursor.execute(f'UPDATE users SET {set_clause} WHERE id = ?', values)
        self.connection.commit()
        return cursor.rowcount > 0

    # ===== PRODUCT OPERATIONS =====
    
    def get_all_products(self):
        """Hole alle Produkte"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM products')
        products = []
        for row in cursor.fetchall():
            product = dict(row)
            # Parse JSON images
            if product.get('images'):
                try:
                    product['images'] = json.loads(product['images'])
                except:
                    product['images'] = []
            else:
                product['images'] = []
            products.append(product)
        return products

    def get_product_by_id(self, product_id):
        """Hole ein Produkt nach ID"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        row = cursor.fetchone()
        if not row:
            return None
        
        product = dict(row)
        if product.get('images'):
            try:
                product['images'] = json.loads(product['images'])
            except:
                product['images'] = []
        else:
            product['images'] = []
        return product

    def create_product(self, name, category, price, description='', images=None, stock=0):
        """Erstelle ein neues Produkt"""
        cursor = self.connection.cursor()
        images_json = json.dumps(images or [], ensure_ascii=False)
        cursor.execute('''
            INSERT INTO products (name, category, price, description, images, stock)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, category, price, description, images_json, stock))
        self.connection.commit()
        return cursor.lastrowid

    def update_product(self, product_id, **kwargs):
        """Aktualisiere ein Produkt"""
        cursor = self.connection.cursor()
        allowed_fields = {'name', 'category', 'price', 'description', 'images', 'stock'}
        fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not fields:
            return False
        
        # Konvertiere images zu JSON
        if 'images' in fields and isinstance(fields['images'], list):
            fields['images'] = json.dumps(fields['images'], ensure_ascii=False)
        
        set_clause = ', '.join(f'{k} = ?' for k in fields.keys())
        values = list(fields.values()) + [product_id]
        
        cursor.execute(f'UPDATE products SET {set_clause} WHERE id = ?', values)
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_product(self, product_id):
        """Lösche ein Produkt"""
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    # ===== ORDER OPERATIONS =====
    
    def create_order(self, user_id, items, total, customer, payment_provider=None, provider_id=None):
        """Erstelle eine neue Bestellung"""
        cursor = self.connection.cursor()
        items_json = json.dumps(items, ensure_ascii=False)
        customer_json = json.dumps(customer, ensure_ascii=False)
        
        cursor.execute('''
            INSERT INTO orders (user_id, items, total, customer, payment_provider, provider_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, items_json, total, customer_json, payment_provider, provider_id))
        self.connection.commit()
        return cursor.lastrowid

    def get_orders_by_user(self, user_id):
        """Hole alle Bestellungen eines Benutzers"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        orders = []
        for row in cursor.fetchall():
            order = dict(row)
            order['items'] = json.loads(order['items']) if order.get('items') else []
            order['customer'] = json.loads(order['customer']) if order.get('customer') else {}
            orders.append(order)
        return orders

    def get_all_orders(self):
        """Hole alle Bestellungen"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM orders ORDER BY created_at DESC')
        orders = []
        for row in cursor.fetchall():
            order = dict(row)
            order['items'] = json.loads(order['items']) if order.get('items') else []
            order['customer'] = json.loads(order['customer']) if order.get('customer') else {}
            orders.append(order)
        return orders

    def update_order_status(self, order_id, status):
        """Aktualisiere den Status einer Bestellung"""
        cursor = self.connection.cursor()
        cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        self.connection.commit()
        return cursor.rowcount > 0

    def delete_order(self, order_id):
        """Lösche eine Bestellung"""
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    # ===== CONSENT OPERATIONS =====
    
    def save_consent(self, user_id, consent_type, value):
        """Speichere eine Einwilligung"""
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO user_consents (user_id, consent_type, value)
            VALUES (?, ?, ?)
        ''', (user_id, consent_type, value))
        self.connection.commit()
        return cursor.lastrowid

    def get_user_consents(self, user_id):
        """Hole alle Einwilligungen eines Benutzers"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM user_consents WHERE user_id = ?', (user_id,))
        return [dict(row) for row in cursor.fetchall()]

    # ===== AUDIT LOG OPERATIONS =====
    
    def log_audit(self, event_type, user_id=None, user_email=None, action='', resource_type=None, resource_id=None, details=None, ip_address=None, status='success'):
        """Schreibe einen Audit-Log-Eintrag"""
        cursor = self.connection.cursor()
        details_json = json.dumps(details, ensure_ascii=False) if details else None
        
        cursor.execute('''
            INSERT INTO audit_log (event_type, user_id, user_email, action, resource_type, resource_id, details, ip_address, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (event_type, user_id, user_email, action, resource_type, resource_id, details_json, ip_address, status))
        self.connection.commit()

    def get_audit_logs(self, user_id=None, limit=1000):
        """Hole Audit-Logs"""
        cursor = self.connection.cursor()
        if user_id:
            cursor.execute('SELECT * FROM audit_log WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?', (user_id, limit))
        else:
            cursor.execute('SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?', (limit,))
        
        logs = []
        for row in cursor.fetchall():
            log = dict(row)
            if log.get('details'):
                try:
                    log['details'] = json.loads(log['details'])
                except:
                    log['details'] = {}
            logs.append(log)
        return logs

    # ===== DSGVO OPERATIONS =====
    
    def export_user_data(self, user_id):
        """Exportiere alle Daten eines Benutzers (Art. 15 DSGVO)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        return {
            'profile': user,
            'orders': self.get_orders_by_user(user_id),
            'consents': self.get_user_consents(user_id),
            'audit_logs': self.get_audit_logs(user_id)
        }

    def delete_user(self, user_id):
        """Lösche einen Benutzer und alle seine Daten (Art. 17 DSGVO)"""
        cursor = self.connection.cursor()
        
        try:
            # Lösche Bestellungen
            cursor.execute('DELETE FROM orders WHERE user_id = ?', (user_id,))
            # Lösche Einwilligungen
            cursor.execute('DELETE FROM user_consents WHERE user_id = ?', (user_id,))
            # Lösche Audit-Logs
            cursor.execute('DELETE FROM audit_log WHERE user_id = ?', (user_id,))
            # Lösche Benutzer
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            
            self.connection.commit()
            return True
        except Exception as e:
            self.connection.rollback()
            print(f"Fehler beim Löschen des Benutzers: {e}")
            return False