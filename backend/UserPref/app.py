from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from supabase import create_client, Client
from postgrest.exceptions import APIError
import os
from datetime import datetime

app = Flask(__name__, static_folder='static')
CORS(app)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Serve the HTML form
@app.route('/')
def serve_home():
    return send_from_directory(app.static_folder, 'user_preference.html')


# Submit user preferences (with JWT-based user ID)
@app.route('/submit', methods=['POST'])
def submit():
    
    uid = request.get_json().get('uid')
    user_pref = request.get_json().get('user_pref')

    if not user_pref:
        return jsonify({"error": "Missing user_pref data"}), 400

    try:
        # Update row in 'users' table where userId matches uid
        result = supabase.table('users').update({
            "taste_preferen": user_pref,
            "updated_at": datetime.now().isoformat()
        }).eq("userId", uid).execute()

        return jsonify({"message": "Preferences saved successfully."}), 200

    except APIError as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
