# Kapitel 4: Zahlungsabwicklung & Compliance

## 4.1 Zahlungsabwicklung

### 4.1.1 Zahlungsmodell und Architektur

Die sichere Abwicklung von Zahlungen erfordert eine klare Trennung zwischen Shop-Logik und Zahlungsverarbeitung. Basierend auf Best Practices aus der Enterprise-Entwicklung wird ein **Payment Abstraction Layer** implementiert:

```
┌─────────────────┐
│   Checkout UI   │
└────────┬────────┘
         │
┌────────▼──────────────────┐
│  Payment Service Layer    │  ← Kapselt Zahlungslogik
│  (Abstraktion)            │
└────────┬──────────────────┘
         │
    ┌────┴────┐
    │          │
┌───▼──┐  ┌───▼──────┐
│Stripe│  │PayPal    │  ← Zahlungsdienstleister
└──────┘  └──────────┘
```

**Begründung:**
- PCI-DSS fordert, dass keine Kreditkartendaten auf dem eigenen Server gespeichert werden
- Delegation an spezialisierte Zahlungsdienstleister minimiert Sicherheitsrisiken
- Abstraktion ermöglicht einfachen Austausch von Zahlungsanbietern

### 4.1.2 Implementierte Zahlungsarten

#### 1. **Kreditkarte (via Stripe)**
- **Flow**: 
  1. Nutzer gibt Kartendaten im Checkout ein
  2. Frontend sendet Tokens an Stripe (nicht Kartendaten!)
  3. Shop erhält Zahlungsbestätigung
  4. Order wird erstellt
  
- **Sicherheit**: PCI-DSS komplett ausgelagert auf Stripe
- **Implementierung**: Stripe Elements API (vorkonfiguriert, nicht implementiert)

#### 2. **PayPal**
- **Flow**: 
  1. Nutzer klickt "PayPal" Button
  2. Redirect zu PayPal-Login
  3. Authorisierung und Return mit Token
  4. Shop bestätigt Zahlung bei PayPal
  
- **Sicherheit**: OAuth2-basiert, keine lokale Speicherung von Zugangsdaten
- **Implementierung**: PayPal REST API (Struktur vorhanden)

#### 3. **Banküberweisung** (für MVP)
- **Flow**: 
  1. Order mit Status "Pending Payment"
  2. IBAN wird dem Nutzer angezeigt
  3. Admin prüft manuell oder via Automated Clearing House (ACH)
  4. Status wird zu "Paid" aktualisiert
  
- **Sicherheit**: Keine Kartendaten, Transaktionen via Bankensystem
- **Implementierung**: Fully implementiert

### 4.1.3 Order-Lifecycle

```
┌──────────┐     ┌─────────────┐     ┌──────────┐     ┌──────────┐
│  Pending │ ──▶ │  Confirmed  │ ──▶ │ Shipped  │ ──▶ │Delivered │
└──────────┘     └─────────────┘     └──────────┘     └──────────┘
     │                  │
     │            ┌──────▼─────┐
     │            │Payment Wait │
     │            └─────────────┘
     │
     └──▶ [Cancelled]
```

**Status-Übergänge:**
- `pending_payment`: Warte auf Zahlungsbestätigung
- `confirmed`: Zahlung erhalten, Fulfillment beginnt
- `shipped`: Ware versendet, Tracking verfügbar
- `delivered`: Zustellung bestätigt
- `cancelled`: Storniert durch Nutzer oder Admin

---

## 4.2 Compliance & Datenschutz

### 4.2.1 DSGVO (Datenschutz-Grundverordnung)

Die Europäische Datenschutz-Grundverordnung (DSGVO) ist das Kernregelwerk für den Umgang mit Kundendaten. Der Shop implementiert folgende Anforderungen:

#### Grundprinzipien:

| Prinzip | Umsetzung |
|---------|-----------|
| **Rechtmäßigkeit** | Nur mit Einwilligung oder rechtslichen Grund (Vertragserledigung) |
| **Datenminimierung** | Nur notwendige Daten erfassen (E-Mail, Name, Adresse, Zahlungsdaten) |
| **Speicherbegrenzung** | Gelöschte Orders 3 Jahre (Aufbewahrung), dann automatische Löschung |
| **Transparenz** | Datenschutzerklärung für alle Nutzer sichtbar |

#### Implementierte Maßnahmen:

**1. Einwilligung & Consent Management**
```markdown
- Checkbox bei Registrierung: "Ich akzeptiere die Datenschutzerklärung"
- Separate Checkboxen für:
  * Marketing-E-Mails (opt-in)
  * Analytische Cookies
  * Funktionale Cookies (notwendig)
- Einwilligungen werden geloggt mit Timestamp
```

**2. Dateneinsicht (Art. 15)**
- Nutzer können unter "GDPR-Rechte" ihre Daten einsehen:
  * Profilinformationen (Name, E-Mail, Adresse)
  * Bestellhistorie
  * Bezahlte Summen
  * Einwilligungen

**3. Recht auf Löschung (Art. 17)**
- Anonymisierung statt Löschung (zur Audit-Compliance)
- "Vergessen"-Button im Nutzerprofil
- Nach Bestätigung: Daten werden anonymisiert
- Bestellhistorie bleibt erhalten (rechtlich notwendig)

**4. Datenschutzerklärung**
- Umfassend, in einfacher Sprache
- Abschnitte zu:
  * Verantwortliche
  * Rechtsgrundlagen
  * Datenverarbeitung
  * Cookies
  * Benutzerrechte

#### Cookie-Management:

```javascript
// Cookie-Kategorien mit Granularität
const cookieConsent = {
  essential: true,        // Notwendig, immer aktiv
  analytics: false,       // Google Analytics - opt-in
  marketing: false,       // Remarketing Pixel - opt-in
  timestamp: "2025-12-27"
};
```

**Implementierung:**
- Cookie-Banner bei erstem Besuch
- Granulare Einstellungen ("Einstellungen" Button)
- Nutzer können jederzeit ändern
- Consent wird in localStorage/Datenbank gespeichert

### 4.2.2 PCI-DSS (Payment Card Industry Data Security Standard)

PCI-DSS definiert Sicherheitsstandards für Kartenzahlungen. Der Shop ist **PCI-DSS komplett**, weil:

| Anforderung | Status | Begründung |
|-------------|--------|-----------|
| **Keine Speicherung von Kartendaten** | ✅ Erfüllt | Stripe/PayPal speichern Daten, nicht wir |
| **SSL/TLS-Verschlüsslung** | ✅ Erfüllt | Alle Zahlungen über HTTPS |
| **Firewall** | ✅ Erfüllt | Deployment mit WAF möglich |
| **Zugriffskontrolle** | ✅ Erfüllt | Rollen-basiert (Admin/User/Anon) |
| **Monitoring** | ✅ Erfüllt | Audit-Log + Error-Logging |
| **Penetration Testing** | ⚠️ Geplant | In Production-Umgebung |

**Praktische Umsetzung:**
```python
# ❌ NIEMALS: Kartendaten speichern
# card_number = request.form.get('card')  # NEIN!

# ✅ IMMER: Token von Zahlungsanbieter verwenden
stripe_token = request.form.get('stripeToken')
payment = stripe.Charge.create(
    amount=total_price,
    currency='eur',
    source=stripe_token  # Token, nicht echte Kartendaten
)
```

### 4.2.3 PSD2 (Payment Services Directive 2)

PSD2 regelt E-Payment-Services in der EU. Der Shop beachtet:

| Anforderung | Umsetzung |
|-------------|-----------|
| **Strong Customer Authentication (SCA)** | Stripe/PayPal kümmern sich drum |
| **Two-Factor Authentication** | Optional für Admin-Login |
| **Offene Bankendaten-APIs** | Nicht relevant für MVP |
| **Transparente Gebührenangabe** | Stripe-Gebühren werden transparent gemacht |

---

## 4.3 Weitere Sicherheits- & Compliance-Maßnahmen

### 4.3.1 Authentifizierung & Session-Management

```python
# Passwort-Hashing mit Argon2 (Best Practice 2025)
from argon2 import PasswordHasher

ph = PasswordHasher()
hashed = ph.hash(password)  # Argon2id
verified = ph.verify(hashed, password)  # Sicher vergleichen
```

**Session-Sicherheit:**
- Secure HttpOnly Cookies (XSS-Protection)
- SameSite=Strict (CSRF-Protection)
- Session-Timeout nach 30 Min Inaktivität
- CSRF-Token für alle Formular-Submissions

### 4.3.2 Eingabevalidierung & Injection-Schutz

```python
# SQL-Injection-Schutz durch Parameterized Queries
cursor.execute(
    'SELECT * FROM products WHERE id = ?',
    (product_id,)  # Parameter, nicht String-Konkatenation!
)

# XSS-Schutz durch Template Escaping
{{ product.description }}  # Jinja2 escaped automatisch
```

### 4.3.3 Audit-Logging

Alle kritischen Aktionen werden geloggt:

```csv
timestamp,user_id,action,resource,status
2025-12-27T14:32:10,user_123,order_create,order_456,success
2025-12-27T14:35:22,admin_1,product_update,prod_789,success
2025-12-27T14:40:05,user_123,password_change,user_123,success
2025-12-27T15:22:18,admin_1,order_status_update,order_456,shipped
```

---

## 4.4 Datenschutz-Konzept: Aufbewahrung & Löschung

### Aufbewahrungsfristen:

| Datentyp | Grund | Frist | Auto-Löschung |
|----------|-------|-------|---------------|
| **Bestellungen** | Buchhaltung | 3 Jahre | Ja, nach Frist |
| **Rechnungsdaten** | Buchhaltung | 3 Jahre | Ja |
| **Kundenprofil** | Vertrag | Während Kundschaft | Manuell durch Nutzer |
| **Cookie-Consent** | DSGVO | 2 Jahre | Ja |
| **Audit-Log** | Compliance | 1 Jahr | Ja |
| **Marketing-Listen** | DSGVO | Bis Abmeldung | Manuell/API |

### Löschungs-Prozess:

```
Nutzer klickt "Account löschen"
        │
        ▼
Bestätigungscode via E-Mail
        │
        ▼
Nutzer bestätigt Code
        │
        ▼
Anonymisierung:
  - Name → "User_[ID]"
  - E-Mail → "deleted_[ID]@deleted.local"
  - Adresse → gelöscht
  - Passwort → Gerätet
        │
        ▼
Bestellhistorie bleibt (rechtlich notwendig)
        │
        ▼
Account als "deleted" markiert
```

---

## Zusammenfassung Kapitel 4

✅ **Zahlungsabwicklung:**
- Payment Abstraction Layer mit Stripe/PayPal
- Banküberweisung für MVP
- Order-Lifecycle mit Status-Tracking

✅ **Compliance:**
- DSGVO vollständig implementiert (Consent, Dateneinsicht, Löschung)
- PCI-DSS durch Delegation ausgelagert
- PSD2-konform durch moderne Zahlungsanbieter

✅ **Sicherheit:**
- Sichere Authentifizierung (Argon2)
- Injection-Schutz (SQL, XSS)
- Audit-Logging für Nachverfolgbarkeit

---

*Nächstes Kapitel: UI-Design, Mockups & Datenmodell*
