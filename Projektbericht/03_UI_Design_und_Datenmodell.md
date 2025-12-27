# Kapitel 5: UI-Design & Datenmodell

## 5.1 UI-Design & Mockups

### 5.1.1 Design-Prinzipien

Der Shop folgt modernen UX-Prinzipien:

| Prinzip | Umsetzung |
|---------|-----------|
| **Mobile-First** | Responsive Design, Breakpoints bei 480px, 768px, 1024px |
| **Barrierefreiheit** | WCAG 2.1 AA: Kontraste, Alt-Texte, Keyboard-Navigation |
| **Performance** | Lazy-Loading für Bilder, CSS/JS Minification |
| **Dark-Mode** | CSS-Custom-Properties, localStorage für Präferenz |
| **Konsistenz** | Design-System mit Button, Card, Input Komponenten |

### 5.1.2 Seitenlayouts - Skizzen

#### **Startseite (Homepage)**
```
┌─────────────────────────────────────────┐
│  🛍️ WEBSHOP  [🌙 Theme] [🛒 Cart(3)]   │  Header
├─────────────────────────────────────────┤
│                                          │
│  ╔════════════════════════════════════╗ │
│  ║  Willkommen! Entdecke unsere Top   ║ │  Hero Section
│  ║  Produkte                          ║ │
│  ║  [Jetzt shoppen]                   ║ │
│  ╚════════════════════════════════════╝ │
│                                          │
│  Kategorien:                             │
│  ┌──────────┐ ┌──────────┐             │  Category Grid
│  │ Kategorie│ │ Kategorie│             │
│  └──────────┘ └──────────┘             │
│                                          │
│  Featured Products:                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐  │  Product Grid
│  │Produkt 1│ │Produkt 2│ │Produkt 3│  │
│  │€ 29.99  │ │€ 49.99  │ │€ 79.99  │  │
│  └─────────┘ └─────────┘ └─────────┘  │
│                                          │
├─────────────────────────────────────────┤
│  © 2025 WebShop | Impressum | Datenschutz
└─────────────────────────────────────────┘
```

#### **Produktdetails**
```
┌─────────────────────────────────────────┐
│  [← Zurück] | 🌙 | 🛒                   │
├─────────────────────────────────────────┤
│                                          │
│  ┌─────────────┐  Produktname           │
│  │    Bild     │  ⭐⭐⭐⭐⭐            │
│  │  [←  →]     │  €29.99                │
│  └─────────────┘  Verfügbar: 15         │
│   Thumbnails: [■][■][■][■]             │
│                                          │
│                   Beschreibung:          │
│                   Lorem ipsum...         │
│                                          │
│                   Menge: [1] [+] [-]    │
│                   [In Warenkorb]        │
│                   [Zu Favoriten]        │
│                                          │
│                   Versand: Kostenlos    │
│                   Rückgabe: 30 Tage     │
│                                          │
│  Bewertungen:      ⭐4.8/5 (124)        │
│  ┌─────────────────────────────────────┐│
│  │"Sehr gutes Produkt!" - Anna, 5⭐   ││
│  │"Schnell erhalten." - Bob, 4⭐       ││
│  └─────────────────────────────────────┘│
│                                          │
└─────────────────────────────────────────┘
```

#### **Warenkorb**
```
┌─────────────────────────────────────────┐
│  🛒 Ihr Warenkorb (3 Artikel)           │
├─────────────────────────────────────────┤
│                                          │
│  Artikel 1: Produkt A        €29.99     │
│  Menge: [1] [2] [3]  [x entfernen]     │
│                                          │
│  Artikel 2: Produkt B        €49.99     │
│  Menge: [2] [3] [4]  [x entfernen]     │
│                                          │
│  ─────────────────────────────────────── │
│  Subtotal:                  €129.97     │
│  Steuern (19%):              €24.69     │
│  Versand:                    Kostenlos  │
│  ─────────────────────────────────────── │
│  **GESAMT:                  €154.66**   │
│                                          │
│  [← Weiter Einkaufen]  [Zur Kasse →]   │
│                                          │
└─────────────────────────────────────────┘
```

#### **Checkout - Adresse**
```
┌─────────────────────────────────────────┐
│  Checkout: Schritt 1 von 3              │
├─────────────────────────────────────────┤
│                                          │
│  Versandadresse:                        │
│  ┌─────────────────────────────────────┐│
│  │ Name: [________________]             ││
│  │ E-Mail: [________________]           ││
│  │ Straße: [________________]           ││
│  │ Hausnr.: [___] PLZ: [_____]         ││
│  │ Stadt: [________________]            ││
│  │ Land: [Deutschland ▼]                ││
│  └─────────────────────────────────────┘│
│                                          │
│  ☐ Abweichende Rechnungsadresse        │
│                                          │
│  [← Zurück]              [Weiter → (3)]│
│                                          │
└─────────────────────────────────────────┘
```

#### **Checkout - Zahlung**
```
┌─────────────────────────────────────────┐
│  Checkout: Schritt 2 von 3              │
├─────────────────────────────────────────┤
│                                          │
│  Zahlungsmethode:                       │
│                                          │
│  ◉ Kreditkarte (Visa, Mastercard)      │
│  ○ PayPal                              │
│  ○ Banküberweisung                     │
│                                          │
│  [Kreditkarte Stripe Widget]           │
│  ┌─────────────────────────────────────┐│
│  │ Kartennummer: [________________]    ││
│  │ MM/YY: [__/__] CVC: [___]          ││
│  └─────────────────────────────────────┘│
│                                          │
│  [← Zurück]              [Weiter → (3)]│
│                                          │
└─────────────────────────────────────────┘
```

#### **Admin - Produktverwaltung**
```
┌─────────────────────────────────────────┐
│  👤 Admin | Dashboard | Produkte | 🚪   │
├─────────────────────────────────────────┤
│                                          │
│  [+ Neues Produkt] [Kategorie: Alle ▼] │
│                                          │
│  ┌─────────────────────────────────────┐│
│  │ Titel      │ Preis │ Lager│ Aktionen││
│  │────────────┼──────┼───────┼────────  ││
│  │ Produkt 1  │€29.99│  15  │ ✏️ 🗑️   ││
│  │ Produkt 2  │€49.99│  8   │ ✏️ 🗑️   ││
│  │ Produkt 3  │€79.99│  0   │ ✏️ 🗑️   ││
│  └─────────────────────────────────────┘│
│                                          │
│  [1] [2] [3] ...                       │  Pagination
│                                          │
└─────────────────────────────────────────┘
```

### 5.1.3 Design-Komponenten

**Buttons:**
```html
<!-- Primary Button -->
<button class="btn btn-primary">In Warenkorb</button>

<!-- Secondary Button -->
<button class="btn btn-secondary">Abbrechen</button>

<!-- Danger Button (Delete) -->
<button class="btn btn-danger">Löschen</button>

<!-- Disabled -->
<button class="btn btn-primary" disabled>Nicht verfügbar</button>
```

**Cards:**
```html
<div class="card">
  <img src="product.jpg" alt="Product">
  <div class="card-body">
    <h3>Produktname</h3>
    <p>€29.99</p>
    <button>Mehr Info</button>
  </div>
</div>
```

**Responsive Breakpoints:**
```css
/* Mobile: < 480px */
.container { display: block; }

/* Tablet: 480px - 768px */
@media (min-width: 480px) {
  .container { display: grid; grid-template-columns: 1fr 1fr; }
}

/* Desktop: > 768px */
@media (min-width: 768px) {
  .container { grid-template-columns: 1fr 1fr 1fr; }
}
```

---

## 5.2 Datenmodell

### 5.2.1 ER-Diagramm

```
                    ┌────────────────┐
                    │     User       │
                    ├────────────────┤
                    │ id (PK)        │
                    │ email (UNIQUE) │
                    │ password_hash  │
                    │ name           │
                    │ created_at     │
                    │ is_admin       │
                    │ is_active      │
                    └────────────────┘
                          │
                ┌─────────┴──────────┐
                │                    │
         ┌──────▼──────┐     ┌──────▼──────┐
         │   Address   │     │   Consent   │
         ├─────────────┤     ├─────────────┤
         │ id (PK)     │     │ id (PK)     │
         │ user_id (FK)      │ user_id (FK)│
         │ street      │     │ type        │ (Marketing, Analytics, Essential)
         │ city        │     │ agreed      │
         │ postal_code │     │ created_at  │
         │ country     │     └─────────────┘
         └─────────────┘

         ┌────────────────┐     ┌────────────────┐
         │   Category     │     │    Product     │
         ├────────────────┤     ├────────────────┤
         │ id (PK)        │     │ id (PK)        │
         │ name           │     │ category_id(FK)│
         │ description    │     │ name           │
         │ created_at     │     │ description    │
         └────────────────┘     │ price          │
                  ▲             │ stock          │
                  │             │ created_at     │
                  │             │ updated_at     │
                  └─────────────┼────────────────┘
                                │
         ┌──────────────────────┴──────────────────┐
         │                                         │
    ┌────▼────────┐                   ┌──────────▼────┐
    │ProductImage │                   │    Order      │
    ├─────────────┤                   ├───────────────┤
    │ id (PK)     │                   │ id (PK)       │
    │ product_id  │                   │ user_id (FK)  │
    │ image_url   │                   │ total_price   │
    │ order       │                   │ status        │
    └─────────────┘                   │ created_at    │
                                      │ updated_at    │
                                      └───────────────┘
                                            │
                            ┌───────────────┴───────────────┐
                            │                               │
                      ┌─────▼─────┐                 ┌──────▼──────┐
                      │OrderItem   │                 │   Payment   │
                      ├────────────┤                 ├─────────────┤
                      │ id (PK)    │                 │ id (PK)     │
                      │ order_id   │                 │ order_id(FK)│
                      │ product_id │                 │ method      │
                      │ quantity   │                 │ status      │
                      │ price      │                 │ amount      │
                      └────────────┘                 │ created_at  │
                                                    └─────────────┘
```

### 5.2.2 Entitäten-Beschreibung

#### **User**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Zweck:** Speichert Nutzerdaten, Authentifizierung
**Besonderheiten:** 
- E-Mail ist eindeutig (UNIQUE)
- Passwort nur gehasht (Argon2)
- is_admin für Rollen-Management

#### **Address**
```sql
CREATE TABLE addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    street VARCHAR(255) NOT NULL,
    postal_code VARCHAR(10) NOT NULL,
    city VARCHAR(255) NOT NULL,
    country VARCHAR(255) DEFAULT 'Germany',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Zweck:** Versand- und Rechnungsadressen
**Besonderheiten:**
- Kann mehrere Adressen pro Nutzer geben
- Country für internationale Expansion

#### **Consent**
```sql
CREATE TABLE consents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,  -- 'marketing', 'analytics', 'essential'
    agreed BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Zweck:** DSGVO-Compliance, Nachverfolgung von Einwilligungen
**Besonderheiten:**
- Separate Einwilligungen pro Kategorie
- Audit-Trail über updated_at

#### **Category**
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Zweck:** Produktklassifizierung
**Besonderheiten:**
- Einfach gehalten (keine Hierarchie im MVP)

#### **Product**
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

**Zweck:** Produktinformationen
**Besonderheiten:**
- price als DECIMAL für Finanz-Genauigkeit
- stock für Verfügbarkeitsprüfung

#### **ProductImage**
```sql
CREATE TABLE product_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

**Zweck:** Multiple Bilder pro Produkt
**Besonderheiten:**
- display_order für Galerie-Sortierung
- Bis zu 20 Bilder pro Produkt

#### **Order**
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending_payment',  -- pending_payment, confirmed, shipped, delivered, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Zweck:** Bestellungen
**Besonderheiten:**
- total_price snapshot zum Zeitpunkt der Order
- status für Workflow-Management

#### **OrderItem**
```sql
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,  -- Preis zum Zeitpunkt der Order
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

**Zweck:** Positionen pro Order
**Besonderheiten:**
- price snapshot (um Preisänderungen zu tracken)

#### **Payment**
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL UNIQUE,
    method VARCHAR(50) NOT NULL,  -- 'credit_card', 'paypal', 'bank_transfer'
    status VARCHAR(50) DEFAULT 'pending',  -- pending, completed, failed
    amount DECIMAL(10, 2) NOT NULL,
    transaction_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
```

**Zweck:** Zahlungsverfolgung
**Besonderheiten:**
- transaction_id von Stripe/PayPal für Nachverfolgung
- status für Payment-Status-Machine

### 5.2.3 Indizes für Performance

```sql
-- Häufig verwendete Abfragen optimieren
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_product_images_product_id ON product_images(product_id);
CREATE INDEX idx_consents_user_id ON consents(user_id);
```

---

## Zusammenfassung Kapitel 5

✅ **UI-Design:**
- Mobile-First, responsive Design
- Barrierefreiheit (WCAG 2.1 AA)
- Dark-Mode Support
- Moderne Komponenten-Struktur

✅ **Datenmodell:**
- Normalisiert (bis 3. Normalform)
- 8 Hauptentitäten mit Relationen
- DECIMAL für Preise (keine Floating-Point-Fehler)
- Audit-Trail durch Timestamps

✅ **Nachverfolgbarkeit:**
- Price Snapshots in Orders (verhindert Konfusion bei Preisänderungen)
- Transaction IDs für Zahlungen
- Status-Machines für Order- und Payment-Lifecycle

---

*Nächste Kapitel: Technologieentscheidungen & Architektur*
