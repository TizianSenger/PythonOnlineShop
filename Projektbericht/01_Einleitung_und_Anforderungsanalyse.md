# Projektbericht: Konzeption und Umsetzung eines Onlineshops

## 1. Einleitung

### 1.1 Hintergrund und Motivation

Die Entwicklung von E-Commerce-Anwendungen stellt eine zentrale Anforderung in der modernen Softwareentwicklung dar. Ein funktionsfähiger Onlineshop erfordert nicht nur technische Kompetenz in der Webentwicklung, sondern auch ein tiefes Verständnis für Datenschutz, regulatorische Compliance und benutzergerechtes Design. 

Dieses Projekt demonstriert die praktische Anwendung von Web-Engineering-Grundlagen bei der Konzeption und Implementierung eines schlanken, aber vollständig funktionsfähigen Onlineshops. Basierend auf meinen Erfahrungen als Full-Stack-Entwickler bei Airbus Defence and Space, wo ich mit Enterprise-Level-Anforderungen an Sicherheit, Skalierbarkeit und Wartbarkeit konfrontiert bin, werde ich ein System entwerfen, das nicht nur gegenwärtigen Standards genügt, sondern auch für zukünftige Erweiterungen robust ausgelegt ist.

### 1.2 Ziele des Projekts

Dieses Projekt verfolgt folgende Ziele:

- **Funktionalität**: Ein vollständig operabler Onlineshop mit Produktverwaltung, Warenkorb und Checkout
- **Compliance**: Umsetzung von Datenschutzanforderungen (DSGVO, PCI-DSS, PSD2)
- **Qualität**: Sichere, wartbare und getestete Implementierung
- **Dokumentation**: Nachvollziehbare Artefakte (Diagramme, Code, Tests)
- **Kreativität**: Durchdachte UX, Rollen-/Berechtigungskonzept, Monitoring

### 1.3 Aufbau des Berichts

Der Bericht folgt den geforderten Schritten der Aufgabenstellung:

1. **Anforderungsanalyse**: Zielgruppen, Rollen, Use Cases
2. **Funktionsumfang**: Feature-Spezifikation
3. **Compliance & Zahlungen**: DSGVO, PCI-DSS, Zahlungsabwicklung
4. **Design & Datenmodell**: UI-Konzepte, ER-Diagramme
5. **Technologieentscheidungen**: Begründete Wahl von Stack
6. **Architektur**: Software-Design und -struktur
7. **Implementierung**: MVP-Realisation mit Code-Beispielen
8. **Testing & Qualität**: Funktions- und Sicherheitstests
9. **Reflexion**: Kritische Bewertung und Learnings

---

## 2. Anforderungsanalyse & Zielgruppen

### 2.1 Zielgruppen und Rollen

Der Onlineshop bedient zwei primäre Zielgruppen mit unterschiedlichen Anforderungen:

#### 2.1.1 Endkund:innen (B2C)

**Charakteristiken:**
- Nutzen den Shop zum Stöbern und Einkaufen von Produkten
- Erwarten intuitive Navigation, schnelle Seitenladung und sichere Bezahlung
- Mobile Geräte-Nutzung ist relevant
- Datenschutz und Privacy sind wichtig

**Rollen & Berechtigungen:**
- **Anonyme Nutzer**: Browsing, Produktsuche, Warenkorb (ohne Login)
- **Registrierte Nutzer**: Zusätzlich: Bestellhistorie, Profilverwaltung, GDPR-Rechte (Dateneinsicht, Löschung)
- **Premium-Nutzer** (optional, zukünftig): Rabatte, exklusive Angebote

#### 2.1.2 Administrator:innen

**Charakteristiken:**
- Verwalten Produkte, Kategorien und Bestellungen
- Benötigen Übersichtlichkeit und Effizienz bei der Datenpflege
- Audit-Logs und Nachverfolgbarkeit sind essenziell

**Rollen & Berechtigungen:**
- **Kategorie-Admin**: Erstellen, Bearbeiten, Löschen von Kategorien
- **Produkt-Admin**: Verwaltung von Produkten, Bilder, Preise, Lagerbestände
- **Order-Admin**: Ansicht, Status-Updates von Bestellungen
- **Super-Admin**: Alle Rechte + Auditierung

### 2.2 Zentrale Use Cases

#### 2.2.1 Nutzer-perspektive (Endkund:innen)

| Use Case | Beschreibung | Aktoren |
|----------|-------------|---------|
| **UC1: Produkte stöbern** | Nutzer durchsucht Shop ohne Login, filtert nach Kategorien | Anonyme Nutzer |
| **UC2: Produktdetails ansehen** | Detaillierte Ansicht mit Bildern, Preis, Beschreibung, Lagerbestand | Alle Nutzer |
| **UC3: In Warenkorb legen** | Produkt mit Menge in Warenkorb (SessionStorage oder DB) | Anonyme/registrierte Nutzer |
| **UC4: Warenkorb verwalten** | Menge ändern, Artikel entfernen, Summe sehen | Anonyme/registrierte Nutzer |
| **UC5: Registrierung/Login** | Konto erstellen oder einloggen | Alle Nutzer |
| **UC6: Checkout & Bezahlung** | Adresse, Zahlungsmethode, Order-Bestätigung | Registrierte Nutzer |
| **UC7: Bestellhistorie** | Frühere Bestellungen einsehen | Registrierte Nutzer |
| **UC8: GDPR-Rechte** | Daten exportieren, Konto löschen | Registrierte Nutzer |

#### 2.2.2 Administrator-perspektive

| Use Case | Beschreibung | Aktoren |
|----------|-------------|---------|
| **UC9: Kategorie verwalten** | CRUD für Kategorien | Admin |
| **UC10: Produkt verwalten** | CRUD für Produkte, Bilder, Preise | Admin |
| **UC11: Bestellung einsehen** | Alle Bestellungen anzeigen, Status ändern | Order-Admin |
| **UC12: Audit-Log** | Nachverfolgung aller Änderungen | Super-Admin |

### 2.3 Priorisierung der Anforderungen (MoSCoW-Methode)

**MUST HAVE (MVP):**
- Produktkatalog mit Kategorien
- Produktsuche und -details
- Warenkorb-Funktionalität
- Registrierung/Login (sichere Authentifizierung)
- Checkout mit Order-Bestätigung
- Admin-Panel für Produkte und Kategorien
- DSGVO-Compliance (Datenschutzerklärung, Einwilligung)

**SHOULD HAVE:**
- Bestellhistorie für Nutzer
- Order-Management für Admins
- Produktbewertungen (optional)
- Newsletter-Anmeldung mit Opt-in
- Dark-Mode für bessere UX

**COULD HAVE:**
- Zahlungsintegration (Stripe/PayPal) – nur API-Structure, keine echte Integration
- Produktempfehlungen (ML-basiert)
- Multi-Language Support
- Advanced Analytics

**WON'T HAVE (für MVP):**
- Lagerbestands-Automation
- Automatische Reorder-Logik
- Integration mit ERP-Systemen

---

## 3. Funktionsumfang

### 3.1 Seiten und Bereiche

**Public Pages (Ohne Login):**
1. **Startseite**: Featured Products, Kategorien-Übersicht
2. **Kategorien-Übersicht**: Alle Kategorien mit Produktcount
3. **Produktliste**: Pro Kategorie, mit Filterung und Pagination
4. **Produktdetails**: Bilder-Galerie, Preis, Beschreibung, "In Warenkorb"-Button
5. **Warenkorb**: Artikelübersicht, Menge, Summe, Checkout-Link
6. **Registrierung**: Formular mit Validierung, Datenschutz-Checkbox
7. **Login**: E-Mail/Passwort
8. **Impressum**: Rechtliche Angaben
9. **Datenschutzerklärung**: DSGVO-konform
10. **Cookie-Banner**: Einwilligung für Analytics/Marketing

**Authentifizierte Pages:**
11. **Dashboard**: Bestellhistorie, Profillinks
12. **Profilverwaltung**: E-Mail, Passwort, Adressenverwaltung
13. **Checkout**: Versand, Zahlungsmethode, Bestätigung
14. **Bestellbestätigung**: Zusammenfassung mit Referenznummer
15. **GDPR-Rechte**: Dateneinsicht, Löschung
16. **Einstellungen**: Benachrichtigungen, Privacy-Einstellungen

**Admin Pages:**
17. **Admin-Dashboard**: Überblick (Bestellungen, Nutzer)
18. **Produkt-Management**: Liste, Erstellen, Bearbeiten, Löschen mit Bildern
19. **Kategorie-Management**: CRUD
20. **Bestellungs-Verwaltung**: Status-Updates, Tracking
21. **Audit-Log**: Änderungshistorie

### 3.2 Kern-Features Detailliert

#### Feature 1: Produktkatalog
- **Kategorisierung**: Hierarchische Struktur (Optional: Subkategorien)
- **Produktbeschreibung**: Titel, Beschreibung, Preis, Lagerbestand
- **Bilder**: Multiple Bilder pro Produkt (bis 20), Galerie-View
- **Suchfunktion**: Volltextsuche nach Titel/Beschreibung
- **Filter & Sortierung**: Nach Preis, Kategorie, Neuheit
- **Pagination**: Max. 12 Produkte pro Seite

#### Feature 2: Warenkorb
- **Session-basiert**: Für anonyme Nutzer
- **DB-persistiert**: Für registrierte Nutzer
- **Funktionen**: Menge anpassen, Artikel entfernen, Leeren
- **Berechnung**: Subtotal, Steuern (19%), Gesamtpreis
- **Persistierung**: Nach Logout wiederherstellbar (Hybrid-Ansatz)

#### Feature 3: Authentifizierung & Autorisierung
- **Registrierung**: E-Mail, Passwort (bcrypt/Argon2), Validierung
- **Login**: Sichere Session-Verwaltung, CSRF-Protection
- **Rollen**: Admin, User, Anonymous
- **Berechtigungen**: Route-basierte Zugriffskontrolle

#### Feature 4: Checkout
- **Schritte**: Warenkorb → Versandadresse → Zahlungsmethode → Bestätigung
- **Zahlungsarten**: 
  - Vorab-Struktur für Stripe/PayPal (ohne echte Integration)
  - Kreditkarte (nur Struktur, kein reales Processing)
  - Banküberweisung (Simuliert)
- **Order-Generierung**: Eindeutige Referenznummer, Timestamp
- **E-Mail-Bestätigung**: Bestellsummary an Nutzer (optional)

#### Feature 5: DSGVO-Compliance
- **Datenschutzerklärung**: Umfassend, verständlich
- **Einwilligungen**: Checkbox bei Registrierung, Newsletter, Cookies
- **Dateneinsicht (Art. 15 DSGVO)**: Nutzer können ihre Daten abrufen
- **Recht auf Löschung (Art. 17)**: "Vergessen"-Funktion
- **Cookie-Management**: Banner mit Granularer Kontrolle (Essential, Analytics, Marketing)
- **Audit-Log**: Nachverfolgung von Datenzugriffen

---

## 4. Zusammenfassung Kapitel 1-3

Dieser Bericht beginnt mit einer Grundlegung der Anforderungen:

- **Zwei Zielgruppen**: Endkund:innen (mit Anonymen und Registrierten) und Admins
- **MoSCoW-Priorisierung**: MVP mit MUST HAVEs, erweiterbar auf SHOULD/COULD
- **16+ Seiten/Features**: Von Katalog über Checkout bis DSGVO
- **Use-Case-getrieben**: Alle Anforderungen sind an reale Nutzer-Szenarien gebunden

---

**Nächste Kapitel folgen:**
- Kapitel 4: Zahlungsabwicklung & Compliance
- Kapitel 5: UI-Design & Mockups
- Kapitel 6: Datenmodell

---

*Bitte gib mir Feedback zu den Kapiteln 1-3, bevor ich weitermache!*
