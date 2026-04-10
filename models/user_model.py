from werkzeug.security import generate_password_hash, check_password_hash


def create_user(data):
    return {
        "username": data["username"],
        "password": generate_password_hash(data["password"]),
        "role": data.get("role", "user"),
        "active": True
    }


def verify_password(user, password):

    stored_password = user["password"]

    # 🔥 If password is bytes (old bcrypt data)
    if isinstance(stored_password, bytes):
        try:
            import bcrypt
            return bcrypt.checkpw(password.encode(), stored_password)
        except:
            return False

    # 🔥 Normal case (werkzeug)
    return check_password_hash(stored_password, password)