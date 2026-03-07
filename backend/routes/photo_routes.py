from flask import Blueprint, request, jsonify, send_from_directory, current_app
from services.photo_service import create_photo, get_all_photos

photo_bp = Blueprint("photos", __name__)


@photo_bp.route("/upload-photo", methods=["POST"])
def upload_photo():
    """Accept a multipart/form-data POST with field 'photo' and save it."""
    if "photo" not in request.files:
        return jsonify({"success": False, "message": "No photo field in request."}), 400

    file = request.files["photo"]
    photo_dict, error = create_photo(file)

    if error:
        return jsonify({"success": False, "message": error}), 400

    return jsonify({"success": True, "photo": photo_dict}), 201


@photo_bp.route("/photos", methods=["GET"])
def list_photos():
    """Return all photo metadata."""
    photos = get_all_photos()
    return jsonify({"success": True, "photos": photos}), 200


@photo_bp.route("/uploads/<path:filename>", methods=["GET"])
def serve_upload(filename):
    """Serve an uploaded image file."""
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(upload_folder, filename)
