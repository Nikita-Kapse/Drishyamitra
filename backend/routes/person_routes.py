import os
from flask import Blueprint, jsonify, request
from models.person_model import Person
from models.photo_model import Photo
from app.database import db

person_bp = Blueprint("persons", __name__)

API_BASE = os.environ.get("API_BASE_URL", "").rstrip("/")


@person_bp.route("/persons", methods=["GET"])
def list_persons():
    """Return all persons with their photo count."""
    persons = Person.query.order_by(Person.created_at.asc()).all()
    result = []
    for p in persons:
        result.append({
            "id": p.id,
            "name": p.name or f"Person {p.id}",
            "photo_count": len(p.photos),
            "created_at": p.created_at.isoformat() if p.created_at else None,
        })
    return jsonify({"success": True, "persons": result}), 200


@person_bp.route("/persons/<int:person_id>/photos", methods=["GET"])
def get_person_photos(person_id):
    """Return all photos belonging to the given person."""
    person = Person.query.get_or_404(person_id)
    photos = (
        Photo.query
        .filter_by(person_id=person_id)
        .order_by(Photo.uploaded_at.desc())
        .all()
    )
    return jsonify({
        "success": True,
        "person": {
            "id": person.id,
            "name": person.name or f"Person {person.id}",
        },
        "photos": [p.to_dict() for p in photos],
    }), 200


@person_bp.route("/persons/<int:person_id>/rename", methods=["PUT"])
def rename_person(person_id):
    """Rename a detected person."""
    data = request.get_json(silent=True) or {}
    new_name = (data.get("name") or "").strip()

    if not new_name:
        return jsonify({"error": "Name is required"}), 400

    person = Person.query.get(person_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404

    person.name = new_name
    db.session.commit()

    return jsonify({
        "message": "Person renamed successfully",
        "person_id": person_id,
        "new_name": new_name,
    }), 200
