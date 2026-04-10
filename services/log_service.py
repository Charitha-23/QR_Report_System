from config import db
import uuid
from datetime import datetime

action_logs_collection = db["action_logs"]

def log_action(username, action_type, document_id=None, document_name=None, description=None):
    action_logs_collection.insert_one({
        "_id": str(uuid.uuid4()),
        "username": username,
        "action_type": action_type,
        "document_id": document_id,
        "document_name": document_name,
        "description": description,
        "timestamp": datetime.utcnow()
    })