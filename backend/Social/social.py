from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import os
import jwt
import pika
import json
from urllib.parse import urlparse
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Initialise Supabase
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# JWT verification
def verify_token(token):
    try:
        payload = jwt.decode(
            token,
            os.getenv('JWT_SECRET', 'esd_jwt_secret_key'),
            algorithms=[os.getenv('JWT_ALGORITHM', 'HS256')]
        )
        return payload
    except jwt.InvalidTokenError:
        return None

# RabbitMQ connection
def publish_notification(event_type, data):
    amqp_url = os.environ.get("AMQP_URL")
    params = pika.URLParameters(amqp_url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue='notifications', durable=True)

    message = {
        "event_type": event_type,
        "data": data
    }
    channel.basic_publish(
        exchange='',
        routing_key='notifications',
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    connection.close()

@app.route('/api/social/like', methods=['POST'])
def like_post():
    token = request.headers.get('Authorization', '').split(' ')[-1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid or missing token'}), 401

    post_id = request.json.get('post_id')
    if not post_id:
        return jsonify({'error': 'Missing post_id'}), 400

    # Get post owner from Supabase
    post_resp = supabase.table("post").select("user_id").eq("id", post_id).single().execute()
    if not post_resp.data:
        return jsonify({"error": "Post not found"}), 404

    post_owner_id = post_resp.data["user_id"]

    # Check if this user already liked the post
    existing_like = supabase.table("likes") \
        .select("*") \
        .eq("post_id", post_id) \
        .eq("liked_by_user_id", payload["user_id"]) \
        .execute()
    
    if existing_like.data:
        # Unlike: delete the like
        supabase.table("likes") \
            .delete() \
            .eq("post_id", post_id) \
            .eq("liked_by_user_id", payload["user_id"]) \
            .execute()

        return jsonify({'message': 'Post unliked'}), 200
    
    else: 
        # Insert like into Supabase
        supabase.table("likes").insert({
            "post_id": post_id,
            "liked_by_user_id": payload['user_id'],
            "liked_by_username": payload['username'],
            "post_owner_id": post_owner_id
        }).execute()

        # Send event to RabbitMQ
        publish_notification("new_like", {
            "post_id": post_id,
            "liked_by_user_id": payload["user_id"],
            "liked_by_username": payload["username"],
            "post_owner_id": post_owner_id
        })

        return jsonify({'message': 'Post liked'}), 201

@app.route('/api/social/comment', methods=['POST'])
def comment_post():
    token = request.headers.get('Authorization', '').split(' ')[-1]
    payload = verify_token(token)
    if not payload:
        return jsonify({'error': 'Invalid or missing token'}), 401

    if not post_id or not comment:
        return jsonify({'error': 'Missing post_id or comment'}), 400
    
    data=request.json()
    post_id = request.json.get('post_id')
    comment = request.json.get('comment')
    parent_comment_id = data.get('parent_comment_id')  
    if not post_id or not comment:
        return jsonify({'error': 'Missing post_id or comment'}), 400

    # Determine who is being replied to
    if parent_comment_id:
        parent_resp = supabase.table("comments").select("user_id").eq("id", parent_comment_id).single().execute()
        if parent_resp.data:
            reply_to_user_id = parent_resp.data["user_id"]

    # Insert comment (with optional reply info)
    supabase.table("comments").insert({
        "post_id": post_id,
        "user_id": payload['user_id'],
        "username": payload['username'],
        "comment": comment,
        "parent_comment_id": parent_comment_id,
        "reply_to_user_id": reply_to_user_id
    }).execute()

    # Send notification to RabbitMQ
    # Send notification to parent commenter (if applicable)
    if reply_to_user_id and reply_to_user_id != payload['user_id']:
        publish_notification("reply_comment", {
            "post_id": post_id,
            "parent_comment_id": parent_comment_id,
            "replied_by_user_id": payload["user_id"],
            "replied_by_username": payload["username"],
            "replied_to_user_id": reply_to_user_id,
            "comment": comment
        })

    return jsonify({'message': 'Comment added'}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
