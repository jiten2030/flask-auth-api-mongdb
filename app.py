import os
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from dotenv import load_dotenv
import bcrypt
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Configure MongoDB
app.config['MONGO_URI'] = os.getenv("MONGO_URI")
mongo = PyMongo(app)

# Secret key for JWT
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = mongo.db.users.find_one({"_id": ObjectId(data['id'])})
            if not current_user:
                raise Exception("User not found")
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
        except PyMongoError as e:
            return jsonify({'message': 'Database error!', 'error': str(e)}), 500
        except Exception as e:
            return jsonify({'message': 'Token is invalid!', 'error': str(e)}), 401
        
        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required!'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    if mongo.db.users.find_one({'username': username}):
        return jsonify({'message': 'User already exists!'}), 409

    user_id = mongo.db.users.insert_one({
        'username': username,
        'password': hashed_password
    }).inserted_id

    return jsonify({'message': 'User registered successfully!', 'user_id': str(user_id)}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required!'}), 400

    user = mongo.db.users.find_one({'username': username})

    if not user or not bcrypt.checkpw(password.encode('utf-8'),user['password']):
        return jsonify({'message': 'Invalid username or password!'}), 401

    token = jwt.encode({
        'id': str(user['_id']),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token})

@app.route('/addPost', methods=['POST'])
@token_required
def addPost(current_user):

    data = request.json
    caption = data['caption']
    post_url = data['postUrl']
    created = data['created']
    uid = str(current_user['_id'])  # Assuming `uid` is part of the `current_user` object

    if not caption or not post_url or not created:
        return jsonify({'message': 'Missing required fields'}), 400
    
    # Create the post document
    post_data = {
        'caption': caption,
        'postUrl': post_url,
        'created': created,
        'uid': uid
    }

    inserted_id = mongo.db.posts.insert_one(post_data).inserted_id
    # Return the response
    return jsonify({
        'message': 'Post added successfully!',
        'post': {
            'caption': post_data['caption'],
            'postUrl': post_data['postUrl'],
            'created': post_data['created'],
            'uid': post_data['uid'],
            'postId': str(inserted_id)  # Include the inserted MongoDB document ID
        }
    }), 201

@app.route('/deleteUser', methods=['DELETE'])
@token_required
def delete_user(current_user):
    try:
        # Extract the uid from the current_user
        current_user_uid = str(current_user['_id'])

        # Match current_user's UID with the '_id' field in the users collection
        user_in_db = mongo.db.users.find_one({"_id": ObjectId(current_user_uid)})

        if not user_in_db:
            return jsonify({'message': 'User not found!'}), 404
        
        # If match, proceed to delete the user
        result = mongo.db.users.delete_one({'_id': ObjectId(current_user_uid)})

        if result.deleted_count == 0:
            return jsonify({'message': 'User could not be deleted!'}), 500

        return jsonify({'message': 'User successfully deleted!'}), 200

    except PyMongoError as e:
        return jsonify({'message': 'Database error!', 'error': str(e)}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'message': 'An error occurred!', 'error': str(e)}), 500


@app.route('/deletePost', methods=['DELETE'])
@token_required
def delete_post(current_user):
    try:
        # Extract the uid from the current_user
        current_user_uid = str(current_user['_id'])

        # json
        postId = request.json['postId']

        # Find the post with postId
        post = mongo.db.posts.find_one({"_id": ObjectId(postId)})
        if not post:
            return jsonify({'message': 'No Posts Found!'}), 404
        
        # Verify ownership of the post
        if post.get('uid') != current_user_uid:
            return jsonify({'message': 'Unauthorized action!'}), 403
        
        # If match, proceed to delete the user
        result = mongo.db.posts.delete_one({'_id': ObjectId(postId)})

        if result.deleted_count == 0:
            return jsonify({'message': 'Post could not be deleted!'}), 500

        return jsonify({'message': 'Post successfully deleted!'}), 200

    except PyMongoError as e:
        return jsonify({'message': 'Database error!', 'error': str(e)}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'message': 'An error occurred!', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)