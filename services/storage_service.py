import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "docx", "txt", "pptx"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, upload_folder):

    if not file or file.filename == "":
        return None

    if not allowed_file(file.filename):
        raise ValueError("Invalid file type")

    os.makedirs(upload_folder, exist_ok=True)

    filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
    file_path = os.path.join(upload_folder, filename)

    file.save(file_path)

    return file_path.replace("\\", "/")