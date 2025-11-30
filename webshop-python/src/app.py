import os
import smtplib
import json
import csv as csv_module
from email.message import EmailMessage
from pathlib import Path
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from storage.csv_backend import CSVBackend
from storage.sqlite_backend import SQLiteBackend
from storage.hybrid_backend import HybridBackend
from api.checkout_routes import checkout_bp
from config import SECRET_KEY, SMTP_USER, SMTP_PASS, ADMIN_PIN, CSV_FOLDER_PATH, USE_DATABASE, DB_PATH
from utils.logging_service import audit_logger, AuditLogType

# App initialisieren
app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), "templates"),
            static_folder=os.path.join(os.path.dirname(__file__), "static"))
app.secret_key = SECRET_KEY

# Checkout-Routen registrieren
app.register_blueprint(checkout_bp)

# Backend initialisieren: Hybrid (SQLite + CSV)
csv_backend = CSVBackend(str(CSV_FOLDER_PATH))

# Versuche SQLite Backend zu initialisieren
sqlite_backend = None
if USE_DATABASE:
    try:
        sqlite_backend = SQLiteBackend(str(DB_PATH))
        app.logger.info(f"SQLite Backend initialisiert: {DB_PATH}")
    except Exception as e:
        app.logger.warning(f"SQLite Backend Initialisierung fehlgeschlagen: {e}. Nutze nur CSV-Backend.")

# Nutze Hybrid-Backend für Fallback-Logik
backend = HybridBackend(csv_backend, sqlite_backend)

# Upload-Konfiguration
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def get_cart_item_count(cart):
    """Berechne die Gesamtanzahl der Artikel im Warenkorb"""
    return sum(int(item.get('quantity', 1)) for item in cart)

def send_registration_email(to_email, name, role):
    msg = EmailMessage()
    msg["Subject"] = "Willkommen beim WebShop"
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    body = f"Hallo {name},\n\nDein {role}-Konto wurde erfolgreich erstellt.\n\nViele Grüße,\nWebShop"
    msg.set_content(body)
    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
    except Exception as e:
        print("Fehler beim Senden der E-Mail:", e)

@app.route("/")
def index():
    # Filter-Parameter
    q = request.args.get('q', '').strip().lower()
    category = request.args.get('category', '').strip().lower()
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')

    products = backend.get_all_products()
    for p in products:
        p['price'] = p.get('price', '') or '0'
        p['stock'] = p.get('stock', '') or '0'
        # Hole das erste Bild oder nutze leeren String
        images = p.get('images', [])
        p['main_image'] = images[0] if images and len(images) > 0 else ''

    categories = sorted({(p.get('category') or '').strip() for p in products if p.get('category')})

    def matches(p):
        if q and q not in (p.get('name','') or '').lower() and q not in (p.get('description','') or '').lower():
            return False
        if category and category != (p.get('category','') or '').lower():
            return False
        try:
            price = float(p.get('price', 0))
        except Exception:
            price = 0.0
        if min_price:
            try:
                if price < float(min_price): return False
            except:
                pass
        if max_price:
            try:
                if price > float(max_price): return False
            except:
                pass
        return True

    filtered = [p for p in products if matches(p)]
    cart = session.get("cart", [])
    cart_count = get_cart_item_count(cart)
    return render_template("index.html", products=filtered, cart_count=cart_count, categories=categories)

@app.route("/product/<product_id>")
def product_detail(product_id):
    product = backend.get_product(product_id)
    if not product:
        flash("Produkt nicht gefunden.", "danger")
        return redirect(url_for("index"))
    
    product['price'] = product.get('price', '0')
    product['stock'] = product.get('stock', '0')
    product['images'] = product.get('images', [])
    
    cart = session.get("cart", [])
    cart_count = get_cart_item_count(cart)
    return render_template("product_detail.html", product=product, cart_count=cart_count)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        cart = session.get("cart", [])
        cart_count = get_cart_item_count(cart)
        return render_template("register.html", cart_count=cart_count)
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    role = request.form.get("role", "user")
    admin_pin = request.form.get("admin_pin", "")

    if not name or not email or not password:
        flash("Bitte alle Pflichtfelder ausfüllen.", "danger")
        return redirect(url_for("register"))

    # DSGVO-Einwilligungen prüfen
    privacy_accept = request.form.get("privacy_accept") == "on"
    terms_accept = request.form.get("terms_accept") == "on"
    
    if not privacy_accept or not terms_accept:
        flash("Bitte akzeptieren Sie die Datenschutzerklärung und AGB.", "danger")
        return redirect(url_for("register"))

    if role == "admin" and admin_pin != ADMIN_PIN:
        flash("Falscher Admin-PIN.", "danger")
        return redirect(url_for("register"))

    users = backend.get_all_users()
    if any(u.get("email", "").lower() == email for u in users):
        flash("E-Mail bereits registriert.", "danger")
        return redirect(url_for("register"))

    hashed = generate_password_hash(password)
    user = {
        "name": name,
        "email": email,
        "password": hashed,
        "role": role,
        "privacy_accept": "True",
        "marketing_consent": "True" if request.form.get("marketing_consent") == "on" else "False",
        "analytics_consent": "True" if request.form.get("analytics_consent") == "on" else "False"
    }
    user_id = backend.save_user(user)
    
    # Logge Registrierung (DSGVO-Compliance)
    audit_logger.log(
        event_type=AuditLogType.USER_REGISTRATION,
        user_id=user_id,
        user_email=email,
        action="User registered",
        details={"role": role},
        ip_address=request.remote_addr
    )
    
    # Speichere Einwilligungen separat
    backend.save_consent(user_id, "privacy_policy", "True")
    backend.save_consent(user_id, "marketing", user.get("marketing_consent"))
    backend.save_consent(user_id, "analytics", user.get("analytics_consent"))
    
    try:
        send_registration_email(email, name, role)
    except Exception:
        pass
    
    session["user"] = {"id": user_id, "name": name, "email": email, "role": role}
    flash("Registrierung erfolgreich.", "success")
    return redirect(url_for("dashboard"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        cart = session.get("cart", [])
        cart_count = get_cart_item_count(cart)
        return render_template("login.html", cart_count=cart_count)
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    users = backend.get_all_users()
    user = next((u for u in users if u.get("email", "").lower() == email), None)
    if not user or not check_password_hash(user.get("password", ""), password):
        flash("Email oder Passwort falsch.", "danger")
        return redirect(url_for("login"))

    session["user"] = {"id": user.get("id"), "name": user.get("name"), "email": user.get("email"), "role": user.get("role", "user")}
    session["cart"] = []  # Clear cart on login
    session.modified = True
    flash("Eingeloggt.", "success")
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("cart", None)  # Clear cart on logout
    session.modified = True
    flash("Ausgeloggt.", "info")
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        flash("Bitte loggen Sie sich ein.", "danger")
        return redirect(url_for("login"))
    products = backend.get_all_products()
    cart = session.get("cart", [])
    cart_count = get_cart_item_count(cart)
    return render_template("dashboard.html", user=user, products=products, cart_count=cart_count)

# Warenkorb-Routes
@app.route("/cart")
def cart():
    user = session.get("user")
    if not user:
        flash("Bitte loggen Sie sich ein, um den Warenkorb zu sehen.", "danger")
        return redirect(url_for("login"))
    
    cart_items = session.get("cart", [])
    products = backend.get_all_products()
    cart_with_details = []
    for cart_item in cart_items:
        product = next((p for p in products if p.get("id") == cart_item["product_id"]), None)
        if product:
            cart_item["name"] = product.get("name")
            try:
                cart_item["price"] = float(product.get("price", 0))
            except:
                cart_item["price"] = 0.0
            cart_with_details.append(cart_item)
    total = sum(item["price"] * item["quantity"] for item in cart_with_details)
    cart_count = get_cart_item_count(session.get("cart", []))
    return render_template("cart.html", cart=cart_with_details, total=total, cart_count=cart_count)

@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    # Prüfe, ob User eingeloggt ist
    user = session.get("user")
    if not user:
        return jsonify({"success": False, "error": "Bitte loggen Sie sich ein, um Produkte hinzuzufügen."}), 401
    
    data = request.get_json() or {}
    product_id = data.get("product_id")
    try:
        quantity = int(data.get("quantity", 1))
    except (ValueError, TypeError):
        quantity = 1

    cart = session.get("cart", [])
    existing = next((item for item in cart if item["product_id"] == product_id), None)
    if existing:
        existing["quantity"] += quantity
    else:
        cart.append({"product_id": product_id, "quantity": quantity})
    session["cart"] = cart
    session.modified = True
    cart_count = get_cart_item_count(cart)
    return jsonify({"success": True, "cart_count": cart_count})

@app.route("/remove-from-cart/<product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = session.get("cart", [])
    cart = [item for item in cart if item["product_id"] != product_id]
    session["cart"] = cart
    session.modified = True
    return redirect(url_for("cart"))

@app.route("/update-cart/<product_id>", methods=["POST"])
def update_cart(product_id):
    data = request.get_json() or {}
    try:
        quantity = int(data.get("quantity", 1))
    except:
        quantity = 1
    cart = session.get("cart", [])
    item = next((item for item in cart if item["product_id"] == product_id), None)
    if item:
        if quantity <= 0:
            cart = [i for i in cart if i["product_id"] != product_id]
        else:
            item["quantity"] = quantity
    session["cart"] = cart
    session.modified = True
    return jsonify({"success": True})

# Admin-Produkt-Verwaltung
@app.route("/admin/products", methods=["GET", "POST"])
def admin_products():
    user = session.get("user")
    if not user or user.get("role") != "admin":
        flash("Zugriff verweigert.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        price = request.form.get("price", "")
        description = request.form.get("description", "").strip()
        stock = request.form.get("stock", "0")
        image_files = request.files.getlist("images")

        if not name or not price or not category:
            flash("Bitte alle Pflichtfelder ausfüllen.", "danger")
            return redirect(url_for("admin_products"))

        try:
            price = float(price)
        except ValueError:
            flash("Preis muss eine Zahl sein.", "danger")
            return redirect(url_for("admin_products"))

        images_list = []
        for image_file in image_files:
            if image_file and image_file.filename and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                base, ext = os.path.splitext(filename)
                filename = f"{base}_{int(os.times()[4])}{ext}"
                dest = os.path.join(UPLOAD_FOLDER, filename)
                image_file.save(dest)
                images_list.append(filename)
                if len(images_list) >= 20:
                    break

        product = {
            "name": name,
            "category": category,
            "price": str(price),
            "description": description,
            "images": images_list,
            "stock": str(int(stock) if stock.isdigit() else 0)
        }

        backend.save_product(product)
        flash(f"Produkt '{name}' erfolgreich hinzugefügt.", "success")
        return redirect(url_for("admin_products"))

    products = backend.get_all_products()
    cart = session.get("cart", [])
    cart_count = get_cart_item_count(cart)
    return render_template("admin_products.html", user=user, products=products, cart_count=cart_count)

@app.route("/admin/edit-product/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    user = session.get("user")
    if not user or user.get("role") != "admin":
        flash("Zugriff verweigert.", "danger")
        return redirect(url_for("index"))

    product = backend.get_product(product_id)
    if not product:
        flash("Produkt nicht gefunden.", "danger")
        return redirect(url_for("admin_products"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        price = request.form.get("price", "")
        description = request.form.get("description", "").strip()
        stock = request.form.get("stock", "0")
        image_files = request.files.getlist("images")

        if not name or not price or not category:
            flash("Bitte alle Pflichtfelder ausfüllen.", "danger")
            return redirect(url_for("edit_product", product_id=product_id))

        try:
            price = float(price)
        except ValueError:
            flash("Preis muss eine Zahl sein.", "danger")
            return redirect(url_for("edit_product", product_id=product_id))

        images_list = product.get('images', []) if isinstance(product.get('images'), list) else []
        
        # Add new images if there's space
        for image_file in image_files:
            if len(images_list) >= 20:
                break
            if image_file and image_file.filename and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                base, ext = os.path.splitext(filename)
                filename = f"{base}_{int(os.times()[4])}{ext}"
                dest = os.path.join(UPLOAD_FOLDER, filename)
                image_file.save(dest)
                images_list.append(filename)

        updates = {
            "name": name,
            "category": category,
            "price": str(price),
            "description": description,
            "images": images_list,
            "stock": str(int(stock) if stock.isdigit() else 0)
        }
        backend.update_product(product_id, updates)
        flash("Produkt aktualisiert.", "success")
        return redirect(url_for("admin_products"))

    cart = session.get("cart", [])
    cart_count = get_cart_item_count(cart)
    return render_template("edit_product.html", user=user, product=product, cart_count=cart_count)

@app.route("/admin/delete-product/<product_id>", methods=["POST"])
def delete_product(product_id):
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return jsonify({"success": False, "error": "Zugriff verweigert"}), 403

    backend.delete_product(product_id)
    flash("Produkt gelöscht.", "success")
    return redirect(url_for("admin_products"))

@app.route("/admin/remove-product-image/<product_id>/<image_name>", methods=["POST"])
def remove_product_image(product_id, image_name):
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return jsonify({"success": False, "error": "Zugriff verweigert"}), 403

    product = backend.get_product(product_id)
    if not product:
        return jsonify({"success": False, "error": "Produkt nicht gefunden"}), 404

    images = product.get('images', [])
    if image_name in images:
        images.remove(image_name)
        backend.update_product(product_id, {"images": images})
        # Optional: Delete file from uploads
        try:
            file_path = os.path.join(UPLOAD_FOLDER, image_name)
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        return jsonify({"success": True})
    
    return jsonify({"success": False, "error": "Bild nicht gefunden"}), 404

# Bestellungs-Verwaltung
# Status-Abfolge für Bestellungen
ORDER_STATUSES = ["paid", "in_bearbeitung", "vorbereitung_transport", "abgeschickt", "zugestellt"]

@app.route("/orders")
def orders():
    user = session.get("user")
    if not user:
        flash("Bitte loggen Sie sich ein.", "danger")
        return redirect(url_for("login"))
    
    all_orders = backend.get_all_orders()
    
    # Normale User sehen nur ihre eigenen Bestellungen
    if user.get("role") != "admin":
        orders_to_show = [o for o in all_orders if o.get("user_id") == user.get("id")]
    else:
        # Admin sieht alle Bestellungen
        orders_to_show = all_orders
    
    # Parse und formatiere Bestellungen
    formatted_orders = []
    for order in orders_to_show:
        formatted_order = _parse_order(order, user)
        if formatted_order:
            formatted_orders.append(formatted_order)
    
    # Sortiere nach Datum (neueste zuerst)
    formatted_orders.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    cart = session.get("cart", [])
    cart_count = get_cart_item_count(cart)
    return render_template("orders.html", user=user, orders=formatted_orders, cart_count=cart_count, statuses=ORDER_STATUSES)

@app.route("/admin/update-order-status/<order_id>", methods=["POST"])
def update_order_status(order_id):
    """Update the status of an order (admin only)"""
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return jsonify({"success": False, "error": "Zugriff verweigert"}), 403
    
    data = request.get_json() or {}
    new_status = data.get("status", "").strip()
    
    if new_status not in ORDER_STATUSES:
        return jsonify({"success": False, "error": "Ungültiger Status"}), 400
    
    updated = backend.update_order(order_id, {"status": new_status})
    if updated:
        return jsonify({"success": True, "message": "Status aktualisiert"})
    else:
        return jsonify({"success": False, "error": "Bestellung nicht gefunden"}), 404

@app.route("/admin/delete-order/<order_id>", methods=["POST"])
def delete_order(order_id):
    """Delete an order (admin only)"""
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return jsonify({"success": False, "error": "Zugriff verweigert"}), 403
    
    try:
        backend.delete_order(order_id)
        audit_logger.log(
            event_type=AuditLogType.ADMIN_ACTION,
            user_id=user.get("id"),
            user_email=user.get("email"),
            action="delete_order",
            resource_type="order",
            resource_id=order_id,
            ip_address=request.remote_addr
        )
        return jsonify({"success": True, "message": "Bestellung gelöscht"})
    except Exception as e:
        app.logger.error(f"Fehler beim Löschen der Bestellung: {e}")
        return jsonify({"success": False, "error": "Fehler beim Löschen"}), 500

def _parse_order(order, current_user):
    """Parse order data and handle JSON fields"""
    try:
        order_items = order.get("items", "[]")
        if isinstance(order_items, str):
            order_items = json.loads(order_items) if order_items else []
        
        customer = order.get("customer", "{}")
        if isinstance(customer, str):
            customer = json.loads(customer) if customer else {}
        
        # Hole User-Name wenn Admin
        user_name = ""
        if current_user.get("role") == "admin":
            users = backend.get_all_users()
            user_obj = next((u for u in users if u.get("id") == order.get("user_id")), None)
            user_name = user_obj.get("name", "Unbekannt") if user_obj else "Unbekannt"
        
        return {
            "id": order.get("id", ""),
            "user_id": order.get("user_id", ""),
            "user_name": user_name,
            "order_items": order_items,
            "total": order.get("total", "0"),
            "customer": customer,
            "status": order.get("status", "pending"),
            "payment_provider": order.get("payment_provider", ""),
            "provider_id": order.get("provider_id", ""),
            "created_at": order.get("created_at", "")
        }
    except ValueError:
        return None
    except TypeError:
        return None


# ===== DSGVO-Compliance Routes =====

@app.route("/privacy-policy")
def privacy_policy():
    """Datenschutzerklärung (DSGVO-Anforderung)"""
    return render_template("privacy_policy.html", current_date=datetime.now().strftime("%d.%m.%Y"))

@app.route("/impressum")
def impressum():
    """Impressum (TMG-Anforderung)"""
    return render_template("impressum.html", current_date=datetime.now().strftime("%d.%m.%Y"))

@app.route("/terms-of-service")
def terms_of_service():
    """Allgemeine Geschäftsbedingungen"""
    cart = session.get("cart", [])
    cart_count = get_cart_item_count(cart)
    return render_template("terms_of_service.html", cart_count=cart_count)

@app.route("/gdpr-rights")
def gdpr_rights():
    """Betroffenenrechte (Art. 12-22 DSGVO)"""
    user = session.get("user")
    cart = session.get("cart", [])
    cart_count = get_cart_item_count(cart)
    return render_template("gdpr_rights.html", user=user, cart_count=cart_count)

@app.route("/api/log-cookie-consent", methods=["POST"])
def log_cookie_consent():
    """Logge Cookie-Einwilligung (DSGVO-Compliance)"""
    try:
        data = request.get_json() or {}
        user = session.get("user")
        user_id = user.get("id") if user else None
        user_email = user.get("email") if user else "anonymous"
        
        audit_logger.log(
            event_type=AuditLogType.COOKIE_CONSENT,
            user_id=user_id,
            user_email=user_email,
            action="Cookie consent provided",
            details=data,
            ip_address=request.remote_addr
        )
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"Fehler beim Logging der Cookie-Einwilligung: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/gdpr/data-export", methods=["GET"])
def gdpr_data_export():
    """Exportiere Benutzerdaten (Art. 15 DSGVO - Recht auf Auskunft)"""
    user = session.get("user")
    if not user:
        flash("Bitte melden Sie sich an.", "danger")
        return redirect(url_for("login"))
    
    user_id = user.get("id")
    
    # Logge Dateneinsicht
    audit_logger.log(
        event_type=AuditLogType.USER_DATA_EXPORT,
        user_id=user_id,
        user_email=user.get("email"),
        action="User requested data export",
        ip_address=request.remote_addr
    )
    
    # Hole alle Benutzerdaten
    export_data = backend.export_user_data(user_id)
    if not export_data:
        flash("Benutzerdaten nicht gefunden.", "danger")
        return redirect(url_for("dashboard"))
    
    cart = session.get("cart", [])
    cart_count = get_cart_item_count(cart)
    
    return render_template("gdpr_data_view.html", 
                         user=user, 
                         export_data=export_data,
                         cart_count=cart_count)

@app.route("/gdpr/export-data", methods=["POST"])
def gdpr_export_data():
    """Exportiere Benutzerdaten als JSON/CSV (Art. 20 DSGVO - Datenportabilität)"""
    user = session.get("user")
    if not user:
        return jsonify({"success": False, "error": "Nicht authentifiziert"}), 401
    
    user_id = user.get("id")
    format_type = request.form.get("format", "json").lower()
    
    # Hole Daten
    export_data = backend.export_user_data(user_id)
    if not export_data:
        return jsonify({"success": False, "error": "Daten nicht gefunden"}), 404
    
    # Logge Export
    audit_logger.log(
        event_type=AuditLogType.USER_DATA_EXPORT,
        user_id=user_id,
        user_email=user.get("email"),
        action=f"Data export requested ({format_type})",
        ip_address=request.remote_addr
    )
    
    if format_type == "json":
        # JSON Export
        import io
        json_data = json.dumps(export_data, ensure_ascii=False, indent=2)
        return send_file(
            io.BytesIO(json_data.encode('utf-8')),
            mimetype="application/json",
            as_attachment=True,
            download_name=f"webshop_data_{user_id}_{datetime.now().strftime('%Y%m%d')}.json"
        )
    
    elif format_type == "csv":
        # CSV Export (vereinfacht)
        import io
        output = io.StringIO()
        writer = csv_module.writer(output)
        
        # Profile
        writer.writerow(["=== PROFILDATEN ==="])
        writer.writerow(["Feld", "Wert"])
        for key, value in export_data['profile'].items():
            writer.writerow([key, str(value)])
        
        # Orders
        writer.writerow([])
        writer.writerow(["=== BESTELLUNGEN ==="])
        writer.writerow(["Bestellungs-ID", "Datum", "Total", "Status"])
        for order in export_data['orders']:
            writer.writerow([
                order.get('id'),
                order.get('created_at', 'N/A'),
                order.get('total'),
                order.get('status')
            ])
        
        # Consents
        writer.writerow([])
        writer.writerow(["=== EINWILLIGUNGEN ==="])
        writer.writerow(["Typ", "Wert", "Zeitstempel"])
        for consent in export_data['consents']:
            writer.writerow([
                consent.get('consent_type'),
                consent.get('value'),
                consent.get('timestamp')
            ])
        
        csv_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
        return send_file(
            csv_bytes,
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"webshop_data_{user_id}_{datetime.now().strftime('%Y%m%d')}.csv"
        )
    
    return jsonify({"success": False, "error": "Ungültiges Format"}), 400

@app.route("/gdpr/delete-account", methods=["POST"])
def gdpr_delete_account():
    """Lösche Benutzerkonto und Daten (Art. 17 DSGVO - Recht auf Vergessenwerden)"""
    user = session.get("user")
    if not user:
        flash("Bitte melden Sie sich an.", "danger")
        return redirect(url_for("login"))
    
    user_id = user.get("id")
    user_email = user.get("email")
    
    # Logge Löschung VOR dem Löschen
    audit_logger.log(
        event_type=AuditLogType.USER_DATA_DELETED,
        user_id=user_id,
        user_email=user_email,
        action="User account deletion request",
        ip_address=request.remote_addr,
        status="pending"
    )
    
    # Lösche Benutzer
    try:
        backend.delete_user(user_id)
        
        # Update Log Status
        audit_logger.log(
            event_type=AuditLogType.USER_DATA_DELETED,
            user_id=user_id,
            user_email=user_email,
            action="User account and data deleted",
            ip_address=request.remote_addr,
            status="success"
        )
        
        # Logout
        session.pop("user", None)
        session.pop("cart", None)
        session.modified = True
        
        flash("✓ Ihr Konto und alle persönlichen Daten wurden gelöscht.", "success")
        return redirect(url_for("index"))
    
    except Exception as e:
        audit_logger.log(
            event_type=AuditLogType.USER_DATA_DELETED,
            user_id=user_id,
            user_email=user_email,
            action=f"Account deletion failed: {str(e)}",
            ip_address=request.remote_addr,
            status="failure"
        )
        flash(f"Fehler beim Löschen des Kontos: {str(e)}", "danger")
        return redirect(url_for("gdpr_rights"))

@app.route("/preferences")
def preferences():
    """Benutzer-Präferenzen (DSGVO Widerspruchsrecht)"""
    user = session.get("user")
    if not user:
        flash("Bitte melden Sie sich an.", "danger")
        return redirect(url_for("login"))
    
    cart = session.get("cart", [])
    cart_count = get_cart_item_count(cart)
    
    return render_template("preferences.html", user=user, cart_count=cart_count)

@app.route("/profile/edit")
def profile_edit():
    """Profilbearbeitung (DSGVO Berichtigungsrecht)"""
    user = session.get("user")
    if not user:
        flash("Bitte melden Sie sich an.", "danger")
        return redirect(url_for("login"))
    
    users = backend.get_all_users()
    full_user = next((u for u in users if u.get("id") == user.get("id")), None)
    
    cart = session.get("cart", [])
    cart_count = get_cart_item_count(cart)
    
    return render_template("profile_edit.html", user=full_user, cart_count=cart_count)


# Logging für wichtige Operationen
@app.before_request
def before_request():
    """Logge alle Requests (optional, für Sicherheit)"""
    # Nur wichtige Routes loggen, um Performance nicht zu beeinträchtigen
    if request.path in ['/login', '/register', '/logout', '/cart', '/orders']:
        pass  # Wird bereits in den Routes geloggt

if __name__ == "__main__":
    app.run(debug=True)
