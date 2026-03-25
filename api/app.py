from http.server import BaseHTTPRequestHandler
import json
from supabase import create_client
import bcrypt

URL = "https://ujclhweqqifgoiscvqmd.supabase.co"
KEY = "YOUR_SERVICE_ROLE_KEY"   # ⚠️ MUST change
TABLE = "app_users"

supabase = create_client(URL, KEY)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)

            path = self.path

            # ---------------- SIGNUP ----------------
            if path == "/signup":
                username = data.get("username")
                password = data.get("password")

                if not username or not password:
                    return self.send_json({"error": "Username & password required"}, 400)

                username = username.lower()

                existing = supabase.table(TABLE).select("*").eq("username", username).execute()
                if existing.data:
                    return self.send_json({"error": "Username already taken"}, 400)

                hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

                res = supabase.table(TABLE).insert({
                    "username": username,
                    "password": hashed
                }).execute()

                if not res.data:
                    return self.send_json({"error": "Insert failed"}, 500)

                return self.send_json({"message": "User created"}, 200)

            # ---------------- LOGIN ----------------
            elif path == "/login":
                username = data.get("username")
                password = data.get("password")

                if not username or not password:
                    return self.send_json({"error": "Username & password required"}, 400)

                username = username.lower()

                user = supabase.table(TABLE).select("*").eq("username", username).execute()

                if not user.data:
                    return self.send_json({"error": "User not found"}, 404)

                stored = user.data[0]["password"]

                if not bcrypt.checkpw(password.encode(), stored.encode()):
                    return self.send_json({"error": "Wrong password"}, 401)

                return self.send_json({"message": "Login successful"}, 200)

            else:
                return self.send_json({"error": "Invalid route"}, 404)

        except Exception as e:
            return self.send_json({"error": str(e)}, 500)

    def send_json(self, data, status):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
