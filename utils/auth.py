from flask import Blueprint, request, jsonify, session
from config import users_collection, db
from models.user_model import create_user, verify_password
from services.log_service import log_action

import uuid
from datetime import datetime

auth_bp = Blueprint("auth", __name__)


from functools import wraps
from flask import session, jsonify, redirect


# ---------------- LOGIN REQUIRED ----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# ---------------- ADMIN REQUIRED ----------------
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("role") != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function


# ---------------- REGISTER ----------------
@auth_bp.route("/api/register", methods=["POST"])
def register():

    try:
        data = request.json

        if not data.get("username") or not data.get("password"):
            return jsonify({"error": "Username and password required"}), 400

        if users_collection.find_one({"username": data["username"]}):
            return jsonify({"error": "User already exists"}), 409

        user = create_user({
            "username": data["username"],
            "password": data["password"],
            "role": "operator"   # UPDATED
        })

        users_collection.insert_one(user)

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"error": "Server error"}), 500


# ---------------- LOGIN ----------------
@auth_bp.route("/api/login", methods=["POST"])
def login():

    try:
        data = request.json

        if not data.get("username") or not data.get("password"):
            return jsonify({"error": "Username and password required"}), 400

        user = users_collection.find_one({"username": data["username"]})

        if not user or not verify_password(user, data["password"]):
            return jsonify({"error": "Invalid credentials"}), 401

        session["user"] = user["username"]
        session["role"] = user["role"]

        if data.get("remember"):
            session.permanent = True
        else:
            session.permanent = False

        log_action(
            username=user["username"],
            action_type="LOGIN",
            description="User logged in"
        )

        return jsonify({
            "message": "Login successful",
            "username": user["username"],
            "role": user["role"]
        }), 200

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"error": "Server error"}), 500