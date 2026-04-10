from flask import Blueprint, request, jsonify, send_from_directory, session
from config import reports_collection, db
from models.report_model import create_report
from services.ocr_service import extract_text
from services.storage_service import save_file
from services.ai_service import generate_summary
from utils.auth import admin_required
from services.log_service import log_action
from utils.auth import admin_required
from utils.permission import can_view

import os
import uuid
from datetime import datetime

# Blueprint
report_bp = Blueprint("report", __name__, url_prefix="/api")

UPLOAD_FOLDER = "uploads/reports"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Collections
dropdowns_collection = db["dropdowns"]
search_collection = db["search_logs"]




# --------------------------------------------------
# Serve uploaded files
# --------------------------------------------------
@report_bp.route("/uploads/<path:filepath>")
def serve_file(filepath):
    full_path = os.path.join("uploads", filepath)

    if not os.path.exists(full_path):
        return "File not found", 404

    return send_from_directory("uploads", filepath)

# --------------------------------------------------
# GET DROPDOWNS
# --------------------------------------------------
@report_bp.route("/dropdowns", methods=["GET"])
def get_dropdowns():
    data = list(dropdowns_collection.find({}, {"_id": 0}))

    result = {}
    for item in data:
        result[item["field"]] = item["values"]

    return jsonify(result)

# --------------------------------------------------
# ADD DROPDOWN VALUE (ADMIN)
# --------------------------------------------------
@report_bp.route("/add-dropdown/<field>", methods=["POST"])
@admin_required
def add_dropdown(field):
    data = request.get_json()

    value = data.get("value")

    if not value or not value.strip():
        return jsonify({"error": "Value required"}), 400

    new_item = {
        "name": value.strip(),
        "uploaded_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "created_by": session.get("username", "admin")
    }

    dropdowns_collection.update_one(
        {"field": field},
        {"$push": {"values": new_item}},
        upsert=True
    )

    return jsonify({"message": "Added successfully"})

# --------------------------------------------------
# Recent Uploads
# --------------------------------------------------
@report_bp.route("/recent-uploads", methods=["GET"])
def recent_uploads():

    reports = list(reports_collection.find(
        {},
        {
            "_id": 0,
            "document_id": 1,
            "report_name": 1,
            "report_type": 1,
            "division": 1,
            "report_date": 1,
            "prepared_by": 1
        }
    ).sort([("_id", -1)]).limit(5))

    return jsonify(reports)

# --------------------------------------------------
# Dashboard Stats
# --------------------------------------------------
@report_bp.route("/stats", methods=["GET"])
def get_stats():

    total_reports = reports_collection.count_documents({})
    total_searches = search_collection.count_documents({})
    total_users = db["users"].count_documents({})

    return jsonify({
        "total_reports": total_reports,
        "total_searches": total_searches,
        "total_users": total_users
    })

# --------------------------------------------------
# Upload Report
# --------------------------------------------------
@report_bp.route("/upload-report", methods=["POST"])
def upload_report():

    files = request.files.getlist("files")

    if not files or all(f.filename == "" for f in files):
        return jsonify({"error": "Files are required"}), 400

    data = request.form

    required_fields = [
        "document_id",
        "report_name",
        "report_type",
        "prepared_by",
        "report_date",
        "division"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    if reports_collection.find_one({"document_id": data["document_id"]}):
        return jsonify({"error": "Document ID already exists"}), 409

    file_paths = []

    for file in files:
        if file and file.filename != "":
            path = save_file(file, UPLOAD_FOLDER)

            try:
                text = extract_text(path)

                # 🔥 DEBUG (add this temporarily)
                print("TEXT LENGTH:", len(text))

                if text and text.strip():
                    summary = generate_summary(text[:3000])
                else:
                    summary = "No text extracted from file"

            except Exception as e:
                print("Error processing file:", e)
                summary = "Error generating summary"

            file_paths.append({
                "path": path,
                "summary": summary
            })

    report = create_report({
        "document_id": data.get("document_id"),
        "report_name": data.get("report_name"),
        "report_type": data.get("report_type"),
        "division": data.get("division"),
        "equipment": data.get("equipment"),
        "prepared_by": data.get("prepared_by"),
        "report_date": data.get("report_date"),
        "summary": data.get("summary"),
        "files": file_paths,
        "ocr_text": "",
        "ai_summary": "",
        "uploaded_at": datetime.utcnow()
    })

    reports_collection.insert_one(report)

    #  LOGGING
    username = session.get("user", "Guest")
    log_action(
        username=username,
        action_type="UPLOAD",
        document_id=data.get("document_id"),
        document_name=data.get("report_name"),
        description="Report uploaded"
    )

    return jsonify({"message": "Report uploaded successfully"}), 201

# --------------------------------------------------
# Get All Reports
# --------------------------------------------------
@report_bp.route("/all-reports", methods=["GET"])
def get_all_reports():

    username = session.get("user")

    reports = reports_collection.find(
        {},
        {
            "_id": 0,
            "document_id": 1,
            "report_name": 1,
            "report_type": 1,
            "division": 1,
            "equipment": 1,
            "report_date": 1,
            "files": 1,
            "ai_summary": 1
        }
    )

    # permission filter
    filtered = [r for r in reports if can_view(username, r, db)]

    return jsonify(filtered)

# --------------------------------------------------
# Delete Report
# --------------------------------------------------
@report_bp.route("/delete-report/<id>", methods=["DELETE"])
@admin_required
def delete_report(id):

    report = reports_collection.find_one({"document_id": id})

    reports_collection.delete_one({"document_id": id})

    #  LOGGING
    username = session.get("user", "Guest")
    log_action(
        username=username,
        action_type="DELETE",
        document_id=id,
        document_name=report.get("report_name") if report else "",
        description="Report deleted"
    )

    return jsonify({"message": "Deleted"})

# --------------------------------------------------
# Update Report
# --------------------------------------------------
@report_bp.route("/update-report/<document_id>", methods=["PUT"])
def update_report(document_id):

    data = request.json

    report = reports_collection.find_one({"document_id": document_id})

    if not report:
        return jsonify({"error": "Report not found"}), 404

    update_fields = {
        "report_name": data.get("report_name"),
        "report_type": data.get("report_type"),
        "division": data.get("division"),
        "equipment": data.get("equipment"),
        "prepared_by": data.get("prepared_by"),
        "report_date": data.get("report_date"),
        "summary": data.get("summary")
    }

    update_fields = {k: v for k, v in update_fields.items() if v is not None}

    reports_collection.update_one(
        {"document_id": document_id},
        {"$set": update_fields}
    )

    #  LOGGING
    username = session.get("user", "Guest")
    log_action(
        username=username,
        action_type="EDIT",
        document_id=document_id,
        document_name=data.get("report_name"),
        description="Report updated"
    )

    return jsonify({"message": "Updated successfully"})

# --------------------------------------------------
# Get Action Logs
# --------------------------------------------------
from bson import ObjectId

@report_bp.route("/action-logs", methods=["GET"])
def get_action_logs():
    try:
        action_logs_collection = db["action_logs"]

        # get query params
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))

        skip = (page - 1) * limit

        total = action_logs_collection.count_documents({})

        logs_cursor = (
            action_logs_collection
            .find()
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )

        logs = []
        for log in logs_cursor:
            log["_id"] = str(log["_id"])
            logs.append(log)

        return jsonify({
            "logs": logs,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }), 200

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Failed"}), 500
    

@report_bp.route("/action-log/<log_id>", methods=["GET"])
def get_action_log(log_id):
    try:
        action_logs_collection = db["action_logs"]

        logs_cursor = action_logs_collection.find()

        for log in logs_cursor:
            if str(log["_id"]) == log_id:
                log["_id"] = str(log["_id"])
                return jsonify(log), 200

        return jsonify({"error": "Log not found"}), 404

    except Exception as e:
        print("ERROR IN get_action_log:", e)
        return jsonify({"error": "Failed"}), 500



# --------------------------------------------------
# Recent Searches
# --------------------------------------------------
@report_bp.route("/recent-searches", methods=["GET"])
def recent_searches():

    searches = list(search_collection.find(
        {},
        {
            "_id": 0,
            "document_id": 1,
            "report_name": 1,
            "report_type": 1,
            "division": 1,
            "date": 1,
            "user": 1
        }
    ).sort([("_id", -1)]).limit(5))

    return jsonify(searches)

# --------------------------------------------------
# Upload Trend (GRAPH)
# --------------------------------------------------
@report_bp.route("/upload-trend", methods=["GET"])
def upload_trend():

    view_type = request.args.get("type", "month")

    reports = list(reports_collection.find({}, {"uploaded_at": 1, "_id": 0}))

    trend = {}

    for r in reports:
        if "uploaded_at" in r and r["uploaded_at"]:
            if view_type == "day":
                key = r["uploaded_at"].strftime("%d %b")
            else:
                key = r["uploaded_at"].strftime("%b")

            trend[key] = trend.get(key, 0) + 1

    labels = sorted(trend.keys())
    values = [trend[k] for k in labels]

    return jsonify({
        "labels": labels,
        "values": values
    })

# --------------------------------------------------
# Log Search
# --------------------------------------------------
@report_bp.route("/log-search", methods=["POST"])
def log_search():

    data = request.json

    report = None
    if data.get("document_id"):
        report = reports_collection.find_one(
            {"document_id": data.get("document_id")},
            {"_id": 0}
        )

    search_collection.insert_one({
        "document_id": report.get("document_id") if report else None,
        "report_name": report.get("report_name") if report else data.get("report_name"),
        "report_type": report.get("report_type") if report else None,
        "division": report.get("division") if report else None,
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "user": data.get("user", "Admin")
    })

    return jsonify({"message": "Logged"})


# ---------------- ROLE MANAGEMENT ----------------
@report_bp.route("/roles", methods=["GET"])
def get_roles():
    roles = list(db.roles.find({}, {"_id": 0}))
    return jsonify(roles)


@report_bp.route("/update-role/<role>", methods=["PUT"])
def update_role(role):

    data = request.json

    db.roles.update_one(
        {"role": role},
        {"$set": {"permissions": data.get("permissions", {})}}
    )

    return jsonify({"message": "Updated"})


@report_bp.route("/users", methods=["GET"])
@admin_required
def get_users():
    users = list(db.users.find({}, {"_id": 0, "password": 0}))
    return jsonify(users)


@report_bp.route("/update-user-role", methods=["PUT"])
@admin_required
def update_user_role():

    data = request.json

    username = data.get("username")
    role = data.get("role")
    divisions = data.get("allowed_divisions", [])
    types = data.get("allowed_types", [])

    db.users.update_one(
        {"username": username},
        {
            "$set": {
                "role": role,
                "allowed_divisions": divisions,
                "allowed_types": types
            }
        }
    )

    return jsonify({"message": "Updated"})