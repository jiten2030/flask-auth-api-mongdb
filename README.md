# Flask Authentication and Post Management API

This is a Flask-based RESTful API for user authentication and managing posts. The application includes user registration, login, adding posts, and deleting users or posts.

## Features

- User registration and login using JWT tokens.
- Password hashing using bcrypt.
- MongoDB integration for data storage.
- Endpoints secured with token authentication.

## Project Structure

- **`app.py`**: Main application file.
- **`.env`**: Environment variables for MongoDB URI and secret key.
- **`generate_secret_key.py`**: Utility to generate a secure key for JWT.
- **`requirements.txt`**: Python dependencies.

## Requirements

- Python 3.8+
- MongoDB running locally or accessible via URI.

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory:

```plaintext
MONGO_URI=mongodb://localhost:27017/authServer
SECRET_KEY=<your_generated_secret_key>
```

Generate a secret key using:

```bash
python generate_secret_key.py
```

## Running the Application

```bash
python app.py
```

The application will run on `http://127.0.0.1:5000`.

---

## API Endpoints

### 1. **Register a User**

- **URL**: `/register`
- **Method**: `POST`
- **Headers**: None
- **Request Body**:
  ```json
  {
    "username": "example",
    "password": "password123"
  }
  ```
- **Response**:
  ```json
  {
    "message": "User registered successfully!",
    "user_id": "<generated_user_id>"
  }
  ```

### 2. **Login a User**

- **URL**: `/login`
- **Method**: `POST`
- **Headers**: None
- **Request Body**:
  ```json
  {
    "username": "example",
    "password": "password123"
  }
  ```
- **Response**:
  ```json
  {
    "token": "<jwt_token>"
  }
  ```

### 3. **Add a Post**

- **URL**: `/addPost`
- **Method**: `POST`
- **Headers**:
  ```plaintext
  x-access-token: <jwt_token>
  ```
- **Request Body**:
  ```json
  {
    "caption": "My first post!",
    "postUrl": "http://example.com/image.jpg",
    "created": "2024-12-22T10:00:00"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Post added successfully!",
    "post": {
      "caption": "My first post!",
      "postUrl": "http://example.com/image.jpg",
      "created": "2024-12-22T10:00:00",
      "uid": "<user_id>",
      "postId": "<post_id>"
    }
  }
  ```

### 4. **Delete a User**

- **URL**: `/deleteUser`
- **Method**: `DELETE`
- **Headers**:
  ```plaintext
  x-access-token: <jwt_token>
  ```
- **Response**:
  ```json
  {
    "message": "User successfully deleted!"
  }
  ```

### 5. **Delete a Post**

- **URL**: `/deletePost`
- **Method**: `DELETE`
- **Headers**:
  ```plaintext
  x-access-token: <jwt_token>
  ```
- **Request Body**:
  ```json
  {
    "postId": "<post_id>"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Post successfully deleted!"
  }
  ```

---

## Notes

1. Ensure MongoDB is running and accessible at the specified URI in `.env`.
2. Tokens are valid for 1 hour; re-authenticate after expiration.
3. Use `generate_secret_key.py` to create a secure `SECRET_KEY`.

---