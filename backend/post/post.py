from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from uuid import uuid4
from datetime import datetime
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

# Load env variables
load_dotenv()

# Init Flask app
app = Flask(__name__)

CORS(app)

# Setup DB (adjust connection string to your DB)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:root@post-db:5432/postdb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# create table from post
with app.app_context():
    db.create_all()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# DB model
class Post(db.Model):
    post_id = db.Column(db.String, primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String, nullable=False)
    content = db.Column(db.Text)
    image_urls = db.Column(db.Text)  # Store as comma-separated URLs
    created_at = db.Column(db.DateTime, default=datetime.now)

# Routes
@app.route('/create-post', methods=['POST'])
def create_post():
    user_id = request.form['user_id']
    content = request.form.get('content', '')
    images = request.files.getlist('images')

    # Upload images
    image_urls = []
    for img in images:
        result = cloudinary.uploader.upload(img)
        image_urls.append(result['secure_url'])

    # Store post in DB
    post = Post(
        user_id=user_id,
        content=content,
        image_urls=','.join(image_urls)
    )
    db.session.add(post)
    db.session.commit()

    return jsonify({
        'code': 201,
        'message': 'Post created successfully.',
        'data': {
            'post_id': post.post_id,
            'image_urls': image_urls
        }
    }), 201

# Get all posts
@app.route('/posts', methods=['GET'])
def get_all_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    result = []
    for post in posts:
        result.append({
            'post_id': post.post_id,
            'user_id': post.user_id,
            'content': post.content,
            'image_urls': post.image_urls.split(','),
            'created_at': post.created_at.isoformat()
        })
    return jsonify({
        'code': 200,
        'message': 'Posts retrieved successfully.',
        'data': result
    }), 200


# Get posts by user_id
@app.route('/posts/<user_id>', methods=['GET'])
def get_posts_by_user(user_id):
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
    result = []
    for post in posts:
        result.append({
            'post_id': post.post_id,
            'user_id': post.user_id,
            'content': post.content,
            'image_urls': post.image_urls.split(','),
            'created_at': post.created_at.isoformat()
        })
    return jsonify({
        'code': 200,
        'message': 'Posts retrieved successfully.',
        'data': result
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
