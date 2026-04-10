from datetime import datetime

def create_report(data):
    return {
        "document_id": data.get("document_id"),
        "report_name": data.get("report_name"),
        "report_type": data.get("report_type"),
        "division": data.get("division"),   
        "equipment": data.get("equipment"), 
        "prepared_by": data.get("prepared_by"),
        "report_date": data.get("report_date"),
        "summary": data.get("summary"),

        # FIXED: support multiple files
        "files": data.get("files", []),

        "ocr_text": data.get("ocr_text"),
        "ai_summary": data.get("ai_summary"),
        "uploaded_at": data.get("uploaded_at")
    }