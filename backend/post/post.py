from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import os
from datetime import datetime
import psycopg2
import cloudinary
import cloudinary.uploader
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8080"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configure Cloudinary
cloudinary.config(
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key = os.getenv('CLOUDINARY_API_KEY'),
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
)

# Set maximum file size to 10MB
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB in bytes

# Database configuration
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'postdb'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'host': os.getenv('DB_HOST', 'post-db'),
    'port': os.getenv('DB_PORT', '5432')
}

def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            return psycopg2.connect(**DB_CONFIG)
        except psycopg2.OperationalError as e:
            if retries > 1:
                retries -= 1
                print(f"Could not connect to database. {retries} retries left. Error: {e}")
                time.sleep(5)  # Wait 5 seconds before retrying
            else:
                raise e

def create_tables():
    max_retries = 5
    retries = max_retries
    
    while retries > 0:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    username VARCHAR(50) NOT NULL,
                    title VARCHAR(200) NOT NULL,
                    content TEXT NOT NULL,
                    image_url VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            print("Successfully created tables!")
            return
        except Exception as e:
            if retries > 1:
                retries -= 1
                print(f"Failed to create tables. {retries} retries left. Error: {e}")
                time.sleep(5)  # Wait 5 seconds before retrying
            else:
                print(f"Final attempt to create tables failed: {e}")
                raise e
        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()

def verify_token(token):
    try:
        payload = jwt.decode(
            token,
            os.getenv('JWT_SECRET', 'esd_jwt_secret_key'),
            algorithms=[os.getenv('JWT_ALGORITHM', 'HS256')]
        )
        print("JWT Payload:", payload)  # Debug log
        return payload
    except jwt.ExpiredSignatureError:
        print("Token expired")  # Debug log
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")  # Debug log
        return None

@app.route('/api/posts', methods=['POST'])
def create_post():
    # Verify JWT token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401

    # Get form data
    title = request.form.get('title')
    content = request.form.get('content')
    
    if not all([title, content]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        image_url = None
        # Handle image upload if present
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(file)
                image_url = upload_result['secure_url']
        
        # Save post to database
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute('''
            INSERT INTO posts (user_id, username, title, content, image_url)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, title, content, image_url, created_at, username
        ''', (payload['user_id'], payload['username'], title, content, image_url))
        
        post = cur.fetchone()
        conn.commit()
        
        return jsonify({
            'message': 'Post created successfully',
            'post': {
                'id': post[0],
                'title': post[1],
                'content': post[2],
                'image_url': post[3],
                'created_at': post[4].isoformat(),
                'user_id': payload['user_id'],
                'username': post[5]
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
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
            SELECT id, title, content, image_url, created_at, user_id, username
            FROM posts
            ORDER BY created_at DESC
        ''')
        
        posts = cur.fetchall()
        
        return jsonify({
            'posts': [{
                'id': post[0],
                'title': post[1],
                'content': post[2],
                'image_url': post[3],
                'created_at': post[4].isoformat(),
                'user_id': post[5],
                'username': post[6]
            } for post in posts]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/posts/user/<int:user_id>', methods=['GET'])
def get_user_posts(user_id):
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
        # Get user's posts
        cur.execute('''
            SELECT id, title, content, image_url, created_at, user_id, username
            FROM posts
            WHERE user_id = %s
            ORDER BY created_at DESC
        ''', (user_id,))
        
        posts = cur.fetchall()
        
        # Get the username from the first post or use the token if no posts
        username = posts[0][6] if posts else payload['username']
        
        return jsonify({
            'username': username,
            'posts': [{
                'id': post[0],
                'title': post[1],
                'content': post[2],
                'image_url': post[3],
                'created_at': post[4].isoformat(),
                'user_id': post[5],
                'username': post[6]
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
