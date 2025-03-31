from flask import Flask, request, jsonify
import os
import json
import logging
from supabase import create_client, Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "user-service"})


# ==============================
# USER REGISTRATION
# ==============================
@app.route('/api/user/register', methods=['POST'])
def register_user():
    data = request.json

    # Validate required fields
    required_fields = ["uid", "email", "name"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        # Insert new user into database
        user_data = {
            "uid": data["uid"],
            "email": data["email"],
            "name": data["name"]
        }
        result = supabase.table("users").insert(user_data).execute()

        if len(result.data) == 0:
            return jsonify({"error": "Failed to register user"}), 500

        return jsonify({"message": "User registered successfully", "user": result.data[0]}), 201

    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({"error": "Error registering user"}), 500


# ==============================
# USER LOGIN (JWT Validated by Kong)
# ==============================
@app.route("/api/user/login", methods=["POST"])
def user_login():
    uid = request.json.get("uid")
    email = request.json.get("email")

    try:
        # Check if the user exists
        result = supabase.table("users").select("*").eq("uid", uid).execute()

        if len(result.data) == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": "Login successful", "user": result.data[0]}), 200

    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({"error": "Error during login"}), 500


# ==============================
# GET USER INFO
# ==============================
@app.route("/api/user/<uid>", methods=["GET"])
def get_user(uid):
    try:
        result = supabase.table("users").select("*").eq("uid", uid).execute()

        if len(result.data) == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"user": result.data[0]}), 200

    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        return jsonify({"error": "Error fetching user"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
