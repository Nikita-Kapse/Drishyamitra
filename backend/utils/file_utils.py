import os
import uuid

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


def allowed_file(filename: str) -> bool:
    """Return True if the file has an allowed image extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def save_file(file, upload_folder: str) -> str:
    """
    Save a Werkzeug FileStorage object to `upload_folder` with a UUID-based name.
    Returns the generated unique filename.
    """
    ext = file.filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    dest = os.path.join(upload_folder, unique_filename)
    os.makedirs(upload_folder, exist_ok=True)
    file.save(dest)
    return unique_filename
