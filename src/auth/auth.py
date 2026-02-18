# auth.py
# This module handles user authentication and role-based access.

from flask import Flask, request, jsonify, render_template, Blueprint
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from passlib.hash import bcrypt
from .config import JWT_SECRET_KEY, BCRYPT_LOG_ROUNDS
from .models import db, User

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Update with your database URI
db.init_app(app)
jwt = JWTManager(app)

# Create the auth blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "Manager")  # Default role is 'Manager'

    if not username or not password or not role:
        return jsonify({"msg": "username, password, and role required"}), 400

    # Check if the username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400

    # Hash the password and save the user
    pw_hash = bcrypt.using(rounds=BCRYPT_LOG_ROUNDS).hash(password)
    user = User(username=username, password=pw_hash, role=role)
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "user created"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    username = data.get("username")
    password = data.get("password")

    # Check if the user exists
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"msg": "Username not found"}), 404

    # Check if the password is correct
    if not bcrypt.verify(password, user.password):
        return jsonify({"msg": "Incorrect password"}), 401

    # Generate access token and log in the user
    access_token = create_access_token(identity={'email': user.email, 'name': user.name})
    return jsonify(access_token=access_token), 200

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)
