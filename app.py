from flask import Flask, render_template, send_from_directory, session, redirect, jsonify, request
from routes.report_routes import report_bp
from routes.auth_routes import auth_bp
from utils.auth import login_required
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime
from utils.permission import can_view
from utils.auth import admin_required

app = Flask(__name__)

# Secret key
app.secret_key = "supersecretkey"

# ------------------ DATABASE ------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["qr_reports_db"]
users = db["users"]

# ------------------ MASTER ADMIN ------------------
def create_admin():
    if not users.find_one({"username": "admin"}):
        users.insert_one({
            "username": "admin",
            "password": generate_password_hash("admin123"),
            "role": "admin"
        })
        print("Admin created")


# ------------------ DEFAULT ROLES ------------------
def create_default_roles():
    roles = [
        {
            "role": "admin",
            "permissions": {
                "view": True,
                "edit": True,
                "delete": True,
                "download": True
            }
        },
        {
            "role": "manager",
            "permissions": {
                "view": True,
                "edit": False,
                "delete": False,
                "download": True
            }
        },
        {
            "role": "operator",
            "permissions": {
                "view": True,
                "edit": False,
                "delete": False,
                "download": False
            }
        }
    ]

    for r in roles:
        if not db.roles.find_one({"role": r["role"]}):
            db.roles.insert_one(r)


# ------------------ REGISTER BLUEPRINTS ------------------
app.register_blueprint(report_bp)
app.register_blueprint(auth_bp)


# ------------------ FILE DOWNLOAD ------------------
@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory('uploads', filename)


# ------------------ MAIN PAGES ------------------

@app.route("/")
@login_required
def dashboard():
    return render_template("home/dashboard.html")


@app.route("/report/<document_id>")
@login_required
def report_details(document_id):

    username = session.get("user")

    report = db.reports.find_one({"document_id": document_id}, {"_id": 0})

    if not report:
        return "Not Found", 404

    if not can_view(username, report, db):
        return "Access Denied", 403

    # LOG VIEW
    db.audit_logs.insert_one({
        "username": username,
        "action_type": "VIEW",
        "document_id": document_id,
        "document_name": report.get("report_name"),
        "timestamp": datetime.utcnow()
    })

    return render_template("report_details.html", report=report)


@app.route("/dropdown-details/<field>/<value>")
@login_required
def dropdown_details(field, value):
    reports = list(db.reports.find({field: value}, {"_id": 0}))
    return render_template(
        "dropdown_details.html",
        reports=reports,
        value=value,
        field=field
    )


@app.route("/upload")
@login_required
def upload_page():
    return render_template("upload.html")


@app.route("/search")
@login_required
def search_page():
    return render_template("search.html", role=session.get("role"))


@app.route("/edit/<document_id>")
@login_required
def edit_page(document_id):
    return render_template("edit.html", document_id=document_id)


# ================= DROPDOWN APIs =================

@app.route('/api/dropdowns')
def get_dropdowns():
    docs = list(db.dropdowns.find({}, {"_id": 0}))

    result = {}
    for d in docs:
        if "field" in d and "values" in d:
            result[d["field"]] = d["values"]

    return jsonify(result)


@app.route('/api/add-dropdown/<field>', methods=['POST'])
def add_dropdown(field):
    value = request.json.get("value")

    new_item = {
        "name": value,
        "uploaded_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "created_by": session.get("user", "Unknown")  # FIXED
    }

    existing = db.dropdowns.find_one({"field": field})

    if existing:
        db.dropdowns.update_one(
            {"field": field},
            {"$push": {"values": new_item}}
        )
    else:
        db.dropdowns.insert_one({
            "field": field,
            "values": [new_item]
        })

    return jsonify({"msg": "added"})


@app.route('/api/delete-dropdown/<field>', methods=['POST'])
def delete_dropdown(field):
    value = request.json.get("value")

    db.dropdowns.update_one(
        {"field": field},
        {"$pull": {"values": {"name": value}}}
    )

    return jsonify({"msg": "deleted"})


# ================= REPORT TYPE APIs =================

@app.route('/api/sample/<field>/<value>')
def sample_report(field, value):
    report = db.reports.find_one({field: value}, {"_id": 0})
    return jsonify(report if report else {})


@app.route('/api/count/<field>/<value>')
def count_reports(field, value):
    count = db.reports.count_documents({field: value})
    return jsonify({"count": count})


@app.route('/api/first-upload/<field>/<value>')
def first_upload(field, value):
    report = db.reports.find_one(
        {field: value},
        {"_id": 0},
        sort=[("report_date", 1)]
    )
    return jsonify(report if report else {})


@app.route('/api/report-types')
def get_types():
    return jsonify(list(db.report_types.find({}, {"_id": 0})))


@app.route('/api/add-report-type', methods=['POST'])
def add_type():
    data = request.json

    new_data = {
        "name": data.get("name"),
        "uploaded_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "created_by": session.get("user", "Unknown")  # FIXED
    }

    db.report_types.insert_one(new_data)

    return jsonify({"msg": "added"})


@app.route('/api/add-sub-type', methods=['POST'])
def add_sub():
    data = request.json
    data["uploaded_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    db.report_types.insert_one(data)
    return jsonify({"msg": "added"})


@app.route('/api/delete-report-type', methods=['POST'])
def delete_type():
    name = request.json['name']
    db.report_types.delete_one({"name": name})
    return jsonify({"msg": "deleted"})


# ------------------ ADMIN PAGES ------------------

@app.route("/admin/report-types")
def manage_report_types():
    return render_template("admin/manage_dropdown.html", field="report_type")


@app.route("/admin/divisions")
def manage_divisions():
    return render_template("admin/manage_dropdown.html", field="division")


@app.route("/admin/equipment")
def manage_equipment():
    return render_template("admin/manage_dropdown.html", field="equipment")


# ------------------ AUTH PAGES ------------------

@app.route("/login")
def login():
    return render_template("accounts/login.html")


@app.route("/register")
def register():
    return render_template("accounts/register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ------------------ ERROR PAGES ------------------

@app.route("/404")
def error_404():
    return render_template("home/page-404.html")


@app.route("/500")
def error_500():
    return render_template("home/page-500.html")


# ------------------ ACTION LOG ------------------

@app.route("/action-logs")
def action_logs_page():
    return render_template("action_logs.html")


@app.route("/log-details")
def log_details_page():
    return render_template("log_details.html")


# ------------------ ROLE MANAGEMENT ------------------

@app.route("/admin/roles")
@login_required
def roles_page():
    return render_template("admin/roles.html")


# ------------------ GLOBAL USER (IMPORTANT) ------------------
@app.context_processor
def inject_user():
    return dict(username=session.get("username", "User"))


# ------------------ RUN ------------------

if __name__ == "__main__":
    create_admin()
    create_default_roles()
    app.run(debug=True)