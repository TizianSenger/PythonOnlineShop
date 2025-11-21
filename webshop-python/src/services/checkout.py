import json
import time
import requests
from datetime import datetime

import stripe

from config import STRIPE_SECRET_KEY, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_MODE, APP_BASE_URL
from storage.csv_backend import CSVBackend

csv_backend = CSVBackend(str((__import__("config").config.CSV_FOLDER_PATH) if False else str(__import__("config").CSV_FOLDER_PATH)) if False else str(__import__("config").CSV_FOLDER_PATH) )  # placeholder not used

# Initialize stripe
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Helper: get PayPal base URL
def paypal_base():
    return "https://api-m.sandbox.paypal.com" if PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com"

def save_order(csv_backend, order):
    """order: dict with keys: items(list), total(float), customer(dict), status, payment_provider, provider_id"""
    # Prepare order dict
    now = datetime.utcnow().isoformat()
    order_obj = {
        "user_id": order.get("user_id", ""),
        "items": json.dumps(order.get("items", []), ensure_ascii=False),
        "total": str(order.get("total", "0")),
        "customer": json.dumps(order.get("customer", {}), ensure_ascii=False),
        "status": order.get("status", "pending"),
        "payment_provider": order.get("payment_provider", ""),
        "provider_id": order.get("provider_id", ""),
        "created_at": now
    }
    return csv_backend.save_order(order_obj)

def create_stripe_session(csv_backend, cart_items, customer, success_url, cancel_url):
    if not stripe.api_key:
        raise RuntimeError("Stripe API key not configured")

    line_items = []
    total = 0.0
    for it in cart_items:
        price = float(it.get("price", 0))
        qty = int(it.get("quantity", 1))
        total += price * qty
        line_items.append({
            "price_data": {
                "currency": "eur",
                "product_data": {"name": it.get("name", "Produkt")},
                "unit_amount": int(price * 100)
            },
            "quantity": qty
        })

    # create order record first (pending)
    order = {
        "items": cart_items,
        "total": total,
        "customer": customer,
        "status": "pending",
        "payment_provider": "stripe",
        "provider_id": ""
    }
    order_id = save_order(csv_backend, order)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}&order_id={order_id}",
        cancel_url=cancel_url,
        metadata={"order_id": order_id}
    )
    # store provider id (session id) in order
    csv_backend.update_product  # noop to avoid lint
    # update order with provider id
    orders = csv_backend.get_all_orders()
    # find and update
    for o in orders:
        if o.get("id") == order_id:
            o["provider_id"] = session.id
            o["payment_provider"] = "stripe"
            o["status"] = "pending"
    csv_backend.write_csv('orders.csv', orders, fieldnames=['id','user_id','items','total','customer','status','payment_provider','provider_id','created_at'])
    return session.url, order_id

def create_paypal_order(csv_backend, cart_items, customer, return_url, cancel_url):
    # Get access token
    token_resp = requests.post(f"{paypal_base()}/v1/oauth2/token",
                               auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
                               headers={"Accept": "application/json"},
                               data={"grant_type": "client_credentials"})
    token_resp.raise_for_status()
    access_token = token_resp.json()['access_token']

    total = 0.0
    purchase_items = []
    for it in cart_items:
        price = float(it.get("price", 0))
        qty = int(it.get("quantity", 1))
        total += price * qty
        purchase_items.append({
            "name": it.get("name", "Produkt"),
            "unit_amount": {"currency_code": "EUR", "value": f"{price:.2f}"},
            "quantity": str(qty)
        })

    order_payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "EUR",
                "value": f"{total:.2f}",
                "breakdown": {
                    "item_total": {"currency_code": "EUR", "value": f"{total:.2f}"}
                }
            },
            "items": purchase_items
        }],
        "application_context": {
            "return_url": return_url,
            "cancel_url": cancel_url
        }
    }

    # create order record first (pending)
    order = {
        "items": cart_items,
        "total": total,
        "customer": customer,
        "status": "pending",
        "payment_provider": "paypal",
        "provider_id": ""
    }
    order_id = save_order(csv_backend, order)

    resp = requests.post(f"{paypal_base()}/v2/checkout/orders",
                         json=order_payload,
                         headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"})
    resp.raise_for_status()
    data = resp.json()
    provider_id = data.get("id")
    # update order provider id
    orders = csv_backend.get_all_orders()
    for o in orders:
        if o.get("id") == order_id:
            o["provider_id"] = provider_id
    csv_backend.write_csv('orders.csv', orders, fieldnames=['id','user_id','items','total','customer','status','payment_provider','provider_id','created_at'])
    # Find approval link
    approve = next((l['href'] for l in data.get("links", []) if l.get("rel") == "approve"), None)
    return approve, order_id

def capture_paypal_order(csv_backend, provider_order_id):
    # capture PayPal order
    token_resp = requests.post(f"{paypal_base()}/v1/oauth2/token",
                               auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
                               headers={"Accept": "application/json"},
                               data={"grant_type": "client_credentials"})
    token_resp.raise_for_status()
    access_token = token_resp.json()['access_token']

    resp = requests.post(f"{paypal_base()}/v2/checkout/orders/{provider_order_id}/capture",
                         headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"})
    resp.raise_for_status()
    # mark order paid
    orders = csv_backend.get_all_orders()
    for o in orders:
        if o.get("provider_id") == provider_order_id:
            o["status"] = "paid"
    csv_backend.write_csv('orders.csv', orders, fieldnames=['id','user_id','items','total','customer','status','payment_provider','provider_id','created_at'])
    return True

class CheckoutService:
    def __init__(self, storage_backend):
        self.storage_backend = storage_backend

    def process_order(self, user_id, product_id, quantity):
        order = {
            'user_id': user_id,
            'product_id': product_id,
            'quantity': quantity
        }
        self.storage_backend.save_order(order)
        return order

    def calculate_total(self, product_id, quantity):
        product = self.storage_backend.get_product(product_id)
        if product:
            return product['price'] * quantity
        return None

    def handle_payment(self, order, payment_info):
        # Here you would integrate with a payment gateway
        # For now, we'll just simulate a successful payment
        return True if payment_info.get('valid') else False

    def complete_checkout(self, user_id, product_id, quantity, payment_info):
        order = self.process_order(user_id, product_id, quantity)
        total = self.calculate_total(product_id, quantity)
        if self.handle_payment(order, payment_info):
            return {
                'status': 'success',
                'order': order,
                'total': total
            }
        return {
            'status': 'failed',
            'order': order,
            'total': total
        }