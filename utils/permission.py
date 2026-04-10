from config import roles_collection


# ---------------- GET USER ----------------
def get_user(username, db):
    return db.users.find_one({"username": username})


# ---------------- GET USER ROLE ----------------
def get_user_role(username, db):
    user = get_user(username, db)
    if not user:
        return None
    return user.get("role")


# ---------------- GET ROLE PERMISSIONS ----------------
def get_role_permissions(role):
    role_data = roles_collection.find_one({"role": role})
    if not role_data:
        return {}
    return role_data.get("permissions", {})


# ---------------- COMMON SCOPE CHECK ----------------
def check_data_scope(user, document):

    # Division restriction
    allowed_divisions = user.get("allowed_divisions", [])
    if allowed_divisions:
        if document.get("division") not in allowed_divisions:
            return False

    # Report type restriction
    allowed_types = user.get("allowed_types", [])
    if allowed_types:
        if document.get("report_type") not in allowed_types:
            return False

    return True


# ---------------- VIEW ----------------
def can_view(username, document, db):

    user = get_user(username, db)
    if not user:
        return False

    role = user.get("role")

    # ADMIN BYPASS
    if role == "admin":
        return True

    permissions = get_role_permissions(role)

    # Role permission check
    if not permissions.get("view", False):
        return False

    # Data scope check
    return check_data_scope(user, document)


# ---------------- DOWNLOAD ----------------
def can_download(username, document, db):

    user = get_user(username, db)
    if not user:
        return False

    role = user.get("role")

    # ADMIN BYPASS
    if role == "admin":
        return True

    permissions = get_role_permissions(role)

    if not permissions.get("download", False):
        return False

    # Apply data scope
    return check_data_scope(user, document)


# ---------------- EDIT ----------------
def can_edit(username, document, db):

    user = get_user(username, db)
    if not user:
        return False

    role = user.get("role")

    # ADMIN BYPASS
    if role == "admin":
        return True

    permissions = get_role_permissions(role)

    if not permissions.get("edit", False):
        return False

    # Apply data scope
    return check_data_scope(user, document)


# ---------------- DELETE ----------------
def can_delete(username, document, db):

    user = get_user(username, db)
    if not user:
        return False

    role = user.get("role")

    # ADMIN BYPASS
    if role == "admin":
        return True

    permissions = get_role_permissions(role)

    if not permissions.get("delete", False):
        return False

    # Apply data scope
    return check_data_scope(user, document)