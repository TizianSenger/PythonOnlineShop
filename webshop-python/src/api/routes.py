# ...existing code...
import os
from flask import Blueprint, jsonify, request
from storage.csv_backend import CSVBackend
from storage.sqlite_backend import SQLiteBackend
import config

api = Blueprint('api', __name__)

# CSV-Folder: falls nicht in config angegeben, auf data/csv im Projekt-Root zurückfallen
default_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "csv"))
csv_folder = str(getattr(config, "CSV_FOLDER_PATH", default_csv))
csv_backend = CSVBackend(csv_folder)

# SQLite file: optional, falls vorhanden in config, sonst data/app.db
default_sqlite = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "app.db"))
sqlite_file = str(getattr(config, "SQLITE_FILE", default_sqlite))

# Ensure the directory exists
os.makedirs(os.path.dirname(sqlite_file), exist_ok=True)

sqlite_backend = SQLiteBackend(sqlite_file)

@api.route("/products", methods=["GET"])
def get_products():
    products = csv_backend.get_all_products()
    return jsonify(products), 200

@api.route("/register", methods=["POST"])
def register_user():
    data = request.json or {}
    user_id = csv_backend.save_user(data)
    return jsonify({"user_id": user_id}), 201

@api.route("/order", methods=["POST"])
def create_order():
    data = request.json or {}
    order_id = csv_backend.save_order(data)
    return jsonify({"order_id": order_id}), 201

# expose api under the name expected by app.py
api_bp = api
# ...existing code...