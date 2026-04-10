from datetime import datetime

def create_log(username, action_type, document_id=None, document_name=None, description=None):
    return {
        "log_id": str(datetime.utcnow().timestamp()),  # unique id
        "username": username,
        "action_type": action_type,
        "document_id": document_id,
        "document_name": document_name,
        "description": description,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }