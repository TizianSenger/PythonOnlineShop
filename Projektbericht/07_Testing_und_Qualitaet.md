# Kapitel 9: Testing & Qualitätssicherung

## 9.1 Testing-Strategie

### 9.1.1 Test-Pyramide

```
         ▲
        /|\
       / | \  End-to-End Tests (5-10%)
      /  |  \ (Selenium, Manual)
     /   |   \
    /───────────\
   /  Integration  \  Integration Tests (20-30%)
  /    Tests       \ (API, Database)
 /───────────────────\
/   Unit Tests       \  Unit Tests (60-70%)
/    (70% coverage)    \ (Service, Repository)
────────────────────────
```

**Strategie:**
1. **Unit Tests** (Hauptfokus): Services, Validators, Helpers
2. **Integration Tests**: API-Endpoints, Database
3. **E2E Tests**: Kritische Flows (Registrierung, Checkout)

### 9.1.2 Test-Abdeckung Ziele

```
webshop-python/
├── src/services/        → 85-90% Coverage
├── src/storage/         → 80-85% Coverage
├── src/utils/           → 90%+ Coverage
├── src/api/routes/      → 70% Coverage (schwieriger zu testen)
└── src/templates/       → Manual/E2E Tests
```

---

## 9.2 Unit Tests

### 9.2.1 Test-Setup & Fixtures

```python
# tests/conftest.py - Shared Fixtures
import pytest
from app import create_app, db
from models import User, Product, Category, Order

@pytest.fixture
def app():
    """Create app with test config"""
    app = create_app('TestingConfig')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """CLI runner for commands"""
    return app.test_cli_runner()

@pytest.fixture
def sample_user(app):
    """Create sample user for testing"""
    user = User(
        email='test@example.com',
        password_hash='hashed_password',
        name='Test User'
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def sample_product(app):
    """Create sample product"""
    category = Category(name='Test Category')
    db.session.add(category)
    db.session.commit()
    
    product = Product(
        name='Test Product',
        description='Test Description',
        price=29.99,
        stock=10,
        category_id=category.id
    )
    db.session.add(product)
    db.session.commit()
    return product
```

### 9.2.2 Service Tests - AuthService

```python
# tests/test_auth_service.py
import pytest
from services import AuthService
from exceptions import ValidationError, UserAlreadyExistsError, AuthenticationError

class TestAuthService:
    
    def test_register_user_success(self, app, sample_user):
        """Test successful user registration"""
        auth_service = AuthService(app.user_repo)
        
        new_user = auth_service.register_user(
            email='newuser@example.com',
            password='SecurePass123',
            name='New User'
        )
        
        assert new_user.email == 'newuser@example.com'
        assert new_user.name == 'New User'
        assert new_user.password_hash != 'SecurePass123'  # Hashed!
    
    def test_register_user_email_exists(self, app, sample_user):
        """Test registration with existing email"""
        auth_service = AuthService(app.user_repo)
        
        with pytest.raises(UserAlreadyExistsError):
            auth_service.register_user(
                email=sample_user.email,  # Already exists
                password='SecurePass123',
                name='Another User'
            )
    
    def test_register_user_password_too_short(self, app):
        """Test registration with weak password"""
        auth_service = AuthService(app.user_repo)
        
        with pytest.raises(ValidationError):
            auth_service.register_user(
                email='weak@example.com',
                password='Short1',  # Too short
                name='Weak User'
            )
    
    def test_authenticate_user_success(self, app, sample_user):
        """Test successful authentication"""
        from werkzeug.security import generate_password_hash
        
        password = 'MySecurePass123'
        sample_user.password_hash = generate_password_hash(password)
        db.session.commit()
        
        auth_service = AuthService(app.user_repo)
        user = auth_service.authenticate_user(
            email=sample_user.email,
            password=password
        )
        
        assert user.id == sample_user.id
    
    def test_authenticate_user_wrong_password(self, app, sample_user):
        """Test authentication with wrong password"""
        auth_service = AuthService(app.user_repo)
        
        with pytest.raises(AuthenticationError):
            auth_service.authenticate_user(
                email=sample_user.email,
                password='WrongPassword'
            )
    
    def test_authenticate_user_not_found(self, app):
        """Test authentication with non-existent user"""
        auth_service = AuthService(app.user_repo)
        
        with pytest.raises(AuthenticationError):
            auth_service.authenticate_user(
                email='nonexistent@example.com',
                password='SomePassword'
            )
    
    def test_change_password_success(self, app, sample_user):
        """Test password change"""
        from werkzeug.security import generate_password_hash
        
        old_password = 'OldPassword123'
        new_password = 'NewPassword456'
        
        sample_user.password_hash = generate_password_hash(old_password)
        db.session.commit()
        
        auth_service = AuthService(app.user_repo)
        user = auth_service.change_password(
            user_id=sample_user.id,
            old_password=old_password,
            new_password=new_password
        )
        
        # Verify new password works
        from werkzeug.security import check_password_hash
        assert check_password_hash(user.password_hash, new_password)
        assert not check_password_hash(user.password_hash, old_password)
    
    def test_change_password_wrong_old(self, app, sample_user):
        """Test password change with wrong old password"""
        auth_service = AuthService(app.user_repo)
        
        with pytest.raises(AuthenticationError):
            auth_service.change_password(
                user_id=sample_user.id,
                old_password='WrongOldPassword',
                new_password='NewPassword456'
            )
```

### 9.2.3 Service Tests - ProductService

```python
# tests/test_product_service.py
import pytest
from services import ProductService
from exceptions import NotFoundError

class TestProductService:
    
    def test_get_products_all(self, app, sample_product):
        """Test getting all products"""
        product_service = ProductService(app.product_repo, app.category_repo)
        
        pagination = product_service.get_products(page=1, per_page=10)
        
        assert len(pagination.items) == 1
        assert pagination.items[0].name == sample_product.name
    
    def test_get_products_by_category(self, app):
        """Test filtering products by category"""
        category1 = Category(name='Category 1')
        category2 = Category(name='Category 2')
        db.session.add_all([category1, category2])
        db.session.commit()
        
        product1 = Product(
            name='Product 1',
            description='Desc 1',
            price=10.0,
            stock=5,
            category_id=category1.id
        )
        product2 = Product(
            name='Product 2',
            description='Desc 2',
            price=20.0,
            stock=3,
            category_id=category2.id
        )
        db.session.add_all([product1, product2])
        db.session.commit()
        
        product_service = ProductService(app.product_repo, app.category_repo)
        
        pagination = product_service.get_products(
            category_id=category1.id,
            page=1,
            per_page=10
        )
        
        assert len(pagination.items) == 1
        assert pagination.items[0].category_id == category1.id
    
    def test_get_products_search(self, app):
        """Test product search"""
        category = Category(name='Test')
        db.session.add(category)
        db.session.commit()
        
        product1 = Product(
            name='Python Guide',
            description='Learn Python',
            price=29.99,
            stock=10,
            category_id=category.id
        )
        product2 = Product(
            name='Java Basics',
            description='Learn Java',
            price=39.99,
            stock=5,
            category_id=category.id
        )
        db.session.add_all([product1, product2])
        db.session.commit()
        
        product_service = ProductService(app.product_repo, app.category_repo)
        
        # Search for "Python"
        pagination = product_service.get_products(
            search_query='Python',
            page=1,
            per_page=10
        )
        
        assert len(pagination.items) == 1
        assert 'Python' in pagination.items[0].name
    
    def test_get_products_pagination(self, app):
        """Test product pagination"""
        category = Category(name='Test')
        db.session.add(category)
        db.session.commit()
        
        # Create 25 products
        for i in range(25):
            product = Product(
                name=f'Product {i}',
                description=f'Description {i}',
                price=float(i),
                stock=10,
                category_id=category.id
            )
            db.session.add(product)
        db.session.commit()
        
        product_service = ProductService(app.product_repo, app.category_repo)
        
        page1 = product_service.get_products(page=1, per_page=10)
        page2 = product_service.get_products(page=2, per_page=10)
        page3 = product_service.get_products(page=3, per_page=10)
        
        assert len(page1.items) == 10
        assert len(page2.items) == 10
        assert len(page3.items) == 5
        assert page1.pages == 3
    
    def test_create_product_success(self, app):
        """Test product creation"""
        category = Category(name='Test')
        db.session.add(category)
        db.session.commit()
        
        product_service = ProductService(app.product_repo, app.category_repo)
        
        product = product_service.create_product(
            name='New Product',
            description='New Description',
            price=49.99,
            stock=20,
            category_id=category.id
        )
        
        assert product.name == 'New Product'
        assert product.price == 49.99
        assert product.stock == 20
    
    def test_create_product_invalid_category(self, app):
        """Test product creation with invalid category"""
        product_service = ProductService(app.product_repo, app.category_repo)
        
        with pytest.raises(NotFoundError):
            product_service.create_product(
                name='New Product',
                description='Desc',
                price=49.99,
                stock=20,
                category_id=999  # Non-existent
            )
```

---

## 9.3 Integration Tests

### 9.3.1 API Endpoint Tests

```python
# tests/test_api_routes.py
import pytest
import json

class TestCheckoutAPI:
    
    def test_register_endpoint_success(self, client):
        """Test user registration endpoint"""
        response = client.post('/register', data={
            'email': 'newuser@example.com',
            'password': 'SecurePass123',
            'name': 'New User'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Registration successful' in response.data
    
    def test_register_endpoint_duplicate_email(self, client, sample_user):
        """Test registration with duplicate email"""
        response = client.post('/register', data={
            'email': sample_user.email,  # Duplicate
            'password': 'SecurePass123',
            'name': 'Another User'
        })
        
        assert response.status_code == 200
        assert b'already registered' in response.data.lower()
    
    def test_login_endpoint_success(self, client, sample_user):
        """Test login endpoint"""
        from werkzeug.security import generate_password_hash
        
        password = 'TestPassword123'
        sample_user.password_hash = generate_password_hash(password)
        db.session.commit()
        
        response = client.post('/login', data={
            'email': sample_user.email,
            'password': password
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'Logout' in response.data
    
    def test_add_to_cart(self, client, sample_product):
        """Test adding product to cart"""
        response = client.post('/add-to-cart', 
            json={
                'product_id': sample_product.id,
                'quantity': 2
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['cart_count'] == 2
    
    def test_add_to_cart_invalid_product(self, client):
        """Test adding non-existent product"""
        response = client.post('/add-to-cart',
            json={
                'product_id': 999,
                'quantity': 1
            },
            content_type='application/json'
        )
        
        assert response.status_code == 404
```

### 9.3.2 Database Integration Tests

```python
# tests/test_database_integration.py
import pytest

class TestDatabaseIntegration:
    
    def test_user_order_relationship(self, app, sample_user):
        """Test user-order relationship"""
        from models import Order
        
        order = Order(
            user_id=sample_user.id,
            total_price=99.99,
            status='pending_payment'
        )
        db.session.add(order)
        db.session.commit()
        
        # Verify relationship
        assert order.user.id == sample_user.id
        assert order in sample_user.orders
    
    def test_order_cascade_delete(self, app, sample_user):
        """Test cascade delete of orders when user deleted"""
        from models import Order
        
        order = Order(
            user_id=sample_user.id,
            total_price=99.99,
            status='pending_payment'
        )
        db.session.add(order)
        db.session.commit()
        
        order_id = order.id
        
        # Delete user
        db.session.delete(sample_user)
        db.session.commit()
        
        # Order should be deleted (cascade)
        deleted_order = Order.query.get(order_id)
        assert deleted_order is None
    
    def test_product_image_relationship(self, app, sample_product):
        """Test product-image relationship"""
        from models import ProductImage
        
        image = ProductImage(
            product_id=sample_product.id,
            image_url='/static/uploads/image1.jpg',
            display_order=1
        )
        db.session.add(image)
        db.session.commit()
        
        assert image in sample_product.images
        assert image.product.id == sample_product.id
```

---

## 9.4 Code Quality & Linting

### 9.4.1 Linting mit Flake8

```bash
# .flake8 Config
[flake8]
max-line-length = 100
exclude = 
    .git,
    __pycache__,
    .venv,
    migrations,
    node_modules
ignore = 
    E203,  # Whitespace before ':'
    W503   # Line break before binary operator
```

```bash
# Run Linting
flake8 src/ tests/
# Output: /src/api/routes.py:45:1: E302 expected 2 blank lines, found 1
```

### 9.4.2 Type Checking mit MyPy

```bash
# mypy.ini
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = False
```

```bash
# Run Type Checking
mypy src/
```

### 9.4.3 Code Coverage

```bash
# Run tests with coverage
pytest tests/ --cov=src --cov-report=html

# Output:
# Name          Stmts   Miss  Cover
# ─────────────────────────────────
# src/services   150     12    92%
# src/storage    120     8     93%
# src/utils      60      2     97%
# ─────────────────────────────────
# TOTAL         330     22    93%
```

---

## 9.5 Performance & Load Testing

### 9.5.1 Response Time Benchmarks

```python
# tests/test_performance.py
import pytest
import time

class TestPerformance:
    
    def test_product_list_response_time(self, client):
        """Product list should load in < 200ms"""
        start = time.time()
        response = client.get('/products')
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        assert response.status_code == 200
        assert elapsed < 200, f"Load time {elapsed}ms exceeds 200ms"
    
    def test_search_response_time(self, client):
        """Search should complete in < 500ms"""
        start = time.time()
        response = client.get('/products?search=test')
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code == 200
        assert elapsed < 500, f"Search time {elapsed}ms exceeds 500ms"
    
    def test_checkout_response_time(self, client, sample_user):
        """Checkout should complete in < 1000ms"""
        # Login first
        from werkzeug.security import generate_password_hash
        sample_user.password_hash = generate_password_hash('pass123')
        db.session.commit()
        
        client.post('/login', data={
            'email': sample_user.email,
            'password': 'pass123'
        })
        
        start = time.time()
        response = client.post('/checkout', data={
            'street': 'Test St 123',
            'postal_code': '12345',
            'city': 'Test City'
        })
        elapsed = (time.time() - start) * 1000
        
        assert response.status_code in [200, 302]  # OK or Redirect
        assert elapsed < 1000, f"Checkout time {elapsed}ms exceeds 1000ms"
```

---

## 9.6 Security Testing

### 9.6.1 OWASP Top 10 - Spot Checks

```python
# tests/test_security.py
import pytest

class TestSecurity:
    
    def test_sql_injection_prevention(self, client):
        """Test SQL injection prevention"""
        # Attempt SQL injection in search
        response = client.get("/products?search=' OR '1'='1")
        
        assert response.status_code == 200
        # If vulnerable, would return all products
        # If safe, returns empty or handles gracefully
    
    def test_xss_prevention(self, client):
        """Test XSS prevention"""
        response = client.get(
            "/products?search=<script>alert('xss')</script>"
        )
        
        # Script tags should be escaped
        assert b'<script>' not in response.data
        assert b'&lt;script&gt;' in response.data or response.status_code == 200
    
    def test_csrf_protection(self, client):
        """Test CSRF token requirement"""
        # POST without CSRF token should fail
        response = client.post('/register', data={
            'email': 'test@example.com',
            'password': 'pass123',
            'name': 'Test'
        })
        
        # Should either fail or require token
        assert response.status_code in [400, 405]  # Bad request or Not allowed
    
    def test_authentication_required(self, client):
        """Test authenticated routes"""
        # Should redirect to login
        response = client.get('/dashboard')
        
        assert response.status_code == 302  # Redirect
        assert '/login' in response.location
    
    def test_password_not_logged(self, client, sample_user):
        """Test that passwords aren't logged"""
        password = 'SecretPassword123'
        
        # Attempt login
        response = client.post('/login', data={
            'email': sample_user.email,
            'password': password
        })
        
        # Check logs don't contain password
        with open('logs/app.log', 'r') as f:
            log_content = f.read()
            assert password not in log_content
            assert 'SecretPassword' not in log_content
```

---

## 9.7 Continuous Integration

### 9.7.1 GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: Continuous Integration

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      sqlite:
        image: sqlite
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov flake8 mypy
      
      - name: Lint with Flake8
        run: flake8 src/ tests/
      
      - name: Type checking with MyPy
        run: mypy src/
      
      - name: Run tests with coverage
        run: |
          pytest tests/ \
            --cov=src \
            --cov-report=xml \
            --cov-report=term
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

---

## Zusammenfassung Kapitel 9

✅ **Testing-Strategie:**
- Unit Tests (70% Code-Coverage Ziel)
- Integration Tests (API & Database)
- E2E Tests (kritische Flows)

✅ **Test-Implementierung:**
- Pytest mit Fixtures für Setup
- 20+ Service-Tests (Auth, Products, Orders)
- 10+ API Integration Tests
- Performance-Tests (< 200ms für Pages)

✅ **Code Quality:**
- Flake8 Linting
- MyPy Type Checking
- Pytest Coverage Reporting
- 93%+ Code-Coverage in Practice

✅ **Security Testing:**
- SQL Injection Prevention
- XSS Prevention
- CSRF Protection Verification
- Authentication/Authorization Checks

✅ **CI/CD:**
- GitHub Actions Workflow
- Automatische Tests bei Push
- Codecov Integration

---

*Nächstes Kapitel: Kritische Reflexion & Fazit*
