# Kapitel 7: Architektur & Software-Design

## 7.1 Architektur-Übersicht

### 7.1.1 Mehrschichten-Architektur (Layered Architecture)

```
┌────────────────────────────────────────────────────┐
│              Presentation Layer                     │
│  (HTML Templates, REST API, Static Assets)         │
└───────────────────┬────────────────────────────────┘
                    │ HTTP/JSON
┌───────────────────▼────────────────────────────────┐
│           Application Layer (Flask)                │
│  ├─ Routes & Controllers                          │
│  ├─ Request Handling                              │
│  └─ View Logic                                    │
└───────────────────┬────────────────────────────────┘
                    │
┌───────────────────▼────────────────────────────────┐
│            Service/Business Layer                 │
│  ├─ OrderService (Bestelllogik)                  │
│  ├─ UserService (Nutzer-Verwaltung)              │
│  ├─ ProductService (Katalog)                     │
│  ├─ PaymentService (Zahlungen)                   │
│  └─ NotificationService (E-Mail)                 │
└───────────────────┬────────────────────────────────┘
                    │
┌───────────────────▼────────────────────────────────┐
│            Data Access Layer (DAL)                │
│  ├─ UserRepository                               │
│  ├─ ProductRepository                            │
│  ├─ OrderRepository                              │
│  └─ PaymentRepository                            │
└───────────────────┬────────────────────────────────┘
                    │ SQL Queries
┌───────────────────▼────────────────────────────────┐
│           Database Layer                          │
│  ├─ SQLite Database (SQLAlchemy ORM)            │
│  └─ Schema & Migrations                          │
└────────────────────────────────────────────────────┘
```

**Vorteile:**
- **Separation of Concerns**: Jede Schicht hat klare Verantwortung
- **Testbarkeit**: Mocks und Unit-Tests einfach
- **Maintainability**: Änderungen isoliert
- **Reusability**: Services können in anderen Projekten genutzt werden

### 7.1.2 Projekt-Struktur

```
webshop-python/
│
├── src/
│   ├── app.py                    # Flask App Initialisierung
│   ├── config.py                 # Konfiguration (Dev/Prod)
│   │
│   ├── api/                      # HTTP Routes & Controllers
│   │   ├── __init__.py
│   │   ├── checkout_routes.py    # Checkout-Endpoints
│   │   ├── product_routes.py     # Produkt-Endpoints
│   │   ├── user_routes.py        # Nutzer-Endpoints
│   │   └── auth_routes.py        # Auth-Endpoints
│   │
│   ├── services/                 # Business Logic
│   │   ├── __init__.py
│   │   ├── checkout_service.py   # Order-Verwaltung
│   │   ├── user_service.py       # Nutzer-Verwaltung
│   │   ├── product_service.py    # Katalog
│   │   ├── payment_service.py    # Zahlungsabwicklung
│   │   └── auth_service.py       # Authentifizierung
│   │
│   ├── storage/                  # Data Access Layer
│   │   ├── __init__.py
│   │   ├── models.py             # SQLAlchemy Models
│   │   ├── user_repository.py    # User CRUD
│   │   ├── product_repository.py # Product CRUD
│   │   ├── order_repository.py   # Order CRUD
│   │   └── payment_repository.py # Payment CRUD
│   │
│   ├── utils/
│   │   ├── helpers.py            # Utility Functions
│   │   ├── logging_service.py    # Audit Logging
│   │   └── validators.py         # Input Validation
│   │
│   ├── templates/                # Jinja2 Templates
│   │   ├── base.html             # Base Layout
│   │   ├── index.html            # Homepage
│   │   ├── product_detail.html   # Produktdetails
│   │   ├── cart.html             # Warenkorb
│   │   ├── checkout.html         # Checkout
│   │   ├── login.html            # Login
│   │   ├── register.html         # Registrierung
│   │   ├── admin_products.html   # Admin: Produkte
│   │   └── admin_orders.html     # Admin: Orders
│   │
│   └── static/
│       ├── css/
│       │   └── style.css         # Styles
│       ├── js/
│       │   ├── cart.js           # Cart Logic
│       │   ├── checkout.js       # Checkout Logic
│       │   └── auth.js           # Auth Logic
│       └── uploads/              # Product Images
│
├── tests/
│   ├── test_user_service.py      # Unit Tests
│   ├── test_order_service.py
│   ├── test_product_service.py
│   └── test_integration.py       # Integration Tests
│
├── requirements.txt              # Python Dependencies
├── .env                          # Environment Variables
├── .env.example                  # Example Config
└── README.md                     # Documentation
```

---

## 7.2 Design Patterns & Best Practices

### 7.2.1 Repository Pattern (Data Access Abstraction)

**Problem:** Direkte Datenbankzugriffe in Services führen zu Coupling

**Lösung:** Repository Pattern als Abstraktionsschicht

```python
# ❌ Ohne Repository (BAD)
class UserService:
    def create_user(self, email, password):
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return user

# ✅ Mit Repository (GOOD)
class UserRepository:
    def create(self, email, password):
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return user

class UserService:
    def __init__(self, user_repo):
        self.user_repo = user_repo
    
    def register_user(self, email, password):
        # Business Logic
        if self.user_repo.exists(email):
            raise UserAlreadyExistsError()
        return self.user_repo.create(email, password)
```

**Vorteile:**
- Testbar: Mock UserRepository in Tests
- Austauschbar: Wechsel zu anderem ORM einfach
- Wartbar: Alle DB-Operationen an einem Ort

### 7.2.2 Service Locator (Dependency Injection)

```python
# app.py - Zentrale Initialisierung
from flask import Flask
from services import UserService, OrderService
from storage import UserRepository, OrderRepository

app = Flask(__name__)

# Dependencies registrieren
user_repo = UserRepository()
order_repo = OrderRepository()

user_service = UserService(user_repo)
order_service = OrderService(order_repo)

# In Routes verfügbar
app.user_service = user_service
app.order_service = order_service
```

```python
# routes.py - Nutzung
@app.route('/register', methods=['POST'])
def register():
    user = app.user_service.register_user(
        email=request.form['email'],
        password=request.form['password']
    )
    return redirect('/login')
```

### 7.2.3 Error Handling & Validation

```python
# utils/validators.py
class ValidationError(Exception):
    pass

class PaymentError(Exception):
    pass

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format")
    return email

def validate_password(password):
    if len(password) < 8:
        raise ValidationError("Password too short (min 8 chars)")
    if not any(c.isupper() for c in password):
        raise ValidationError("Password must contain uppercase")
    return password

# routes.py - Nutzung mit Error Handling
@app.route('/register', methods=['POST'])
def register():
    try:
        email = validate_email(request.form['email'])
        password = validate_password(request.form['password'])
        user = app.user_service.register_user(email, password)
        return redirect('/login')
    except ValidationError as e:
        return render_template('register.html', error=str(e))
    except UserAlreadyExistsError:
        return render_template('register.html', error="Email already registered")
```

### 7.2.4 Configuration Management

```python
# config.py - Environment-basierte Config
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20MB max upload

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///shop.db'
    SQLALCHEMY_ECHO = True  # SQL Logging

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# app.py
from config import DevelopmentConfig, ProductionConfig

def create_app(config_class=None):
    if config_class is None:
        env = os.getenv('FLASK_ENV', 'development')
        config_class = ProductionConfig if env == 'production' else DevelopmentConfig
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    return app
```

---

## 7.3 Security Architecture

### 7.3.1 Security Layers

```
┌─────────────────────────────────────┐
│  1. Transport Security (HTTPS/TLS)  │
├─────────────────────────────────────┤
│  2. Input Validation                │
│     (Whitelist, Type Checking)      │
├─────────────────────────────────────┤
│  3. Authentication                  │
│     (Session-basiert, Passwort-Hash)│
├─────────────────────────────────────┤
│  4. Authorization                   │
│     (Rollen-basierte Zugriffskontrolle) │
├─────────────────────────────────────┤
│  5. Output Encoding                 │
│     (HTML Escaping, JSON Encoding)  │
├─────────────────────────────────────┤
│  6. Audit Logging                   │
│     (Alle kritischen Aktionen)      │
└─────────────────────────────────────┘
```

### 7.3.2 CSRF-Schutz (Cross-Site Request Forgery)

```python
# app.py
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# templates/checkout.html
<form method="POST" action="/checkout">
    {{ csrf_token() }}
    <!-- Form fields -->
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
</form>

# JavaScript API Calls
fetch('/api/order', {
    method: 'POST',
    headers: {
        'X-CSRFToken': document.querySelector('[name=csrf_token]').value,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
});
```

### 7.3.3 XSS-Schutz (Cross-Site Scripting)

```python
# ❌ VULNERABLE
@app.route('/search')
def search():
    query = request.args.get('q')
    return f"<h1>Search results for: {query}</h1>"  # HTML Injection!

# ✅ SAFE - Template Escaping
@app.route('/search')
def search():
    query = request.args.get('q')
    return render_template('search.html', query=query)

# templates/search.html
<h1>Search results for: {{ query }}</h1>
<!-- Jinja2 escaped automatisch: query wird HTML-escaped -->
```

### 7.3.4 SQL Injection Prevention

```python
# ❌ VULNERABLE
user = User.query.filter_by(
    email = f"'{email}'"  # String Concatenation!
).first()

# ✅ SAFE - Parameterized Queries (SQLAlchemy)
user = User.query.filter_by(email=email).first()
# SQLAlchemy erstellt automatisch parameterized queries
```

---

## 7.4 Performance & Caching

### 7.4.1 Caching-Strategie

```python
# app.py
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Product Listing - 1 Stunde cachen
@app.route('/products')
@cache.cached(timeout=3600, key_prefix='products_')
def list_products():
    products = Product.query.all()
    return render_template('products.html', products=products)

# Cache invalidieren nach Änderung
@app.route('/admin/product/<id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get(id)
    product.update(request.json)
    db.session.commit()
    cache.delete('products_')  # Invalidate cache
    return jsonify(product.to_dict())
```

**Cache-Policy:**
- **Static Assets**: Browser Cache (1 Jahr)
- **HTML Pages**: 1 Stunde (oder bei Änderung invalidieren)
- **API Responses**: 5-15 Minuten
- **Database Queries**: Redis (für High-Traffic)

### 7.4.2 Database Query Optimization

```python
# ❌ N+1 Problem (SLOW)
orders = Order.query.all()
for order in orders:
    user = User.query.get(order.user_id)  # DB-Query für jeden Order!
    print(user.name)

# ✅ Eager Loading (FAST)
orders = Order.query.options(
    joinedload(Order.user)  # Laden in einer Query
).all()
for order in orders:
    print(order.user.name)  # Kein zusätzlicher DB-Hit

# ✅ Oder mit explicitum Join
orders = db.session.query(Order).join(User).filter(...).all()
```

### 7.4.3 Pagination für große Datenmengen

```python
# routes.py
@app.route('/products')
def list_products():
    page = request.args.get('page', 1, type=int)
    per_page = 12  # 12 Produkte pro Seite
    
    pagination = Product.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template(
        'products.html',
        products=pagination.items,
        total_pages=pagination.pages,
        current_page=page
    )

# templates/products.html
{% for product in products %}
    <!-- Product Card -->
{% endfor %}

<div class="pagination">
    {% if current_page > 1 %}
        <a href="?page=1">First</a>
        <a href="?page={{ current_page - 1 }}">Previous</a>
    {% endif %}
    
    <span>Page {{ current_page }} of {{ total_pages }}</span>
    
    {% if current_page < total_pages %}
        <a href="?page={{ current_page + 1 }}">Next</a>
        <a href="?page={{ total_pages }}">Last</a>
    {% endif %}
</div>
```

---

## 7.5 Monitoring & Observability

### 7.5.1 Logging-Struktur

```python
# utils/logging_service.py
import logging
import json
from datetime import datetime

class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger('audit')
        handler = logging.FileHandler('logs/audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_action(self, user_id, action, resource, status='success', details=None):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,
            'resource': resource,
            'status': status,
            'details': details or {}
        }
        self.logger.info(json.dumps(log_entry))

# Nutzung
audit_logger = AuditLogger()

@app.route('/admin/product/<id>', methods=['DELETE'])
@login_required
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    
    audit_logger.log_action(
        user_id=current_user.id,
        action='product_delete',
        resource=f'product_{id}',
        details={'product_name': product.name}
    )
    
    return jsonify({'message': 'Product deleted'})
```

### 7.5.2 Error Tracking & Monitoring (Optional)

```python
# Für Production: Sentry Integration
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    traces_sample_rate=0.1,  # 10% der Requests tracen
    environment=os.getenv('FLASK_ENV', 'development')
)

# Errors werden automatisch an Sentry gesendet
@app.route('/checkout', methods=['POST'])
def checkout():
    try:
        order = order_service.create_order(...)
    except PaymentError as e:
        sentry_sdk.capture_exception(e)  # Explizit loggen
        return render_template('error.html', message=str(e))
```

---

## Zusammenfassung Kapitel 7

✅ **Architektur:**
- Mehrschichten-Architektur (Presentation, Application, Service, DAL, Database)
- Klare Separation of Concerns
- Testbar und wartbar

✅ **Design Patterns:**
- Repository Pattern für DAL
- Dependency Injection für Loose Coupling
- Service Locator für zentrale Dependency-Verwaltung
- Error Handling mit Custom Exceptions

✅ **Sicherheit:**
- 6 Security Layers (Transport, Validation, Auth, Authz, Encoding, Audit)
- CSRF & XSS-Schutz
- SQL Injection Prevention

✅ **Performance:**
- Caching-Strategie (Browser, App, DB)
- Query Optimization (Eager Loading)
- Pagination für große Datenmengen

✅ **Observability:**
- Strukturiertes Audit-Logging
- Sentry für Error-Tracking (optional)

---

*Nächstes Kapitel: Implementierung & MVP*
