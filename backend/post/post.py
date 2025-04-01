from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import os
from datetime import datetime
import psycopg2

app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'postgres',
    'port': '5432'
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

def verify_token(token):
    try:
        payload = jwt.decode(
            token,
            os.getenv('JWT_SECRET', 'your-secret-key-here'),
            algorithms=[os.getenv('JWT_ALGORITHM', 'HS256')]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route('/api/posts', methods=['POST'])
def create_post():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    data = request.get_json()
    if not all(k in data for k in ['title', 'content']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('''
            INSERT INTO posts (user_id, title, content)
            VALUES (%s, %s, %s)
            RETURNING id, title, content, created_at
        ''', (payload['user_id'], data['title'], data['content']))
        
        post = cur.fetchone()
        conn.commit()
        
        return jsonify({
            'message': 'Post created successfully',
            'post': {
                'id': post[0],
                'title': post[1],
                'content': post[2],
                'created_at': post[3].isoformat(),
                'user_id': payload['user_id']
            }
        }), 201
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/posts', methods=['GET'])
def get_posts():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute('''
            SELECT id, title, content, created_at, user_id
            FROM posts
            ORDER BY created_at DESC
        ''')
        
        posts = cur.fetchall()
        
        return jsonify({
            'posts': [{
                'id': post[0],
                'title': post[1],
                'content': post[2],
                'created_at': post[3].isoformat(),
                'user_id': post[4]
            } for post in posts]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=5000)
