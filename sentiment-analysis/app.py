import json
from datetime import datetime
from bson import ObjectId
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# 1. Set up Flask App & Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)

# 2. Connect to MongoDB
# This is your correct, working URI
uri = "mongodb+srv://kdp:Nikitadh1@cluster0.xgqltqs.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

# Ping the database to test the connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Get your database collections
db = client['SocialMediaAnalytics'] 
users_collection = db['users']
posts_collection = db['posts']
comments_collection = db['comments']


# 3. API Routes

@app.route("/")
def home():
    """A test route to see if the server is running."""
    return "Hello, your backend server is running!"

# --- 4. CRUD OPERATIONS ---

# C = CREATE a new user (Sign Up)
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    existing_user = users_collection.find_one({"email": data['email']})
    if existing_user:
        return jsonify({"error": "Email already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    # This matches your 'users' schema exactly
    new_user = {
        "username": data['username'],
        "display_name": data['display_name'],
        "email": data['email'],
        "password": hashed_password,
        "join_date": datetime.now(),
        "role": "user",
        "age": data['age'],
        "gender": data['gender']
    }
    users_collection.insert_one(new_user)
    return jsonify({"message": "User created successfully"}), 201

# R = READ a user (Login)
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = users_collection.find_one({"email": data['email']})

    if user and bcrypt.check_password_hash(user['password'], data['password']):
        return jsonify({
            "message": "Login successful",
            "user_id": str(user['_id']), 
            "username": user['username'],
            "role": user['role']
        }), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401

# --- POSTS CRUD (Using Final Upgraded Schema) ---

# C = CREATE a new post
@app.route("/posts", methods=["POST"])
def create_post():
    data = request.get_json()
    new_post = {
        "author_id": ObjectId(data['author_id']), 
        "author_username": data['author_username'],
        "content": data['content'],
        "timestamp": datetime.now(),
        "comment_count": 0,
        "hashtags": data.get('hashtags', []),
        "media_url": data.get('media_url', None),
        "location": data.get('location', None),
        "category": "Unclassified", # Automatically set for Spark to analyze later
        "like_count": 0,         
        "liked_by": []           
    }
    result = posts_collection.insert_one(new_post)
    return jsonify({
        "message": "Post created successfully",
        "post_id": str(result.inserted_id) 
    }), 201

# R = READ all posts
@app.route("/posts", methods=["GET"])
def get_all_posts():
    all_posts = []
    # .find() is a simple "Read"
    for post in posts_collection.find().sort("timestamp", -1):
        post['_id'] = str(post['_id'])
        post['author_id'] = str(post['author_id'])
        # Also send the 'liked_by' list, converting IDs to strings
        post['liked_by'] = [str(uid) for uid in post.get('liked_by', [])]
        all_posts.append(post)
    
    return jsonify(all_posts), 200

# U = UPDATE a post (Toggle Like - FINAL SCHEMA)
@app.route("/posts/<post_id>/like", methods=["POST"])
def toggle_like_post(post_id):
    data = request.get_json()
    
    # Check if user_id was provided
    if 'user_id' not in data:
        return jsonify({"error": "user_id is required to like a post"}), 400

    try:
        user_id = ObjectId(data['user_id'])
        post_obj_id = ObjectId(post_id)
    except Exception as e:
        return jsonify({"error": "Invalid user_id or post_id format"}), 400

    # Check if user already liked the post
    post = posts_collection.find_one({"_id": post_obj_id, "liked_by": user_id})

    if post:
        # User has liked it, so UNLIKE it
        posts_collection.update_one(
            {"_id": post_obj_id},
            {
                "$pull": {"liked_by": user_id}, # Remove user from array
                "$inc": {"like_count": -1}       # Decrement count
            }
        )
        return jsonify({"message": "Post unliked"}), 200
    else:
        # User has not liked it, so LIKE it
        posts_collection.update_one(
            {"_id": post_obj_id},
            {
                "$addToSet": {"liked_by": user_id}, # Add user to array (prevents duplicates)
                "$inc": {"like_count": 1}         # Increment count
            }
        )
        return jsonify({"message": "Post liked"}), 200

# D = DELETE a post
@app.route("/posts/<post_id>", methods=["DELETE"])
def delete_post(post_id):
    try:
        post_obj_id = ObjectId(post_id)
        # 1. Delete the post
        result = posts_collection.delete_one({"_id": post_obj_id})
        if result.deleted_count == 0:
            return jsonify({"error": "Post not found"}), 404
        
        # 2. Delete all comments for that post
        comments_collection.delete_many({"post_id": post_obj_id})
        return jsonify({"message": "Post and associated comments deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": "Invalid Post ID format"}), 400

# --- COMMENTS CRUD (Using Final Upgraded Schema) ---

# C = CREATE a new comment
@app.route("/comments", methods=["POST"])
def create_comment():
    data = request.get_json()
    
    # Check for required fields
    if 'post_id' not in data or 'author_id' not in data or 'comment_text' not in data:
         return jsonify({"error": "post_id, author_id, and comment_text are required"}), 400

    try:
        new_comment = {
            "post_id": ObjectId(data['post_id']), 
            "author_id": ObjectId(data['author_id']), # <-- FINAL SCHEMA
            "author_username": data['author_username'],
            "comment_text": data['comment_text'],
            "timestamp": datetime.now()
        }
        result = comments_collection.insert_one(new_comment)
        
        # Update the post's comment_count
        posts_collection.update_one(
            {"_id": ObjectId(data['post_id'])},
            {"$inc": {"comment_count": 1}}
        )
        
        return jsonify({
            "message": "Comment added successfully",
            "comment_id": str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({"error": "Invalid post_id or author_id format"}), 400


# This line runs the app
if __name__ == '__main__':
    app.run(debug=True)

