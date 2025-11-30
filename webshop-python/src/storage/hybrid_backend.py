"""
Hybrid Backend: Versucht SQLite zu nutzen, fällt zu CSV zurück bei Fehlern.
Ermöglicht sanfte Migration von CSV zu SQLite.
"""

class HybridBackend:
    def __init__(self, csv_backend, sqlite_backend=None):
        """
        Initialisiere das Hybrid-Backend
        
        Args:
            csv_backend: CSVBackend-Instanz als Fallback
            sqlite_backend: SQLiteBackend-Instanz (optional)
        """
        self.csv = csv_backend
        self.sqlite = sqlite_backend
        self.fallback_log = []

    def set_sqlite_backend(self, sqlite_backend):
        """Setze das SQLite-Backend später"""
        self.sqlite = sqlite_backend

    def _log_fallback(self, method_name, error):
        """Protokolliere Fallback-Ereignisse"""
        self.fallback_log.append({
            'method': method_name,
            'error': str(error),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })

    def _try_sqlite(self, method_name, *args, **kwargs):
        """Versuche die Operation in SQLite auszuführen"""
        if not self.sqlite:
            return None
        
        try:
            method = getattr(self.sqlite, method_name)
            return method(*args, **kwargs)
        except Exception as e:
            self._log_fallback(method_name, e)
            return None

    # ===== USER OPERATIONS =====
    
    def get_user_by_id(self, user_id):
        """Hole einen Benutzer - versuche SQLite, falle zu CSV zurück"""
        result = self._try_sqlite('get_user_by_id', user_id)
        if result:
            return result
        
        users = self.csv.get_all_users()
        for user in users:
            if str(user.get('id')) == str(user_id):
                return user
        return None

    def get_user_by_email(self, email):
        """Hole einen Benutzer nach E-Mail"""
        result = self._try_sqlite('get_user_by_email', email)
        if result:
            return result
        
        users = self.csv.get_all_users()
        for user in users:
            if user.get('email') == email:
                return user
        return None

    def get_all_users(self):
        """Hole alle Benutzer"""
        result = self._try_sqlite('get_all_users')
        if result:
            return result
        return self.csv.get_all_users()

    def create_user(self, name, email, password, role='user', privacy_accept=False, marketing_consent=False, analytics_consent=False):
        """Erstelle einen neuen Benutzer in beiden Backends"""
        # Versuche SQLite
        if self.sqlite:
            try:
                user_id = self.sqlite.create_user(name, email, password, role, privacy_accept, marketing_consent, analytics_consent)
                # Speichere auch in CSV als Backup
                users = self.csv.get_all_users()
                new_user = {
                    'id': str(user_id),
                    'name': name,
                    'email': email,
                    'password': password,
                    'role': role,
                    'privacy_accept': privacy_accept,
                    'marketing_consent': marketing_consent,
                    'analytics_consent': analytics_consent,
                    'created_at': __import__('datetime').datetime.now().isoformat()
                }
                users.append(new_user)
                self.csv.write_csv('users.csv', users)
                return user_id
            except Exception as e:
                self._log_fallback('create_user', e)
        
        # Fallback zu CSV
        users = self.csv.get_all_users()
        user_id = str(max([int(u.get('id', 0)) for u in users] + [0]) + 1)
        new_user = {
            'id': user_id,
            'name': name,
            'email': email,
            'password': password,
            'role': role,
            'privacy_accept': privacy_accept,
            'marketing_consent': marketing_consent,
            'analytics_consent': analytics_consent,
            'created_at': __import__('datetime').datetime.now().isoformat()
        }
        users.append(new_user)
        self.csv.write_csv('users.csv', users)
        return int(user_id)

    def update_user(self, user_id, **kwargs):
        """Aktualisiere einen Benutzer in beiden Backends"""
        # Versuche SQLite
        if self.sqlite:
            try:
                self.sqlite.update_user(user_id, **kwargs)
            except Exception as e:
                self._log_fallback('update_user', e)
        
        # Aktualisiere auch CSV
        users = self.csv.get_all_users()
        for user in users:
            if str(user.get('id')) == str(user_id):
                user.update(kwargs)
                break
        self.csv.write_csv('users.csv', users)

    # ===== PRODUCT OPERATIONS =====
    
    def get_all_products(self):
        """Hole alle Produkte"""
        result = self._try_sqlite('get_all_products')
        if result:
            return result
        return self.csv.get_all_products()

    def get_product_by_id(self, product_id):
        """Hole ein Produkt nach ID"""
        result = self._try_sqlite('get_product_by_id', product_id)
        if result:
            return result
        
        products = self.csv.get_all_products()
        for product in products:
            if str(product.get('id')) == str(product_id):
                return product
        return None

    def create_product(self, name, category, price, description='', images=None, stock=0):
        """Erstelle ein neues Produkt in beiden Backends"""
        if self.sqlite:
            try:
                product_id = self.sqlite.create_product(name, category, price, description, images, stock)
            except Exception as e:
                self._log_fallback('create_product', e)
                product_id = None
        else:
            product_id = None
        
        # Speichere auch in CSV
        products = self.csv.get_all_products()
        if product_id is None:
            product_id = max([int(p.get('id', 0)) for p in products] + [0]) + 1
        
        import json
        new_product = {
            'id': str(product_id),
            'name': name,
            'category': category,
            'price': str(price),
            'description': description,
            'images': json.dumps(images or []),
            'stock': str(stock)
        }
        products.append(new_product)
        self.csv.write_csv('products.csv', products)
        return product_id

    def update_product(self, product_id, **kwargs):
        """Aktualisiere ein Produkt in beiden Backends"""
        if self.sqlite:
            try:
                self.sqlite.update_product(product_id, **kwargs)
            except Exception as e:
                self._log_fallback('update_product', e)
        
        # Aktualisiere auch CSV
        products = self.csv.get_all_products()
        for product in products:
            if str(product.get('id')) == str(product_id):
                product.update(kwargs)
                break
        self.csv.write_csv('products.csv', products)

    def delete_product(self, product_id):
        """Lösche ein Produkt aus beiden Backends"""
        if self.sqlite:
            try:
                self.sqlite.delete_product(product_id)
            except Exception as e:
                self._log_fallback('delete_product', e)
        
        # Lösche auch aus CSV
        products = self.csv.get_all_products()
        products = [p for p in products if str(p.get('id')) != str(product_id)]
        self.csv.write_csv('products.csv', products)

    # ===== ORDER OPERATIONS =====
    
    def create_order(self, user_id, items, total, customer, payment_provider=None, provider_id=None):
        """Erstelle eine neue Bestellung in beiden Backends"""
        if self.sqlite:
            try:
                order_id = self.sqlite.create_order(user_id, items, total, customer, payment_provider, provider_id)
            except Exception as e:
                self._log_fallback('create_order', e)
                order_id = None
        else:
            order_id = None
        
        # Speichere auch in CSV
        import json
        orders = self.csv.read_csv('orders.csv')
        if order_id is None:
            order_id = max([int(o.get('id', 0)) for o in orders] + [0]) + 1
        
        new_order = {
            'id': str(order_id),
            'user_id': str(user_id),
            'items': json.dumps(items),
            'total': str(total),
            'customer': json.dumps(customer),
            'status': 'pending',
            'payment_provider': payment_provider or '',
            'provider_id': provider_id or '',
            'created_at': __import__('datetime').datetime.now().isoformat()
        }
        orders.append(new_order)
        self.csv.write_csv('orders.csv', orders)
        return order_id

    def get_orders_by_user(self, user_id):
        """Hole alle Bestellungen eines Benutzers"""
        result = self._try_sqlite('get_orders_by_user', user_id)
        if result:
            return result
        
        orders = self.csv.read_csv('orders.csv')
        import json
        user_orders = []
        for order in orders:
            if str(order.get('user_id')) == str(user_id):
                order['items'] = json.loads(order.get('items', '[]')) if order.get('items') else []
                order['customer'] = json.loads(order.get('customer', '{}')) if order.get('customer') else {}
                user_orders.append(order)
        return user_orders

    def get_all_orders(self):
        """Hole alle Bestellungen"""
        result = self._try_sqlite('get_all_orders')
        if result:
            return result
        
        orders = self.csv.read_csv('orders.csv')
        import json
        for order in orders:
            order['items'] = json.loads(order.get('items', '[]')) if order.get('items') else []
            order['customer'] = json.loads(order.get('customer', '{}')) if order.get('customer') else {}
        return orders

    def update_order_status(self, order_id, status):
        """Aktualisiere den Status einer Bestellung"""
        if self.sqlite:
            try:
                self.sqlite.update_order_status(order_id, status)
            except Exception as e:
                self._log_fallback('update_order_status', e)
        
        # Aktualisiere auch CSV
        orders = self.csv.read_csv('orders.csv')
        for order in orders:
            if str(order.get('id')) == str(order_id):
                order['status'] = status
                break
        self.csv.write_csv('orders.csv', orders)

    def delete_order(self, order_id):
        """Lösche eine Bestellung aus beiden Systemen"""
        # Versuche SQLite zu löschen
        if self.sqlite:
            try:
                self.sqlite.delete_order(order_id)
            except Exception as e:
                self._log_fallback('delete_order', e)
        
        # Lösche auch aus CSV
        try:
            orders = self.csv.read_csv('orders.csv')
            orders = [o for o in orders if str(o.get('id')) != str(order_id)]
            self.csv.write_csv('orders.csv', orders)
        except Exception as e:
            self._log_fallback('delete_order_csv', e)
        
        return True

    # ===== CONSENT OPERATIONS =====
    
    def save_consent(self, user_id, consent_type, value):
        """Speichere eine Einwilligung"""
        if self.sqlite:
            try:
                return self.sqlite.save_consent(user_id, consent_type, value)
            except Exception as e:
                self._log_fallback('save_consent', e)
        
        # Fallback zu CSV
        consents = self.csv.read_csv('user_consents.csv')
        consent_id = max([int(c.get('id', 0)) for c in consents] + [0]) + 1
        import datetime
        new_consent = {
            'id': str(consent_id),
            'user_id': str(user_id),
            'consent_type': consent_type,
            'value': str(value),
            'timestamp': datetime.datetime.now().isoformat()
        }
        consents.append(new_consent)
        self.csv.write_csv('user_consents.csv', consents)
        return consent_id

    def get_user_consents(self, user_id):
        """Hole alle Einwilligungen eines Benutzers"""
        result = self._try_sqlite('get_user_consents', user_id)
        if result:
            return result
        
        consents = self.csv.read_csv('user_consents.csv')
        return [c for c in consents if str(c.get('user_id')) == str(user_id)]

    # ===== AUDIT LOG OPERATIONS =====
    
    def log_audit(self, event_type, user_id=None, user_email=None, action='', resource_type=None, resource_id=None, details=None, ip_address=None, status='success'):
        """Schreibe einen Audit-Log-Eintrag"""
        if self.sqlite:
            try:
                self.sqlite.log_audit(event_type, user_id, user_email, action, resource_type, resource_id, details, ip_address, status)
            except Exception as e:
                self._log_fallback('log_audit', e)
        
        # Speichere auch in CSV
        from utils.logging_service import audit_logger
        audit_logger.log(event_type, user_id, user_email, action, resource_type, resource_id, details, ip_address, status)

    def get_audit_logs(self, user_id=None, limit=1000):
        """Hole Audit-Logs"""
        result = self._try_sqlite('get_audit_logs', user_id, limit)
        if result:
            return result
        
        # Fallback zu CSV
        from utils.logging_service import audit_logger
        if user_id:
            return audit_logger.get_user_logs(user_id, limit)
        else:
            return audit_logger.get_all_logs(limit)

    # ===== DSGVO OPERATIONS =====
    
    def export_user_data(self, user_id):
        """Exportiere alle Daten eines Benutzers (Art. 15 DSGVO)"""
        result = self._try_sqlite('export_user_data', user_id)
        if result:
            return result
        
        # Fallback: Manuell zusammenstellen
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
        success = True
        
        if self.sqlite:
            try:
                self.sqlite.delete_user(user_id)
            except Exception as e:
                self._log_fallback('delete_user', e)
                success = False
        
        # Lösche auch aus CSV
        users = self.csv.get_all_users()
        users = [u for u in users if str(u.get('id')) != str(user_id)]
        self.csv.write_csv('users.csv', users)
        
        orders = self.csv.read_csv('orders.csv')
        orders = [o for o in orders if str(o.get('user_id')) != str(user_id)]
        self.csv.write_csv('orders.csv', orders)
        
        consents = self.csv.read_csv('user_consents.csv')
        consents = [c for c in consents if str(c.get('user_id')) != str(user_id)]
        self.csv.write_csv('user_consents.csv', consents)
        
        return success

    # ===== UTILITY =====
    
    def get_fallback_log(self):
        """Hole das Fallback-Logbuch"""
        return self.fallback_log

    def clear_fallback_log(self):
        """Leere das Fallback-Logbuch"""
        self.fallback_log = []

    # ===== CSV-KOMPATIBLE METHODEN =====
    
    def get_product(self, product_id):
        """Hole ein Produkt nach ID (CSV-kompatibel)"""
        return self.get_product_by_id(product_id)

    def save_user(self, user):
        """Speichere einen Benutzer (CSV-kompatibel)"""
        # Wenn Benutzer bereits eine ID hat, aktualisiere ihn
        if 'id' in user and user.get('id'):
            self.update_user(user['id'], **{k: v for k, v in user.items() if k != 'id'})
            return user['id']
        else:
            # Neuen Benutzer erstellen
            return self.create_user(
                user.get('name', ''),
                user.get('email', ''),
                user.get('password', ''),
                user.get('role', 'user'),
                user.get('privacy_accept', False),
                user.get('marketing_consent', False),
                user.get('analytics_consent', False)
            )

    def save_product(self, product):
        """Speichere ein Produkt (CSV-kompatibel)"""
        if 'id' in product and product.get('id'):
            self.update_product(product['id'], **{k: v for k, v in product.items() if k != 'id'})
            return product['id']
        else:
            return self.create_product(
                product.get('name', ''),
                product.get('category', ''),
                float(product.get('price', 0)),
                product.get('description', ''),
                product.get('images', []),
                int(product.get('stock', 0))
            )

    def save_order(self, order):
        """Speichere eine Bestellung (CSV-kompatibel)"""
        import json
        if 'id' in order and order.get('id'):
            self.update_order_status(order['id'], order.get('status', 'pending'))
            return order['id']
        else:
            return self.create_order(
                int(order.get('user_id', 0)),
                json.loads(order.get('items', '[]')) if isinstance(order.get('items'), str) else order.get('items', []),
                float(order.get('total', 0)),
                json.loads(order.get('customer', '{}')) if isinstance(order.get('customer'), str) else order.get('customer', {}),
                order.get('payment_provider'),
                order.get('provider_id')
            )

    def update_order(self, order_id, updates):
        """Aktualisiere eine Bestellung (CSV-kompatibel)"""
        if 'status' in updates:
            self.update_order_status(order_id, updates['status'])
            return True
        return False

    def add_product_image(self, product_id, image_filename):
        """Füge ein Bild zu einem Produkt hinzu"""
        product = self.get_product_by_id(product_id)
        if not product:
            return False
        
        images = product.get('images', [])
        if image_filename not in images:
            images.append(image_filename)
            self.update_product(product_id, images=images)
        return True

    def remove_product_image(self, product_id, image_filename):
        """Entferne ein Bild von einem Produkt"""
        product = self.get_product_by_id(product_id)
        if not product:
            return False
        
        images = product.get('images', [])
        if image_filename in images:
            images.remove(image_filename)
            self.update_product(product_id, images=images)
        return True

    def read_csv(self, filename):
        """Lese CSV-Datei direkt (für Fallback)"""
        return self.csv.read_csv(filename)

    def write_csv(self, filename, data, fieldnames=None):
        """Schreibe CSV-Datei direkt (für Fallback)"""
        self.csv.write_csv(filename, data, fieldnames)
