from flask import Blueprint, request, jsonify, session
from config import users_collection, db
from models.user_model import create_user, verify_password
from services.log_service import log_action

import uuid
from datetime import datetime

auth_bp = Blueprint("auth", __name__)




# ---------------- REGISTER ----------------
@auth_bp.route("/api/register", methods=["POST"])
def register():

    try:
        data = request.json

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        # Validate required fields
        if not username or not email or not password:
            return jsonify({"error": "Username, email and password required"}), 400

        # Check username exists
        if users_collection.find_one({"username": username}):
            return jsonify({"error": "Username already exists"}), 409

        # Check email exists
        if users_collection.find_one({"email": email}):
            return jsonify({"error": "Email already registered"}), 409

        # Create user
        user = create_user({
            "username": username,
            "email": email,
            "password": password,
            "role": "user"
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

        #  STORE SESSION
        session["user"] = user["username"]
        session["role"] = user["role"]

        #  REMEMBER ME
        if data.get("remember"):
            session.permanent = True
        else:
            session.permanent = False

        #  ADD LOGIN LOG
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