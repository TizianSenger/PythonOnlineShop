import os
import smtplib
import json
from email.message import EmailMessage
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from storage.csv_backend import CSVBackend
from api.routes import api_bp
from api.checkout_routes import checkout_bp
from config import SECRET_KEY, SMTP_USER, SMTP_PASS, ADMIN_PIN, CSV_FOLDER_PATH

# App initialisieren
app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), "templates"),
            static_folder=os.path.join(os.path.dirname(__file__), "static"))
app.secret_key = SECRET_KEY

# API unter /api bereitstellen
app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(checkout_bp)  # Checkout-Routen

# CSV-Backend initialisieren
csv_backend = CSVBackend(str(CSV_FOLDER_PATH))

# Upload-Konfiguration
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

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

    products = csv_backend.get_all_products()
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
    return render_template("index.html", products=filtered, cart_count=len(cart), categories=categories)

@app.route("/product/<product_id>")
def product_detail(product_id):
    product = csv_backend.get_product(product_id)
    if not product:
        flash("Produkt nicht gefunden.", "danger")
        return redirect(url_for("index"))
    
    product['price'] = product.get('price', '0')
    product['stock'] = product.get('stock', '0')
    product['images'] = product.get('images', [])
    
    cart = session.get("cart", [])
    return render_template("product_detail.html", product=product, cart_count=len(cart))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    role = request.form.get("role", "user")
    admin_pin = request.form.get("admin_pin", "")

    if not name or not email or not password:
        flash("Bitte alle Pflichtfelder ausfüllen.", "danger")
        return redirect(url_for("register"))

    if role == "admin" and admin_pin != ADMIN_PIN:
        flash("Falscher Admin-PIN.", "danger")
        return redirect(url_for("register"))

    users = csv_backend.get_all_users()
    if any(u.get("email", "").lower() == email for u in users):
        flash("E-Mail bereits registriert.", "danger")
        return redirect(url_for("register"))

    hashed = generate_password_hash(password)
    user = {
        "name": name,
        "email": email,
        "password": hashed,
        "role": role
    }
    user_id = csv_backend.save_user(user)
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
        return render_template("login.html")
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    users = csv_backend.get_all_users()
    user = next((u for u in users if u.get("email", "").lower() == email), None)
    if not user or not check_password_hash(user.get("password", ""), password):
        flash("Email oder Passwort falsch.", "danger")
        return redirect(url_for("login"))

    session["user"] = {"id": user.get("id"), "name": user.get("name"), "email": user.get("email"), "role": user.get("role", "user")}
    flash("Eingeloggt.", "success")
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Ausgeloggt.", "info")
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        flash("Bitte loggen Sie sich ein.", "danger")
        return redirect(url_for("login"))
    products = csv_backend.get_all_products()
    return render_template("dashboard.html", user=user, products=products)

# Warenkorb-Routes
@app.route("/cart")
def cart():
    cart_items = session.get("cart", [])
    products = csv_backend.get_all_products()
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
    return render_template("cart.html", cart=cart_with_details, total=total)

@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    data = request.get_json() or {}
    product_id = data.get("product_id")
    try:
        quantity = int(data.get("quantity", 1))
    except:
        quantity = 1

    cart = session.get("cart", [])
    existing = next((item for item in cart if item["product_id"] == product_id), None)
    if existing:
        existing["quantity"] += quantity
    else:
        cart.append({"product_id": product_id, "quantity": quantity})
    session["cart"] = cart
    session.modified = True
    return jsonify({"success": True, "cart_count": len(cart)})

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

        csv_backend.save_product(product)
        flash(f"Produkt '{name}' erfolgreich hinzugefügt.", "success")
        return redirect(url_for("admin_products"))

    products = csv_backend.get_all_products()
    return render_template("admin_products.html", user=user, products=products)

@app.route("/admin/edit-product/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    user = session.get("user")
    if not user or user.get("role") != "admin":
        flash("Zugriff verweigert.", "danger")
        return redirect(url_for("index"))

    product = csv_backend.get_product(product_id)
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
        csv_backend.update_product(product_id, updates)
        flash("Produkt aktualisiert.", "success")
        return redirect(url_for("admin_products"))

    return render_template("edit_product.html", user=user, product=product)

@app.route("/admin/delete-product/<product_id>", methods=["POST"])
def delete_product(product_id):
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return jsonify({"success": False, "error": "Zugriff verweigert"}), 403

    csv_backend.delete_product(product_id)
    flash("Produkt gelöscht.", "success")
    return redirect(url_for("admin_products"))

@app.route("/admin/remove-product-image/<product_id>/<image_name>", methods=["POST"])
def remove_product_image(product_id, image_name):
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return jsonify({"success": False, "error": "Zugriff verweigert"}), 403

    product = csv_backend.get_product(product_id)
    if not product:
        return jsonify({"success": False, "error": "Produkt nicht gefunden"}), 404

    images = product.get('images', [])
    if image_name in images:
        images.remove(image_name)
        csv_backend.update_product(product_id, {"images": images})
        # Optional: Delete file from uploads
        try:
            file_path = os.path.join(UPLOAD_FOLDER, image_name)
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        return jsonify({"success": True})
    
    return jsonify({"success": False, "error": "Bild nicht gefunden"}), 404

if __name__ == "__main__":
    app.run(debug=True)