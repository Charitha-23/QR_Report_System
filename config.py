from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["qr_reports_db"]

users_collection = db["users"]
reports_collection = db["reports"]
audit_collection = db["audit_logs"]

# roles
roles_collection = db["roles"]