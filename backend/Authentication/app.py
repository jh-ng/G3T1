from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import os
from datetime import datetime, timedelta
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'authdb'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'host': os.getenv('DB_HOST', 'auth-db'),
    'port': '5432'
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(200) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Check if username or email already exists
        cur.execute('SELECT username, email FROM users WHERE username = %s OR email = %s',
                   (data['username'], data['email']))
        if cur.fetchone():
            return jsonify({'error': 'Username or email already exists'}), 400
        
        # Hash password and insert user
        password_hash = generate_password_hash(data['password'])
        cur.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id, username, email
        ''', (data['username'], data['email'], password_hash))
        
        user = cur.fetchone()
        conn.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': user[0],
                'username': user[1],
                'email': user[2]
            }
        }), 201
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(k in data for k in ['username', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('SELECT id, username, password_hash FROM users WHERE username = %s',
                   (data['username'],))
        user = cur.fetchone()
        
        if not user or not check_password_hash(user[2], data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        token = jwt.encode(
            {
                'user_id': user[0],
                'username': user[1],
                'exp': datetime.utcnow() + timedelta(days=1)
            },
            os.getenv('JWT_SECRET', 'your-secret-key-here'),
            algorithm=os.getenv('JWT_ALGORITHM', 'HS256')
        )
        
        return jsonify({
            'token': token,
            'user': {
                'id': user[0],
                'username': user[1]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/auth/verify-token', methods=['GET'])
def verify_token():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    
    try:
        payload = jwt.decode(
            token,
            os.getenv('JWT_SECRET', 'your-secret-key-here'),
            algorithms=[os.getenv('JWT_ALGORITHM', 'HS256')]
        )
        return jsonify({'valid': True, 'user': payload}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5001) 