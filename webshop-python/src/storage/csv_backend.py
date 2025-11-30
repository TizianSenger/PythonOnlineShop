import csv
import json
from pathlib import Path

class CSVBackend:
    def __init__(self, csv_folder):
        self.csv_folder = Path(csv_folder)
        self.csv_folder.mkdir(parents=True, exist_ok=True)
        self._ensure_csv_files()
        self._migrate_old_format()

    def _migrate_old_format(self):
        users_file = self.csv_folder / 'users.csv'
        if users_file.exists():
            users = self.read_csv('users.csv')
            if users and 'username' in users[0]:
                for user in users:
                    if 'username' in user:
                        user['name'] = user.pop('username')
                self.write_csv('users.csv', users, fieldnames=['id', 'name', 'email', 'password', 'role', 'privacy_accept', 'marketing_consent', 'analytics_consent', 'created_at'])

    def _ensure_csv_files(self):
        files = {
            'users.csv': ['id', 'name', 'email', 'password', 'role', 'privacy_accept', 'marketing_consent', 'analytics_consent', 'created_at'],
            'products.csv': ['id', 'name', 'category', 'price', 'description', 'images', 'stock'],
            'orders.csv': ['id', 'user_id', 'product_id', 'quantity', 'total'],
            'user_consents.csv': ['id', 'user_id', 'consent_type', 'value', 'timestamp']
        }
        for filename, headers in files.items():
            filepath = self.csv_folder / filename
            if not filepath.exists():
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()

    def read_csv(self, filename):
        filepath = self.csv_folder / filename
        if not filepath.exists():
            return []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader) if reader else []

    def write_csv(self, filename, data, fieldnames=None):
        filepath = self.csv_folder / filename
        defaults = {
            'users.csv': ['id', 'name', 'email', 'password', 'role'],
            'products.csv': ['id', 'name', 'category', 'price', 'description', 'images', 'stock'],
            'orders.csv': ['id', 'user_id', 'product_id', 'quantity', 'total']
        }
        if fieldnames is None:
            if data:
                fieldnames = list(data[0].keys())
            else:
                fieldnames = defaults.get(filename, [])
        # Normalize values: ensure lists are JSON-serialized and None -> ''
        rows_to_write = []
        for row in data:
            normalized = {}
            for k in fieldnames:
                v = row.get(k, '')
                if isinstance(v, list):
                    try:
                        normalized[k] = json.dumps(v, ensure_ascii=False)
                    except Exception:
                        normalized[k] = json.dumps([str(x) for x in v], ensure_ascii=False)
                elif v is None:
                    normalized[k] = ''
                else:
                    # Ensure it's a string for CSV (numbers kept as-is but cast to str)
                    normalized[k] = v
            rows_to_write.append(normalized)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            if rows_to_write:
                writer.writerows(rows_to_write)

    def get_all_users(self):
        return self.read_csv('users.csv')

    def get_all_products(self):
        products = self.read_csv('products.csv')
        for p in products:
            # Parse JSON images list
            if 'images' in p and p['images']:
                try:
                    p['images'] = json.loads(p['images'])
                except Exception:
                    # fallback: if it's Python list string repr or invalid JSON, try eval safely
                    try:
                        # avoid using plain eval on untrusted data; try to fix common patterns
                        s = p['images'].strip()
                        if s.startswith('[') and s.endswith(']'):
                            # replace single quotes with double quotes for JSON
                            s2 = s.replace("'", '"')
                            p['images'] = json.loads(s2)
                        else:
                            p['images'] = []
                    except Exception:
                        p['images'] = []
            else:
                p['images'] = []
        return products

    def get_product(self, product_id):
        products = self.get_all_products()
        return next((p for p in products if p.get('id') == product_id), None)

    def save_user(self, user):
        users = self.get_all_users()
        user_id = str(max([int(u.get('id', 0)) for u in users] + [0]) + 1)
        user['id'] = user_id
        users.append(user)
        self.write_csv('users.csv', users, fieldnames=['id', 'name', 'email', 'password', 'role'])
        return user_id

    def save_product(self, product):
        products = self.get_all_products()
        product_id = str(max([int(p.get('id', 0)) for p in products] + [0]) + 1)
        product['id'] = product_id

        # Ensure images is a list -> will be serialized in write_csv
        if 'images' not in product or not product['images']:
            product['images'] = []
        elif isinstance(product['images'], str):
            # try to decode if someone passed JSON string
            try:
                product['images'] = json.loads(product['images'])
            except:
                # fallback to empty or list with single string
                product['images'] = [product['images']]

        if 'stock' not in product:
            product['stock'] = '0'

        products.append(product)
        # write_csv will serialize lists
        self.write_csv('products.csv', products, fieldnames=['id', 'name', 'category', 'price', 'description', 'images', 'stock'])
        return product_id

    def update_product(self, product_id, updates):
        products = self.get_all_products()
        updated = False
        for p in products:
            if p.get('id') == product_id:
                for k, v in updates.items():
                    if k == 'images':
                        # ensure images stored as list here; write_csv will serialize
                        if isinstance(v, str):
                            try:
                                p[k] = json.loads(v)
                            except:
                                p[k] = [v]
                        else:
                            p[k] = v
                    else:
                        p[k] = v
                updated = True
                break
        if updated:
            self.write_csv('products.csv', products, fieldnames=['id', 'name', 'category', 'price', 'description', 'images', 'stock'])
        return updated

    def add_product_image(self, product_id, image_filename):
        """Add an image to a product's images list (max 20)"""
        products = self.get_all_products()
        for p in products:
            if p.get('id') == product_id:
                images = p.get('images', [])
                if not isinstance(images, list):
                    images = []
                if len(images) < 20 and image_filename not in images:
                    images.append(image_filename)
                    p['images'] = images
                    self.write_csv('products.csv', products, fieldnames=['id', 'name', 'category', 'price', 'description', 'images', 'stock'])
                    return True
        return False

    def remove_product_image(self, product_id, image_filename):
        """Remove an image from a product's images list"""
        products = self.get_all_products()
        for p in products:
            if p.get('id') == product_id:
                images = p.get('images', [])
                if not isinstance(images, list):
                    images = []
                if image_filename in images:
                    images.remove(image_filename)
                    p['images'] = images
                    self.write_csv('products.csv', products, fieldnames=['id', 'name', 'category', 'price', 'description', 'images', 'stock'])
                    return True
        return False

    def delete_product(self, product_id):
        products = self.get_all_products()
        products = [p for p in products if p.get('id') != product_id]
        self.write_csv('products.csv', products, fieldnames=['id', 'name', 'category', 'price', 'description', 'images', 'stock'])

    def get_all_orders(self):
        return self.read_csv('orders.csv')

    def save_order(self, order):
        orders = self.get_all_orders()
        # Safely get order_id, handling empty strings
        existing_ids = []
        for o in orders:
            id_val = o.get('id', '0')
            if id_val and str(id_val).strip():
                try:
                    existing_ids.append(int(id_val))
                except (ValueError, TypeError):
                    pass
        order_id = str(max(existing_ids + [0]) + 1)
        order['id'] = order_id
        orders.append(order)
        # Determine fieldnames from order keys if it's a new checkout order (has items, customer, etc.)
        if 'items' in order or 'customer' in order:
            fieldnames = ['id', 'user_id', 'items', 'total', 'customer', 'status', 'payment_provider', 'provider_id', 'created_at']
        else:
            # Legacy format for simple orders
            fieldnames = ['id', 'user_id', 'product_id', 'quantity', 'total']
        self.write_csv('orders.csv', orders, fieldnames=fieldnames)
        return order_id

    def update_order(self, order_id, updates):
        """Update order fields (e.g., status)"""
        orders = self.get_all_orders()
        updated = False
        for o in orders:
            if o.get('id') == order_id:
                for k, v in updates.items():
                    o[k] = v
                updated = True
                break
        if updated:
            # Determine fieldnames
            if orders and ('items' in orders[0] or 'customer' in orders[0]):
                fieldnames = ['id', 'user_id', 'items', 'total', 'customer', 'status', 'payment_provider', 'provider_id', 'created_at']
            else:
                fieldnames = ['id', 'user_id', 'product_id', 'quantity', 'total']
            self.write_csv('orders.csv', orders, fieldnames=fieldnames)

    # ===== DSGVO-Compliance Methoden =====
    
    def save_consent(self, user_id, consent_type, value):
        """Speichere Benutzer-Einwilligung (DSGVO-Compliance)"""
        from datetime import datetime
        consent = {
            'id': str(max([int(c.get('id', 0)) for c in self.read_csv('user_consents.csv')] + [0]) + 1),
            'user_id': user_id,
            'consent_type': consent_type,
            'value': str(value),
            'timestamp': datetime.utcnow().isoformat()
        }
        consents = self.read_csv('user_consents.csv')
        consents.append(consent)
        self.write_csv('user_consents.csv', consents, 
                      fieldnames=['id', 'user_id', 'consent_type', 'value', 'timestamp'])
        return consent['id']
    
    def get_user_consents(self, user_id):
        """Hole alle Einwilligungen eines Benutzers"""
        consents = self.read_csv('user_consents.csv')
        return [c for c in consents if c.get('user_id') == user_id]
    
    def export_user_data(self, user_id, include_orders=True):
        """Exportiere alle Daten eines Benutzers (Art. 15 + 20 DSGVO)"""
        users = self.get_all_users()
        user = next((u for u in users if u.get('id') == user_id), None)
        
        if not user:
            return None
        
        # Entferne Passwort aus Export
        user_copy = user.copy()
        user_copy.pop('password', None)
        
        export_data = {
            'profile': user_copy,
            'consents': self.get_user_consents(user_id),
            'orders': []
        }
        
        if include_orders:
            orders = self.get_all_orders()
            user_orders = [o for o in orders if o.get('user_id') == user_id]
            export_data['orders'] = user_orders
        
        return export_data
    
    def delete_user(self, user_id):
        """Lösche einen Benutzer und seine Daten (Art. 17 DSGVO - Right to be forgotten)"""
        users = self.get_all_users()
        users = [u for u in users if u.get('id') != user_id]
        self.write_csv('users.csv', users, 
                      fieldnames=['id', 'name', 'email', 'password', 'role', 'privacy_accept', 'marketing_consent', 'analytics_consent', 'created_at'])
        
        # Lösche auch Einwilligungen
        consents = self.read_csv('user_consents.csv')
        consents = [c for c in consents if c.get('user_id') != user_id]
        self.write_csv('user_consents.csv', consents, 
                      fieldnames=['id', 'user_id', 'consent_type', 'value', 'timestamp'])
        
        return True
    
    def update_user_consents(self, user_id, privacy_accept=None, marketing_consent=None, analytics_consent=None):
        """Update Benutzer-Einwilligung nach Registrierung"""
        users = self.get_all_users()
        from datetime import datetime
        
        for user in users:
            if user.get('id') == user_id:
                if privacy_accept is not None:
                    user['privacy_accept'] = str(privacy_accept)
                if marketing_consent is not None:
                    user['marketing_consent'] = str(marketing_consent)
                if analytics_consent is not None:
                    user['analytics_consent'] = str(analytics_consent)
                if 'created_at' not in user:
                    user['created_at'] = datetime.utcnow().isoformat()
                break
        
        self.write_csv('users.csv', users, 
                      fieldnames=['id', 'name', 'email', 'password', 'role', 'privacy_accept', 'marketing_consent', 'analytics_consent', 'created_at'])
        return True
        return updated