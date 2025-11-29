import json
from flask import Blueprint, render_template, request, session, redirect, url_for, current_app, flash
from services.checkout import create_stripe_session, create_paypal_order, capture_paypal_order, save_order
from storage.csv_backend import CSVBackend
from config import STRIPE_PUBLISHABLE_KEY, APP_BASE_URL, CSV_FOLDER_PATH

checkout_bp = Blueprint("checkout_bp", __name__, template_folder="../templates")

csv_backend = CSVBackend(str(CSV_FOLDER_PATH))

@checkout_bp.route("/checkout", methods=["GET"])
def checkout_page():
    cart_items = session.get("cart", [])
    products = csv_backend.get_all_products()
    cart = []
    total = 0.0
    for item in cart_items:
        p = next((x for x in products if x.get("id") == item["product_id"]), None)
        if p:
            price = float(p.get("price", 0))
            qty = int(item.get("quantity", 1))
            # try to get a product image if available
            main_image = ''
            images = p.get('images') or []
            if isinstance(images, list) and len(images) > 0:
                main_image = images[0]
            cart.append({"id": p.get("id"), "name": p.get("name"), "price": price, "quantity": qty, "_image": main_image})
            total += price * qty

    # prefill user info if logged in
    user = session.get("user")

    return render_template(
        "checkout.html",
        cart=cart,
        total=total,
        stripe_key=STRIPE_PUBLISHABLE_KEY,
        user=user
    )

@checkout_bp.route("/checkout/create", methods=["POST"])
def create_checkout():
    # Check if user is logged in
    user = session.get("user")
    if not user:
        flash("Bitte melden Sie sich an, um eine Bestellung zu erstellen.", "danger")
        return redirect(url_for("checkout_bp.checkout_page"))
    
    data = request.form.to_dict()
    payment_method = data.get("payment_method", "stripe")
    # Collect customer info
    customer = {
        "name": data.get("name", ""),
        "email": data.get("email", ""),
        "address": data.get("address", ""),
        "city": data.get("city", ""),
        "zip": data.get("zip", ""),
        "country": data.get("country", "")
    }
    # Build cart items details
    cart_items = []
    products = csv_backend.get_all_products()
    for item in session.get("cart", []):
        p = next((x for x in products if x.get("id") == item["product_id"]), None)
        if p:
            cart_items.append({"product_id": p.get("id"), "name": p.get("name"), "price": float(p.get("price", 0)), "quantity": int(item.get("quantity",1))})
    success_url = f"{APP_BASE_URL}/checkout/success"
    cancel_url = f"{APP_BASE_URL}/checkout/cancel"

    try:
        if payment_method == "stripe":
            session_url, order_id = create_stripe_session(csv_backend, cart_items, customer, success_url, cancel_url, user.get("id"))
            return redirect(session_url)
        elif payment_method == "paypal":
            approve_url, order_id = create_paypal_order(csv_backend, cart_items, customer, f"{APP_BASE_URL}/api/checkout/paypal-return", cancel_url, user.get("id"))
            return redirect(approve_url)
        else:
            flash("Unbekannte Zahlungsart", "danger")
            return redirect(url_for("checkout_bp.checkout_page"))
    except Exception as e:
        current_app.logger.exception("Payment error")
        flash("Fehler bei der Zahlung: " + str(e), "danger")
        return redirect(url_for("checkout_bp.checkout_page"))

@checkout_bp.route("/checkout/success")
def checkout_success():
    # Stripe returns session_id & order_id
    session_id = request.args.get("session_id")
    order_id = request.args.get("order_id")
    # Try to mark order as paid (we could verify with Stripe API)
    orders = csv_backend.get_all_orders()
    for o in orders:
        if o.get("id") == order_id:
            o["status"] = "paid"
    csv_backend.write_csv('orders.csv', orders, fieldnames=['id','user_id','items','total','customer','status','payment_provider','provider_id','created_at'])
    # Clear cart
    session.pop("cart", None)
    # Render confirmation
    return render_template("confirmation.html", order_id=order_id, paid=True)

@checkout_bp.route("/checkout/cancel")
def checkout_cancel():
    flash("Zahlung abgebrochen.", "info")
    return redirect(url_for("cart"))

@checkout_bp.route("/api/checkout/paypal-return")
def paypal_return():
    token = request.args.get("token")
    # Capture order
    try:
        capture_paypal_order(csv_backend, token)
        # find local order and mark paid
        orders = csv_backend.get_all_orders()
        local_order = next((o for o in orders if o.get("provider_id") == token), None)
        if local_order:
            local_order["status"] = "paid"
            csv_backend.write_csv('orders.csv', orders, fieldnames=['id','user_id','items','total','customer','status','payment_provider','provider_id','created_at'])
        session.pop("cart", None)
        return render_template("confirmation.html", order_id=(local_order and local_order.get("id")), paid=True)
    except Exception as e:
        current_app.logger.exception("PayPal capture failed")
        flash("PayPal Zahlung fehlgeschlagen: " + str(e), "danger")
        return redirect(url_for("checkout_bp.checkout_page"))