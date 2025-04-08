from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import os
from datetime import datetime
import time
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
from supabase import create_client, Client

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

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL", "your-supabase-url")
supabase_key = os.environ.get("SUPABASE_KEY", "your-supabase-anon-key")
supabase: Client = create_client(supabase_url, supabase_key)

# Define the table name for posts
POSTS_TABLE = "post"

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
    location = request.form.get('location')
    preferences = request.form.get('preferences')  # Might be comma-separated

    
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
        
        # Create post data object
        post_data = {
            'user_id': payload['user_id'],
            'username': payload['username'],
            'title': title,
            'content': content,
            'location': location,
            'preferences': preferences,
            'image_url': image_url,
            'created_at': datetime.now().isoformat()
        }
        
        # Insert data into Supabase
        response = supabase.table(POSTS_TABLE).insert(post_data).execute()
        
        # Get the created post from the response
        new_post = response.data[0]
        
        return jsonify({
            'message': 'Post created successfully',
            'post': {
                'id': new_post['id'],
                'title': new_post['title'],
                'content': new_post['content'],
                'image_url': new_post['image_url'],
                'created_at': new_post['created_at'],
                'user_id': new_post['user_id'],
                'username': new_post['username']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts', methods=['GET'])
def get_posts():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    try:
        # Query posts from Supabase
        response = supabase.table(POSTS_TABLE).select('*').order('created_at', desc=True).execute()
        
        posts = response.data
        
        return jsonify({
            'posts': [{
                'id': post['id'],
                'title': post['title'],
                'content': post['content'],
                'image_url': post['image_url'],
                'created_at': post['created_at'],
                'user_id': post['user_id'],
                'username': post['username'],
                'preference': [tag.strip() for tag in (post['preferences'] or '').split(',') if tag],
                'location': post['location']
            } for post in posts]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/user/<int:user_id>', methods=['GET'])
def get_user_posts(user_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401
    
    try:
        # Query user's posts from Supabase
        response = supabase.table(POSTS_TABLE).select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        
        posts = response.data
        
        # Get the username from the first post or use the token if no posts
        username = posts[0]['username'] if posts else payload['username']
        
        return jsonify({
            'username': username,
            'posts': [{
                'id': post['id'],
                'title': post['title'],
                'content': post['content'],
                'image_url': post['image_url'],
                'created_at': post['created_at'],
                'user_id': post['user_id'],
                'username': post['username']
            } for post in posts]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    # Verify JWT token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401

    try:
        # First, get the post to check ownership
        post_response = supabase.table(POSTS_TABLE).select('*').eq('id', post_id).execute()
        
        if not post_response.data:
            return jsonify({'error': 'Post not found'}), 404
        
        post = post_response.data[0]
        
        # Check if the user is the owner of the post
        if post['user_id'] != payload['user_id']:
            return jsonify({'error': 'Unauthorized to update this post'}), 403
        
        # Get form data
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not all([title, content]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Prepare update data
        update_data = {
            'title': title,
            'content': content,
            'updated_at': datetime.now().isoformat()
        }
        
        # Handle image upload if present
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(file)
                update_data['image_url'] = upload_result['secure_url']
        
        # Update post in Supabase
        response = supabase.table(POSTS_TABLE).update(update_data).eq('id', post_id).execute()
        
        updated_post = response.data[0]
        
        return jsonify({
            'message': 'Post updated successfully',
            'post': {
                'id': updated_post['id'],
                'title': updated_post['title'],
                'content': updated_post['content'],
                'image_url': updated_post['image_url'],
                'created_at': updated_post['created_at'],
                'updated_at': updated_post.get('updated_at'),
                'user_id': updated_post['user_id'],
                'username': updated_post['username']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    # Verify JWT token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    
    if not payload:
        return jsonify({'error': 'Invalid or expired token'}), 401

    try:
        # First, get the post to check ownership
        post_response = supabase.table(POSTS_TABLE).select('*').eq('id', post_id).execute()
        
        if not post_response.data:
            return jsonify({'error': 'Post not found'}), 404
        
        post = post_response.data[0]
        
        # Check if the user is the owner of the post
        if post['user_id'] != payload['user_id']:
            return jsonify({'error': 'Unauthorized to delete this post'}), 403
        
        # Delete the post from Supabase
        supabase.table(POSTS_TABLE).delete().eq('id', post_id).execute()
        
        return jsonify({
            'message': 'Post deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)