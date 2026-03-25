from flask import Flask, request, jsonify
from supabase import create_client
import bcrypt
import os

app = Flask(__name__)

# ---------------- CONFIG ----------------
URL = "https://ujclhweqqifgoiscvqmd.supabase.co"
KEY = os.getenv("SUPABASE_KEY")  # ✅ secure (from Vercel env)
TABLE = "app_users"

supabase = create_client(URL, KEY)

# ---------------- ROOT ----------------
@app.route("/")
def home():
    return jsonify({"status": "API working ✅"})


# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json(force=True)

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username & password required"}), 400

        username = username.lower().strip()

        # Check existing user
        existing = supabase.table(TABLE).select("id").eq("username", username).execute()

        if existing.data:
            return jsonify({"error": "Username already taken"}), 400

        # Hash password
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # Insert user
        insert = supabase.table(TABLE).insert({
            "username": username,
            "password": hashed
        }).execute()

        if not insert.data:
            return jsonify({"error": "User creation failed"}), 500

        return jsonify({"message": "User created successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json(force=True)

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username & password required"}), 400

        username = username.lower().strip()

        # Get user
        user = supabase.table(TABLE).select("*").eq("username", username).execute()

        if not user.data:
            return jsonify({"error": "User not found"}), 404

        stored_password = user.data[0]["password"]

        # Check password
        if not bcrypt.checkpw(password.encode(), stored_password.encode()):
            return jsonify({"error": "Wrong password"}), 401

        return jsonify({"message": "Login successful"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
