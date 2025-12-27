# Kapitel 6: Technologieentscheidungen

## 6.1 Programmiersprache: Python

### 6.1.1 Begründung der Wahl

**Warum Python?**

| Kriterium | Bewertung | Begründung |
|-----------|-----------|-----------|
| **Entwicklungsgeschwindigkeit** | ⭐⭐⭐⭐⭐ | Einfache Syntax, große Bibliotheken, schnelle Prototypisierung |
| **Sicherheit** | ⭐⭐⭐⭐ | OWASP-Standards gut etabliert, Libraries wie Werkzeug |
| **Performance** | ⭐⭐⭐ | Gut genug für E-Commerce (mit Caching) |
| **Community** | ⭐⭐⭐⭐⭐ | Große Python-Community, Flask/Django sehr populär |
| **Datenschutz** | ⭐⭐⭐⭐⭐ | Libraries für DSGVO-Compliance vorhanden |
| **Wartbarkeit** | ⭐⭐⭐⭐⭐ | Lesbar, gut dokumentierbar |
| **Skalierbarkeit** | ⭐⭐⭐⭐ | Mit gunicorn/nginx gut skalierbar |

**Alternativen und Bewertung:**

```
PHP (Laravel/Symfony)
├─ Vorteil: Traditionell für Web
├─ Nachteil: Sicherheit, Typsystem schwach
└─ Fazit: Nicht gewählt, weniger Enterprise-ready

Java (Spring Boot)
├─ Vorteil: Sehr skalierbar, Enterprise-Standard
├─ Nachteil: Zu komplex für MVP, höherer Overhead
└─ Fazit: Nicht gewählt, Overkill für MVP

Node.js (Express)
├─ Vorteil: Full-Stack JavaScript, async native
├─ Nachteil: Weniger typsicher (ohne TypeScript)
└─ Fazit: Gute Alternative, aber Python überzeugt mehr

Python (Flask)
├─ Vorteil: ✅ Einfach, schnell, sicher, gut dokumentiert
├─ Nachteil: Etwas langsamer (aber ausreichend)
└─ Fazit: ✅ GEWÄHLT - beste Balance für MVP
```

**Praktischer Kontext (Airbus):**
Bei Airbus Defence and Space nutzen wir Python für:
- Backend-Services (Flask, Django)
- Data Processing und Analytics
- DevOps/Infrastructure (Ansible, Terraform)
- Testing & Automation

Python ist etabliert und wird Enterprise-weit unterstützt.

---

## 6.2 Framework: Flask

### 6.2.1 Warum Flask statt Django?

| Aspekt | Flask | Django |
|--------|-------|--------|
| **Größe/Komplexität** | Klein, "Micro" | Groß, "Full-Stack" |
| **Setup-Zeit** | 10 Minuten | 30 Minuten |
| **ORM** | SQLAlchemy (extra) | Django ORM (inkl.) |
| **Auth** | Extensions | Eingebaut |
| **Admin Panel** | Nicht mitgeliefert | Automatisch generiert |
| **Lernkurve** | Flach | Steiler |
| **Für MVP** | ✅ Ideal | ⚠️ Zu mächtig |

**Entscheidung:**
- **Flask gewählt** für MVP, da schnell, flexibel, "Just What You Need"
- Django wäre für Enterprise-Application besser, aber hier overengineered

### 6.2.2 Flask-Ökosystem

```
┌─────────────────────────────────────┐
│         Flask Application           │
├─────────────────────────────────────┤
│                                     │
│  Flask-SQLAlchemy   → ORM/Database │
│  Flask-Login        → Authentication│
│  Flask-WTF          → Forms/CSRF    │
│  Flask-Cors         → Cross-Origin  │
│  python-dotenv      → Config Mgmt   │
│  Werkzeug           → Security      │
│  Jinja2             → Templates     │
│                                     │
└─────────────────────────────────────┘
```

**Wichtige Extensions:**

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
csrf = CSRFProtect(app)
```

---

## 6.3 Datenbank: SQLite vs. Alternativen

### 6.3.1 Entscheidungsmatrix

| Kriterium | SQLite | MySQL | PostgreSQL |
|-----------|--------|-------|------------|
| **Setup** | 0 Minuten | 10 Minuten | 10 Minuten |
| **Wartung** | Keine | Kompliziert | Komplex |
| **Skalierbarkeit** | Begrenzt | Gut | Sehr gut |
| **Concurrent Users** | <100 | 1000+ | 10000+ |
| **Für MVP** | ✅ Perfekt | Overkill | Overkill |
| **Preis** | Kostenlos | Kostenlos | Kostenlos |

### 6.3.2 SQLite für MVP - Begründung

**SQLite ist ideal für Entwicklung & MVP, weil:**

1. **Zero-Setup**: Datei-basiert, keine Server-Installation
2. **Einfaches Deployment**: DB ist einfach eine `.db`-Datei
3. **Für <1000 Daily Active Users**: Vollständig ausreichend
4. **Entwicklungs-freundlich**: Schnelles Iterieren
5. **Produktions-ready**: SQLite läuft produktiv bei vielen Unternehmen

**Wann zu PostgreSQL migrieren?**

```
Daily Active Users (DAU):
< 100 DAU      → SQLite ✅
100 - 1000 DAU → SQLite noch OK, aber PostgreSQL erwägen
1000+ DAU      → PostgreSQL/MySQL notwendig
```

### 6.3.3 Migrations & Datenbank-Evolution

```bash
# Neue Spalte hinzufügen
flask db init
flask db migrate -m "Add product_rating column"
flask db upgrade

# Migration wird automatisch in migrations/versions/ gespeichert
```

**Migration-Beispiel:**
```python
# migrations/versions/001_add_product_rating.py
def upgrade():
    op.add_column('products', 
        sa.Column('rating', sa.Float, default=0))

def downgrade():
    op.drop_column('products', 'rating')
```

---

## 6.4 Frontend-Stack: HTML5, CSS3, Vanilla JavaScript

### 6.4.1 Warum keine Heavy-Framework?

| Framework | Größe | Komplexität | Für MVP |
|-----------|-------|-------------|---------|
| **React** | 40 KB | Hoch (Virtual DOM, JSX) | ❌ Overkill |
| **Vue.js** | 35 KB | Mittel (SFC) | ⚠️ Zu viel |
| **Alpine.js** | 15 KB | Niedrig (Attribute) | ✅ Gut |
| **Vanilla JS** | 0 KB | Niedrig (Plain JS) | ✅ Ideal für MVP |

**Entscheidung:**
- **Vanilla JavaScript** mit **Alpine.js** für kleine Interaktionen
- Kein Build-Step nötig, performant, wartbar

### 6.4.2 CSS-Architektur: Custom Properties + BEM

```css
/* Custom Properties für Theme-Management */
:root {
  --primary: #6366f1;
  --secondary: #ec4899;
  --bg-light: #ffffff;
  --bg-dark: #0f172a;
  --text-dark: #1e293b;
  --text-light: #64748b;
}

/* Dark Mode */
[data-theme="dark"] {
  --bg-light: #0f172a;
  --bg-dark: #1e293b;
  --text-dark: #f1f5f9;
  --text-light: #cbd5e1;
}

/* BEM: Block-Element-Modifier */
.card {
  background: var(--bg-light);
  padding: 1rem;
}

.card__title {
  font-size: 1.5rem;
  color: var(--text-dark);
}

.card__title--featured {
  color: var(--primary);
  font-weight: bold;
}
```

### 6.4.3 JavaScript - Moderne Praktiken

```javascript
// ✅ Moderne ES6+ Syntax
const addToCart = async (productId, quantity) => {
  try {
    const response = await fetch('/add-to-cart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: productId, quantity })
    });
    
    if (!response.ok) throw new Error('Failed');
    
    const data = await response.json();
    showNotification(`${quantity} Artikel hinzugefügt!`, 'success');
    updateCartUI(data.cart_count);
  } catch (error) {
    showNotification('Fehler beim Hinzufügen', 'error');
  }
};

// ✅ DOM-Manipulation mit event delegation
document.addEventListener('click', (e) => {
  if (e.target.matches('[data-add-to-cart]')) {
    const productId = e.target.dataset.productId;
    addToCart(productId, 1);
  }
});
```

---

## 6.5 Server & Deployment

### 6.5.1 Entwicklung vs. Produktion

**Entwicklung:**
```bash
flask run  # Development Server (Werkzeug, Auto-Reload)
# http://localhost:5000
```

**Produktion:**
```bash
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
# WSGI-Server, produktionsreif
# Mit nginx als Reverse Proxy
```

### 6.5.2 Deployment-Stack

```
Internet
    │
    ▼
┌─────────────┐
│   Nginx     │ ← Reverse Proxy, Static Files, SSL/TLS
└────────┬────┘
         │
    ┌────▼────┐
    │ Gunicorn│ ← 4-8 Worker Processes
    ├─────────┤
    │ Flask   │
    │  App    │
    └────┬────┘
         │
    ┌────▼────────────┐
    │ SQLite Database │
    └─────────────────┘
```

**Optionen für Hosting:**

| Anbieter | Preis | Einsatz |
|----------|-------|---------|
| **VPS (Linode, DigitalOcean)** | €5-10/mo | Self-managed, vollständig |
| **Heroku** | €7-50/mo | Easy deploy, eingeschränkt |
| **PythonAnywhere** | €5-28/mo | Python-spezialisiert |
| **AWS Lambda** | Pay-per-use | Serverless, kompliziert |

**Empfehlung:** DigitalOcean App Platform oder VPS (günstiger und flexibler)

---

## 6.6 Entwicklungswerkzeuge

### 6.6.1 IDE & Debugging

```bash
# VSCode Extensions
Code --install-extension ms-python.python
Code --install-extension ms-python.vscode-pylance

# Debugging mit Flask
FLASK_DEBUG=1 FLASK_APP=app.py flask run
# Debugger läuft auf port 5678
```

### 6.6.2 Version Control & CI/CD

```yaml
# .github/workflows/ci.yml - GitHub Actions
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: pytest tests/
      - run: flake8 src/  # Linting
```

### 6.6.3 Code Quality Tools

```bash
# Type Checking
mypy src/  # Static type checking

# Linting
flake8 src/  # PEP 8 compliance
pylint src/  # Deeper code analysis

# Formatting
black src/  # Auto-formatter (opinionated)

# Testing
pytest tests/  # Unit & Integration Tests
coverage report  # Code coverage
```

---

## Zusammenfassung Kapitel 6

✅ **Programmiersprache: Python**
- Schnelle Entwicklung, sichere Syntax
- Enterprise-ready (auch bei Airbus verwendet)
- Große Community & Ökosystem

✅ **Framework: Flask**
- Leicht und flexibel für MVP
- Mit SQLAlchemy ORM und sicheren Extensions
- Zero-Boilerplate

✅ **Datenbank: SQLite**
- Perfekt für MVP und <1000 DAU
- Zero-Wartung, Zero-Setup
- Einfache Migration auf PostgreSQL später

✅ **Frontend: Vanilla JS + CSS3**
- Keine Dependencies, performant
- Modern (ES6+, Fetch API, async/await)
- BEM-basierte CSS-Architektur

✅ **Deployment:**
- Gunicorn + Nginx für Produktion
- VPS oder PaaS möglich
- CI/CD mit GitHub Actions

---

*Nächstes Kapitel: Architektur & Software-Design*
