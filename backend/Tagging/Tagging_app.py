# app.py for User Service
from flask import Flask, request, jsonify
import os
import json
import logging
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

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

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    
    # Validate required fields
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        # Hash the password
        password_hash = generate_password_hash(data['password'])
        
        # Insert user into database
        user_data = {
            'username': data['username'],
            'email': data['email'],
            'password_hash': password_hash
        }
        
        result = supabase.table('users').insert(user_data).execute()
        
        if len(result.data) == 0:
            return jsonify({"error": "Failed to create user"}), 500
            
        # Return user without password
        user = result.data[0]
        del user['password_hash']
        
        return jsonify({"message": "User created successfully", "user": user}), 201
    
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        return jsonify({"error": "Error creating user"}), 500

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        result = supabase.table('users').select('id, username, email, created_at, updated_at').eq('id', user_id).execute()
        
        if len(result.data) == 0:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify({"user": result.data[0]}), 200
    
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        return jsonify({"error": "Error fetching user"}), 500

@app.route('/users/login', methods=['POST'])
def login():
    data = request.json
    
    # Validate required fields
    if 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password required"}), 400
    
    try:
        # Fetch user by email
        result = supabase.table('users').select('*').eq('email', data['email']).execute()
        
        if len(result.data) == 0:
            return jsonify({"error": "Invalid credentials"}), 401
            
        user = result.data[0]
        
        # Check password
        if not check_password_hash(user['password_hash'], data['password']):
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Don't return password hash
        del user['password_hash']
        
        return jsonify({"message": "Login successful", "user": user}), 200
    
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({"error": "Error during login"}), 500

@app.route('/users/<user_id>/activities', methods=['POST'])
def log_activity(user_id):
    data = request.json
    
    # Validate required fields
    required_fields = ['activity_type', 'resource_id']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        # Insert activity into database
        activity_data = {
            'user_id': user_id,
            'activity_type': data['activity_type'],
            'resource_id': data['resource_id'],
            'metadata': data.get('metadata', {})
        }
        
        result = supabase.table('user_activities').insert(activity_data).execute()
        
        if len(result.data) == 0:
            return jsonify({"error": "Failed to log activity"}), 500
            
        return jsonify({"message": "Activity logged successfully", "activity": result.data[0]}), 201
    
    except Exception as e:
        logger.error(f"Error logging activity: {str(e)}")
        return jsonify({"error": "Error logging activity"}), 500

@app.route('/users/<user_id>/activities', methods=['GET'])
def get_user_activities(user_id):
    try:
        # Optional query parameters
        activity_type = request.args.get('type')
        
        query = supabase.table('user_activities').select('*').eq('user_id', user_id)
        
        if activity_type:
            query = query.eq('activity_type', activity_type)
        
        result = query.order('created_at', desc=True).execute()
        
        return jsonify({"activities": result.data}), 200
    
    except Exception as e:
        logger.error(f"Error fetching activities: {str(e)}")
        return jsonify({"error": "Error fetching activities"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)