import os
from flask import Flask, request, jsonify
from supabase import create_client, Client
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Vercel Environment Variables se values uthayi jayengi
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Check karein ke keys missing to nahi
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL ya SUPABASE_KEY Environment Variables set nahi hain!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('name')

        if not email or not password or not full_name:
            return jsonify({"error": "Name, Email aur Password zaroori hain"}), 400

        # Supabase Auth Logic
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "full_name": full_name
                }
            }
        })

        if response.user:
            return jsonify({
                "status": "success",
                "message": "User successfully created!",
                "user_id": response.user.id
            }), 201
        
        return jsonify({"error": "Registration failed"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel deployment ke liye app instance
app = app
