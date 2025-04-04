from flask import Flask, request, jsonify
import os
import json
import logging
from supabase import create_client, Client
from datetime import datetime
import jwt
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(name)

app = Flask(name)

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# JWT secret key - should match the one used by authentication service
JWT_SECRET = os.environ.get("JWT_SECRET")

# JWT Validation Middleware
def validate_jwt_token(f):
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
            # Verify the token
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            
            # Add the decoded token to the request for use in route handlers
            request.user = decoded_token
            
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return jsonify({"error": "Invalid or expired token"}), 401
            
    return decorated_function

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "user-service"})


# ==============================
# USER CREATION (Internal API for Auth Service)
# ==============================
@app.route('/api/internal/user/create', methods=['POST'])
def create_user():
    """
    Internal API endpoint for the authentication service to call after creating a user.
    This endpoint should only be accessible by the authentication service,
    not directly by clients.
    """
    # In production, add additional security like API keys or internal network restrictions
    data = request.json
    
    # Validate required fields
    required_fields = ["user_id", "email"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        # Check if user already exists
        check_result = supabase.table("users").select("*").eq("user_id", data["user_id"]).execute()
        
        if len(check_result.data) > 0:
            return jsonify({"message": "User already exists", "user": check_result.data[0]}), 200
            
        # Insert new user into database with minimal information
        user_data = {
            "user_id": data["user_id"],
            "email": data["email"],
            "username": data.get("username", data["email"].split("@")[0]),  # Default to part of email
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        result = supabase.table("users").insert(user_data).execute()

        if len(result.data) == 0:
            return jsonify({"error": "Failed to create user"}), 500

        return jsonify({"message": "User created successfully", "user": result.data[0]}), 201

    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return jsonify({"error": f"Error creating user: {str(e)}"}), 500
    
# ==============================
# GET USER INFO (READ)
# ==============================
@app.route("/api/user/<user_id>", methods=["GET"])
@validate_jwt_token
def get_user(user_id):
    # Ensure user can only access their own data
    if user_id != request.user["sub"]:  # 'sub' is standard JWT claim for subject (user ID)
        return jsonify({"error": "Unauthorized access"}), 403
        
    try:
        result = supabase.table("users").select("*").eq("user_id", user_id).execute()

        if len(result.data) == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"user": result.data[0]}), 200

    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        return jsonify({"error": f"Error fetching user: {str(e)}"}), 500


# ==============================
# UPDATE USER INFO (UPDATE)
# ==============================
@app.route("/api/user/<user_id>", methods=["PUT"])
@validate_jwt_token
def update_user(user_id):
    # Ensure user can only update their own data
    if user_id != request.user["sub"]:
        return jsonify({"error": "Unauthorized access"}), 403
        
    data = request.json
    
    if not data:
        return jsonify({"error": "No update data provided"}), 400
    
    try:
        # Check if user exists
        check_result = supabase.table("users").select("*").eq("user_id", user_id).execute()
        
        if len(check_result.data) == 0:
            return jsonify({"error": "User not found"}), 404
        
        # Update timestamp
        data["updated_at"] = datetime.now().isoformat()
        
        # Remove any attempt to change user_id
        if "user_id" in data:
            del data["user_id"]
            
        # Update user information
        result = supabase.table("users").update(data).eq("user_id", user_id).execute()
        
        if len(result.data) == 0:
            return jsonify({"error": "Failed to update user"}), 500
            
        return jsonify({"message": "User updated successfully", "user": result.data[0]}), 200
        
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        return jsonify({"error": f"Error updating user: {str(e)}"}), 500


# ==============================
# DELETE USER (DELETE)
# ==============================
@app.route("/api/user/<user_id>", methods=["DELETE"])
@validate_jwt_token
def delete_user(user_id):
    # Ensure user can only delete their own account
    if user_id != request.user["sub"]:
        return jsonify({"error": "Unauthorized access"}), 403
        
    try:
        # Check if user exists
        check_result = supabase.table("users").select("*").eq("user_id", user_id).execute()
        
        if len(check_result.data) == 0:
            return jsonify({"error": "User not found"}), 404
            
        # Delete the user
        result = supabase.table("users").delete().eq("user_id", user_id).execute()
        
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
@validate_jwt_token
def list_users():
    # This should be restricted to admin users only
    # Check if user has admin role in the JWT
    if not request.user.get("roles", []) or "admin" not in request.user.get("roles", []):
        return jsonify({"error": "Unauthorized. Admin access required"}), 403
    
    try:
        # Optional pagination parameters
        limit = request.args.get("limit", 100, type=int)
        offset = request.args.get("offset", 0, type=int)
        
        result = supabase.table("users").select("*").limit(limit).offset(offset).execute()
        
        return jsonify({"users": result.data, "count": len(result.data)}), 200
        
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        return jsonify({"error": f"Error listing users: {str(e)}"}), 500


if name == 'main':
    app.run(host='0.0.0.0', port=5001, debug=True)