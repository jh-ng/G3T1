from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import os
import requests
from datetime import datetime, timedelta
from supabase import create_client, Client
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:8080"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL", "your-supabase-url")
supabase_key = os.environ.get("SUPABASE_KEY", "your-supabase-anon-key")
supabase: Client = create_client(supabase_url, supabase_key)

# Define the table name for authentication
AUTHENTICATION_TABLE = "users"

# Kong API Gateway URL (adjust as needed)
KONG_URL = os.environ.get("KONG_URL", "http://localhost:8000")

# User Registration (POST)
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Check if username or email already exists
        response = supabase.table(AUTHENTICATION_TABLE).select('username, email').or_(
            f"username.eq.{data['username']},email.eq.{data['email']}"
        ).execute()
        
        if response.data:
            return jsonify({'error': 'Username or email already exists'}), 400
        
        # Hash password
        password_hash = generate_password_hash(data['password'])
        
        # Insert new user in auth database
        response = supabase.table(AUTHENTICATION_TABLE).insert({
            "username": data['username'],
            "email": data['email'],
            "password_hash": password_hash
        }).execute()
        
        if not response.data:
            return jsonify({'error': 'Failed to register user'}), 500
            
        user = response.data[0]
        
        # Now create a user record in the user service through Kong
        try:
            # Prepare the data to send to user service
            user_data = {
                "user_id": user['id'],
                "email": user['email'],
                "username": user['username']
            }
            
            # Send request to user service through Kong
            user_service_response = requests.post(
                f"{KONG_URL}/api/internal/user/create",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Check if user creation in user service was successful
            if user_service_response.status_code not in (200, 201):
                # If user service fails, we should log this but still return success
                # as the auth part worked
                print(f"Warning: User service creation failed: {user_service_response.text}")
        
        except Exception as e:
            # Log error but don't fail the registration if user service is unavailable
            print(f"Error creating user in user service: {str(e)}")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'created_at': user['created_at']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Login & JWT Token Generation (POST)
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(k in data for k in ['username', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Get user by username
        response = supabase.table(AUTHENTICATION_TABLE).select('id, username, password_hash').eq(
            'username', data['username']
        ).execute()
        
        if not response.data:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user = response.data[0]
        
        # Verify password
        if not check_password_hash(user['password_hash'], data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        token = jwt.encode(
            {
                'user_id': user['id'],
                'username': user['username'],
                'exp': datetime.utcnow() + timedelta(days=1)
            },
            os.getenv('JWT_SECRET', 'esd_jwt_secret_key'),
            algorithm=os.getenv('JWT_ALGORITHM', 'HS256')
        )
        
        return jsonify({
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Verify JWT Token (GET)
@app.route('/api/auth/verify-token', methods=['GET'])
def verify_token():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(
            token,
            os.getenv('JWT_SECRET', 'esd_jwt_secret_key'),
            algorithms=[os.getenv('JWT_ALGORITHM', 'HS256')]
        )
        return jsonify({'valid': True, 'user': payload}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)