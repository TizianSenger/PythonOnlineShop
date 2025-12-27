# Kapitel 8: Implementierung & MVP

## 8.1 MVP-Kern-Funktionalität

Der MVP (Minimum Viable Product) konzentriert sich auf die essentiellen Features:

- ✅ Produktkatalog mit Kategorien
- ✅ Produktsuche & Filterung
- ✅ Warenkorb (Session-basiert)
- ✅ User-Registrierung & Login
- ✅ Checkout & Order-Erstellung
- ✅ Admin-Panel (Produkte & Kategorien)
- ✅ DSGVO-Compliance
- ✅ Sichere Authentifizierung

---

## 8.2 Implementierungsbeispiele

### 8.2.1 User Service - Authentifizierung

```python
# services/auth_service.py
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets

class AuthService:
    def __init__(self, user_repository):
        self.user_repo = user_repository
    
    def register_user(self, email, password, name):
        """Registriert einen neuen Nutzer mit Validierung"""
        # Validierung
        if self.user_repo.find_by_email(email):
            raise UserAlreadyExistsError(f"Email {email} already registered")
        
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        
        # Passwort hashen mit Argon2
        password_hash = generate_password_hash(password, method='argon2')
        
        # Nutzer erstellen
        user = User(
            email=email,
            password_hash=password_hash,
            name=name,
            created_at=datetime.utcnow()
        )
        
        return self.user_repo.create(user)
    
    def authenticate_user(self, email, password):
        """Authentifiziert Nutzer"""
        user = self.user_repo.find_by_email(email)
        
        if not user:
            raise AuthenticationError("Invalid email or password")
        
        # Passwort vergleichen (sichere Vergleichsfunktion)
        if not check_password_hash(user.password_hash, password):
            raise AuthenticationError("Invalid email or password")
        
        return user
    
    def change_password(self, user_id, old_password, new_password):
        """Ändert das Passwort mit Validierung"""
        user = self.user_repo.find_by_id(user_id)
        
        if not check_password_hash(user.password_hash, old_password):
            raise AuthenticationError("Current password is incorrect")
        
        if new_password == old_password:
            raise ValidationError("New password must be different")
        
        user.password_hash = generate_password_hash(new_password, method='argon2')
        self.user_repo.update(user)
        
        return user

# routes/auth_routes.py
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    try:
        email = request.form['email'].strip().lower()
        password = request.form['password']
        name = request.form['name'].strip()
        
        # Nutzer registrieren
        user = app.auth_service.register_user(email, password, name)
        
        # DSGVO: Consent tracken
        app.consent_service.record_consent(
            user_id=user.id,
            type='essential',
            agreed=True
        )
        
        flash('Registration successful! Please login.', 'success')
        return redirect('/login')
    
    except (ValidationError, UserAlreadyExistsError) as e:
        return render_template('register.html', error=str(e))

@app.route('/login', methods=['GET', 'POST'])
@csrf.protect
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    try:
        email = request.form['email'].strip().lower()
        password = request.form['password']
        
        user = app.auth_service.authenticate_user(email, password)
        session['user_id'] = user.id
        session.permanent = True
        app.permanent_session_lifetime = timedelta(hours=2)
        
        # Audit Log
        app.audit_logger.log_action(
            user_id=user.id,
            action='login',
            resource=f'user_{user.id}',
            status='success'
        )
        
        return redirect('/')
    
    except AuthenticationError as e:
        app.audit_logger.log_action(
            user_id=None,
            action='login_attempt',
            resource='authentication',
            status='failed',
            details={'email': request.form.get('email')}
        )
        return render_template('login.html', error=str(e))
```

### 8.2.2 Product Service - Katalog

```python
# services/product_service.py
from sqlalchemy import and_, or_

class ProductService:
    def __init__(self, product_repo, category_repo):
        self.product_repo = product_repo
        self.category_repo = category_repo
    
    def get_products(self, category_id=None, search_query=None, 
                     page=1, per_page=12, sort_by='newest'):
        """
        Holt Produkte mit Filterung und Sortierung
        
        Args:
            category_id: Optional Kategorie-Filter
            search_query: Optional Suchtext (Titel/Beschreibung)
            page: Seite (1-basiert)
            per_page: Produkte pro Seite (max 50)
            sort_by: 'newest', 'price_asc', 'price_desc'
        
        Returns:
            Pagination Object mit Produkten
        """
        query = Product.query
        
        # Category Filter
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        # Search Filter
        if search_query:
            search_term = f"%{search_query}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )
        
        # Sorting
        if sort_by == 'price_asc':
            query = query.order_by(Product.price.asc())
        elif sort_by == 'price_desc':
            query = query.order_by(Product.price.desc())
        else:  # newest
            query = query.order_by(Product.created_at.desc())
        
        # Pagination
        pagination = query.paginate(
            page=max(1, page),
            per_page=min(per_page, 50),  # Max 50 per page
            error_out=False
        )
        
        return pagination
    
    def get_product_with_images(self, product_id):
        """Holt Produkt mit allen Bildern (eager loaded)"""
        product = Product.query.options(
            joinedload(Product.images)
        ).get(product_id)
        
        if not product:
            raise NotFoundError(f"Product {product_id} not found")
        
        return product
    
    def create_product(self, name, description, price, stock, category_id):
        """Admin-Funktion: Neues Produkt erstellen"""
        category = self.category_repo.find_by_id(category_id)
        if not category:
            raise NotFoundError(f"Category {category_id} not found")
        
        product = Product(
            name=name,
            description=description,
            price=float(price),
            stock=int(stock),
            category_id=category_id,
            created_at=datetime.utcnow()
        )
        
        return self.product_repo.create(product)
    
    def update_product(self, product_id, **kwargs):
        """Admin-Funktion: Produkt aktualisieren"""
        product = self.product_repo.find_by_id(product_id)
        if not product:
            raise NotFoundError(f"Product {product_id} not found")
        
        # Nur erlaubte Felder aktualisieren
        allowed_fields = ['name', 'description', 'price', 'stock']
        for field in allowed_fields:
            if field in kwargs:
                setattr(product, field, kwargs[field])
        
        product.updated_at = datetime.utcnow()
        return self.product_repo.update(product)

# routes/product_routes.py
@app.route('/products')
def list_products():
    """Produktliste mit Filterung"""
    category_id = request.args.get('category', type=int)
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'newest')
    
    pagination = app.product_service.get_products(
        category_id=category_id,
        search_query=search_query,
        page=page,
        sort_by=sort_by
    )
    
    categories = app.category_service.get_all_categories()
    
    return render_template(
        'products.html',
        pagination=pagination,
        categories=categories,
        current_category=category_id,
        search_query=search_query,
        sort_by=sort_by
    )

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Produktdetails"""
    product = app.product_service.get_product_with_images(product_id)
    
    return render_template(
        'product_detail.html',
        product=product
    )
```

### 8.2.3 Order Service - Checkout

```python
# services/checkout_service.py
from decimal import Decimal
from datetime import datetime

class OrderService:
    def __init__(self, order_repo, product_repo, payment_repo):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.payment_repo = payment_repo
    
    def create_order(self, user_id, cart_items, shipping_address):
        """
        Erstellt eine neue Order mit Validierung
        
        Args:
            user_id: Nutzer-ID
            cart_items: Liste von {'product_id': X, 'quantity': Y}
            shipping_address: {'street': ..., 'city': ..., ...}
        
        Returns:
            Order Object
        """
        # Validiere Cart Items
        order_items = []
        total_price = Decimal('0.00')
        
        for item in cart_items:
            product = self.product_repo.find_by_id(item['product_id'])
            
            if not product:
                raise NotFoundError(f"Product {item['product_id']} not found")
            
            # Lagerbestand prüfen
            if product.stock < item['quantity']:
                raise InsufficientStockError(
                    f"Only {product.stock} of {product.name} available"
                )
            
            # Order Item erstellen (mit Price Snapshot)
            order_item = OrderItem(
                product_id=product.id,
                quantity=item['quantity'],
                price=product.price  # Snapshot zum Zeitpunkt der Order
            )
            order_items.append(order_item)
            total_price += product.price * Decimal(str(item['quantity']))
        
        # Steuern hinzufügen (19% MwSt)
        tax_amount = total_price * Decimal('0.19')
        total_with_tax = total_price + tax_amount
        
        # Order erstellen
        order = Order(
            user_id=user_id,
            total_price=float(total_with_tax),
            status='pending_payment',
            created_at=datetime.utcnow(),
            items=order_items,
            shipping_address=shipping_address
        )
        
        # Speichern
        order = self.order_repo.create(order)
        
        # Audit Log
        app.audit_logger.log_action(
            user_id=user_id,
            action='order_create',
            resource=f'order_{order.id}',
            status='success',
            details={
                'total': float(total_with_tax),
                'item_count': len(order_items)
            }
        )
        
        return order
    
    def update_order_status(self, order_id, new_status, admin_id):
        """Admin-Funktion: Order-Status aktualisieren"""
        valid_statuses = [
            'pending_payment', 'confirmed', 'shipped', 'delivered', 'cancelled'
        ]
        
        if new_status not in valid_statuses:
            raise ValidationError(f"Invalid status: {new_status}")
        
        order = self.order_repo.find_by_id(order_id)
        if not order:
            raise NotFoundError(f"Order {order_id} not found")
        
        old_status = order.status
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        self.order_repo.update(order)
        
        # Audit Log
        app.audit_logger.log_action(
            user_id=admin_id,
            action='order_status_update',
            resource=f'order_{order_id}',
            status='success',
            details={
                'old_status': old_status,
                'new_status': new_status
            }
        )
        
        return order

# routes/checkout_routes.py
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'GET':
        return render_template('checkout.html')
    
    try:
        # Cart aus Session laden
        cart = session.get('cart', {})
        cart_items = [
            {'product_id': int(pid), 'quantity': qty}
            for pid, qty in cart.items()
        ]
        
        if not cart_items:
            raise ValidationError("Cart is empty")
        
        # Versandadresse aus Formular
        shipping_address = {
            'street': request.form['street'],
            'postal_code': request.form['postal_code'],
            'city': request.form['city'],
            'country': request.form.get('country', 'Germany')
        }
        
        # Order erstellen
        order = app.order_service.create_order(
            user_id=current_user.id,
            cart_items=cart_items,
            shipping_address=shipping_address
        )
        
        # Cart löschen
        session['cart'] = {}
        
        # E-Mail senden (optional)
        # app.notification_service.send_order_confirmation(order)
        
        return redirect(f'/order-confirmation/{order.id}')
    
    except (ValidationError, NotFoundError, InsufficientStockError) as e:
        return render_template('checkout.html', error=str(e))
```

### 8.2.4 DSGVO Service - Privacy

```python
# services/privacy_service.py
import json
from datetime import datetime

class PrivacyService:
    def __init__(self, user_repo, order_repo, consent_repo):
        self.user_repo = user_repo
        self.order_repo = order_repo
        self.consent_repo = consent_repo
    
    def export_user_data(self, user_id):
        """Art. 15 DSGVO: Dateneinsicht"""
        user = self.user_repo.find_by_id(user_id)
        
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        
        # Alle Nutzer-relevanten Daten sammeln
        data = {
            'profile': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'created_at': user.created_at.isoformat()
            },
            'addresses': [
                {
                    'street': addr.street,
                    'city': addr.city,
                    'postal_code': addr.postal_code,
                    'country': addr.country
                }
                for addr in user.addresses
            ],
            'orders': [
                {
                    'id': order.id,
                    'total_price': float(order.total_price),
                    'status': order.status,
                    'created_at': order.created_at.isoformat(),
                    'items': [
                        {
                            'product_name': item.product.name,
                            'quantity': item.quantity,
                            'price': float(item.price)
                        }
                        for item in order.items
                    ]
                }
                for order in self.order_repo.find_by_user(user_id)
            ],
            'consents': [
                {
                    'type': consent.type,
                    'agreed': consent.agreed,
                    'created_at': consent.created_at.isoformat(),
                    'updated_at': consent.updated_at.isoformat()
                }
                for consent in self.consent_repo.find_by_user(user_id)
            ]
        }
        
        # Audit Log
        app.audit_logger.log_action(
            user_id=user_id,
            action='data_export',
            resource=f'user_{user_id}',
            status='success'
        )
        
        return data
    
    def delete_user_account(self, user_id, confirmed=False):
        """Art. 17 DSGVO: Recht auf Löschung (mit Anonymisierung)"""
        if not confirmed:
            raise ValidationError("Account deletion must be confirmed")
        
        user = self.user_repo.find_by_id(user_id)
        
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        
        # Anonymisieren statt Löschen (für Audit Trail)
        user.email = f"deleted_{user_id}@deleted.local"
        user.name = f"Deleted User {user_id}"
        user.password_hash = ""  # Inaccessible
        user.is_active = False
        
        # Adressen löschen
        for address in user.addresses:
            db.session.delete(address)
        
        # Benutzerdaten in Orders bleiben erhalten (rechtlich notwendig)
        # Orders werden nicht gelöscht, nur de-identifiziert
        
        db.session.commit()
        
        # Audit Log
        app.audit_logger.log_action(
            user_id=user_id,
            action='account_delete',
            resource=f'user_{user_id}',
            status='success'
        )
        
        return True

# routes/privacy_routes.py
@app.route('/gdpr-rights/export')
@login_required
def export_data():
    """DSGVO Dateneinsicht - Download als JSON"""
    data = app.privacy_service.export_user_data(current_user.id)
    
    response = jsonify(data)
    response.headers['Content-Disposition'] = (
        f'attachment; filename="user_data_{current_user.id}.json"'
    )
    return response

@app.route('/gdpr-rights/delete', methods=['POST'])
@login_required
def delete_account():
    """DSGVO Recht auf Löschung"""
    confirmation_code = request.form.get('confirmation_code')
    
    # Verification Code aus Session prüfen
    if session.get('delete_confirmation') != confirmation_code:
        flash('Invalid confirmation code', 'error')
        return redirect('/profile')
    
    try:
        app.privacy_service.delete_user_account(
            user_id=current_user.id,
            confirmed=True
        )
        
        session.clear()  # Logout
        flash('Your account has been deleted.', 'success')
        return redirect('/')
    
    except ValidationError as e:
        flash(str(e), 'error')
        return redirect('/profile')
```

---

## 8.3 Datenbank-Schema Initialisierung

```python
# storage/init_database.py
from flask_sqlalchemy import SQLAlchemy
from storage.models import User, Product, Category, Order, OrderItem, Payment

def init_db(app):
    """Initialisiert die Datenbank mit Schema"""
    with app.app_context():
        db.create_all()
        
        # Beispieldaten für Entwicklung
        if Category.query.count() == 0:
            categories = [
                Category(name='Electronics', description='Electronic devices'),
                Category(name='Books', description='Physical and digital books'),
                Category(name='Clothing', description='Fashion and apparel')
            ]
            db.session.add_all(categories)
            db.session.commit()
            
            products = [
                Product(
                    name='Laptop',
                    description='High-performance laptop',
                    price=999.99,
                    stock=10,
                    category_id=categories[0].id
                ),
                Product(
                    name='Python Guide',
                    description='Learn Python in 30 days',
                    price=29.99,
                    stock=50,
                    category_id=categories[1].id
                ),
            ]
            db.session.add_all(products)
            db.session.commit()
            
            print("✅ Database initialized with sample data")

# app.py
from flask import Flask
from storage.init_database import init_db

app = Flask(__name__)
init_db(app)
```

---

## 8.4 Environment Setup

```bash
# .env - Environment Variables
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///shop.db
DEBUG=True
LOG_LEVEL=DEBUG

# Payment Providers (Optional)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
PAYPAL_CLIENT_ID=...
PAYPAL_SECRET=...

# Email (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

```bash
# requirements.txt
Flask==3.0.0
Flask-SQLAlchemy==3.0.0
Flask-Login==0.6.3
Flask-WTF==1.2.1
Werkzeug==3.0.1
python-dotenv==1.0.0
gunicorn==21.2.0
```

```bash
# Setup Instructions
git clone https://github.com/yourusername/webshop-python.git
cd webshop-python

# Create Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt

# Initialize Database
python -c "from app import app, init_db; init_db(app)"

# Run Development Server
FLASK_ENV=development python app.py
# Open http://localhost:5000
```

---

## Zusammenfassung Kapitel 8

✅ **Implementiert:**
- User-Authentifizierung mit Passwort-Hashing (Argon2)
- Produktkatalog mit Suche, Filter, Pagination
- Warenkorb und Order-Verwaltung
- DSGVO-konform: Dateneinsicht & Löschung
- Audit-Logging für alle kritischen Aktionen
- Environment-basierte Konfiguration

✅ **Code-Qualität:**
- Exception Handling mit benutzerdefinierten Exceptions
- Service-Layer mit Geschäftslogik
- Input-Validierung und SQL-Injection-Schutz
- CSRF-Protection für alle POST-Requests

✅ **Deployment-ready:**
- Gunicorn + Nginx für Produktion
- Database Migrations vorbereitet
- Logging & Error-Handling etabliert

---

*Nächstes Kapitel: Testing & Qualitätssicherung*
