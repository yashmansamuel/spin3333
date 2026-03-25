from flask import Flask, request, jsonify
from supabase import create_client
import bcrypt

# -------------------------
# CONFIG
# -------------------------
URL = "https://ujclhweqqifgoiscvqmd.supabase.co"
KEY = "YOUR_SERVICE_ROLE_KEY"   # ⚠️ change this
TABLE = "app_users"

# -------------------------
# INIT
# -------------------------
app = Flask(__name__)
supabase = create_client(URL, KEY)

# -------------------------
# SIGNUP
# -------------------------
@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username & password required"}), 400

        username = username.lower()

        existing = supabase.table(TABLE).select("*").eq("username", username).execute()
        if existing.data:
            return jsonify({"error": "Username already taken"}), 400

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        res = supabase.table(TABLE).insert({
            "username": username,
            "password": hashed
        }).execute()

        if not res.data:
            return jsonify({"error": "Insert failed"}), 500

        return jsonify({"message": "User created successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "Username & password required"}), 400

        username = username.lower()

        user = supabase.table(TABLE).select("*").eq("username", username).execute()

        if not user.data:
            return jsonify({"error": "User not found"}), 404

        stored = user.data[0]["password"]

        if not bcrypt.checkpw(password.encode(), stored.encode()):
            return jsonify({"error": "Wrong password"}), 401

        return jsonify({"message": "Login successful"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 👇 IMPORTANT FOR VERCEL
def handler(request, context):
    return app(request.environ, lambda status, headers: None)
