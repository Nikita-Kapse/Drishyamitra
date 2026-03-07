from flask import Blueprint, jsonify
from models.person_model import Person
from models.photo_model import Photo

person_bp = Blueprint("persons", __name__)

API_BASE = "http://localhost:5000/api"


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
