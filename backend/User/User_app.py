from flask import Flask, request, jsonify
import os
import json
import logging
from supabase import create_client, Client
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, auth
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Initialize Firebase Admin SDK for server-side verification
# You'll need to download your Firebase service account JSON from Firebase console
cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json")
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)

# JWT Validation Middleware
def validate_firebase_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the Authorization header
        auth_header = request.headers.get('Authorization')
        
        # Check if header exists and has the right format
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization header missing or invalid"}), 401
        
        # Extract the token
        token = auth_header.split('Bearer ')[1]
        
        try:
            # Verify the token with Firebase
            decoded_token = auth.verify_id_token(token)
            
            # Add the decoded token to the request for use in route handlers
            request.firebase_user = decoded_token
            
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return jsonify({"error": "Invalid or expired token"}), 401
            
    return decorated_function

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "user-service"})


# ==============================
# USER REGISTRATION (CREATE)
# ==============================
@app.route('/api/user/register', methods=['POST'])
@validate_firebase_token
def register_user():
    data = request.json
    firebase_user = request.firebase_user
    
    # Validate that the Firebase UID matches the one in the token
    if data.get("uid") != firebase_user["uid"]:
        return jsonify({"error": "UID mismatch between token and request"}), 403

    # Validate required fields
    required_fields = ["uid", "email"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        # Check if user already exists
        check_result = supabase.table("users").select("*").eq("user_id", data["uid"]).execute()
        
        if len(check_result.data) > 0:
            return jsonify({"message": "User already exists", "user": check_result.data[0]}), 200
            
        # Insert new user into database
        user_data = {
            "user_id": data["uid"],  # Using user_id to match your Supabase column
            "email": data["email"],
            "username": data.get("username", data["email"].split("@")[0]),  # Default to part of email if not provided
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "display_name": data.get("display_name", ""),
            "dark_mode": data.get("dark_mode", False)
        }
        
        result = supabase.table("users").insert(user_data).execute()

        if len(result.data) == 0:
            return jsonify({"error": "Failed to register user"}), 500

        return jsonify({"message": "User registered successfully", "user": result.data[0]}), 201

    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({"error": f"Error registering user: {str(e)}"}), 500


# ==============================
# USER LOGIN (JWT Validated by Firebase)
# ==============================
@app.route("/api/user/login", methods=["POST"])
@validate_firebase_token
def user_login():
    # Get UID from the validated Firebase token
    uid = request.firebase_user["uid"]
    
    try:
        # Check if the user exists in Supabase
        result = supabase.table("users").select("*").eq("user_id", uid).execute()

        if len(result.data) == 0:
            # User authenticated with Firebase but not in Supabase
            # This is a good place to auto-create the user in Supabase
            user_data = {
                "user_id": uid,
                "email": request.firebase_user["email"],
                "username": request.firebase_user.get("email", "").split("@")[0],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "display_name": request.firebase_user.get("name", ""),
                "dark_mode": False
            }
            
            new_user = supabase.table("users").insert(user_data).execute()
            
            if len(new_user.data) == 0:
                return jsonify({"error": "Failed to create user record"}), 500
                
            return jsonify({"message": "User profile created", "user": new_user.data[0]}), 201

        return jsonify({"message": "Login successful", "user": result.data[0]}), 200

    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({"error": f"Error during login: {str(e)}"}), 500


# ==============================
# GET USER INFO (READ)
# ==============================
@app.route("/api/user/<uid>", methods=["GET"])
@validate_firebase_token
def get_user(uid):
    # Ensure user can only access their own data
    if uid != request.firebase_user["uid"]:
        # You can comment this out if you want admins to access any user
        return jsonify({"error": "Unauthorized access"}), 403
        
    try:
        result = supabase.table("users").select("*").eq("user_id", uid).execute()

        if len(result.data) == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"user": result.data[0]}), 200

    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        return jsonify({"error": f"Error fetching user: {str(e)}"}), 500


# ==============================
# UPDATE USER INFO (UPDATE)
# ==============================
@app.route("/api/user/<uid>", methods=["PUT"])
@validate_firebase_token
def update_user(uid):
    # Ensure user can only update their own data
    if uid != request.firebase_user["uid"]:
        return jsonify({"error": "Unauthorized access"}), 403
        
    data = request.json
    
    if not data:
        return jsonify({"error": "No update data provided"}), 400
    
    try:
        # Check if user exists
        check_result = supabase.table("users").select("*").eq("user_id", uid).execute()
        
        if len(check_result.data) == 0:
            return jsonify({"error": "User not found"}), 404
        
        # Update timestamp
        data["updated_at"] = datetime.now().isoformat()
        
        # Remove any attempt to change user_id
        if "user_id" in data:
            del data["user_id"]
            
        # Update user information
        result = supabase.table("users").update(data).eq("user_id", uid).execute()
        
        if len(result.data) == 0:
            return jsonify({"error": "Failed to update user"}), 500
            
        return jsonify({"message": "User updated successfully", "user": result.data[0]}), 200
        
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        return jsonify({"error": f"Error updating user: {str(e)}"}), 500


# ==============================
# DELETE USER (DELETE)
# ==============================
@app.route("/api/user/<uid>", methods=["DELETE"])
@validate_firebase_token
def delete_user(uid):
    # Ensure user can only delete their own account
    if uid != request.firebase_user["uid"]:
        return jsonify({"error": "Unauthorized access"}), 403
        
    try:
        # Check if user exists
        check_result = supabase.table("users").select("*").eq("user_id", uid).execute()
        
        if len(check_result.data) == 0:
            return jsonify({"error": "User not found"}), 404
            
        # Delete the user
        result = supabase.table("users").delete().eq("user_id", uid).execute()
        
        if len(result.data) == 0:
            return jsonify({"error": "Failed to delete user"}), 500
            
        return jsonify({"message": "User deleted successfully"}), 200
        
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        return jsonify({"error": f"Error deleting user: {str(e)}"}), 500


# ==============================
# LIST ALL USERS - Admin only endpoint
# ==============================
@app.route("/api/users", methods=["GET"])
@validate_firebase_token
def list_users():
    # This should be restricted to admin users only
    # You would need to add admin role verification here
    # For now, we're keeping it simple
    
    try:
        # Optional pagination parameters
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)
        
        result = supabase.table("users").select("*").limit(limit).offset(offset).execute()
        
        return jsonify({"users": result.data, "count": len(result.data)}), 200
        
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        return jsonify({"error": f"Error listing users: {str(e)}"}), 500


# ==============================
# SYNC FIREBASE USER TO SUPABASE
# ==============================
@app.route("/api/user/sync", methods=["POST"])
@validate_firebase_token
def sync_firebase_user():
    # Get user data from the validated Firebase token
    uid = request.firebase_user["uid"]
    email = request.firebase_user["email"]
    
    # Additional data can come from the request body
    data = request.json or {}
    
    try:
        # Check if user already exists in Supabase
        check_result = supabase.table("users").select("*").eq("user_id", uid).execute()
        
        # If user exists, just return success
        if len(check_result.data) > 0:
            return jsonify({"message": "User already synchronized", "user": check_result.data[0]}), 200
            
        # Create new user record in Supabase
        user_data = {
            "user_id": uid,
            "email": email,
            "username": data.get("username", email.split("@")[0]),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "display_name": data.get("display_name", ""),
            "dark_mode": data.get("dark_mode", False)
        }
        
        result = supabase.table("users").insert(user_data).execute()
        
        if len(result.data) == 0:
            return jsonify({"error": "Failed to sync user"}), 500
            
        return jsonify({"message": "User synchronized successfully", "user": result.data[0]}), 201
        
    except Exception as e:
        logger.error(f"Error syncing user: {str(e)}")
        return jsonify({"error": f"Error syncing user: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
