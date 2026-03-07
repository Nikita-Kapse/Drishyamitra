import os
from flask import current_app
from app.database import db
from models.photo_model import Photo
from models.person_model import Person
from models.embedding_model import Embedding
from utils.file_utils import allowed_file, save_file
from services.face_service import detect_faces, generate_embedding, embedding_to_json
from services.recognition_service import find_matching_person


def create_photo(file):
    """
    Full upload pipeline:
      1. Validate + save the image file
      2. Persist Photo record to DB
      3. Run face detection (RetinaFace)
      4. For each face, generate Facenet512 embedding
      5. Try to match against existing persons; create a new Person if no match
      6. Store embedding linked to both photo and person

    Returns (photo_dict, error_string). Exactly one will be None.
    """
    if not file or file.filename == "":
        return None, "No file provided."

    if not allowed_file(file.filename):
        return None, "File type not allowed. Use JPG, JPEG, or PNG."

    upload_folder = current_app.config["UPLOAD_FOLDER"]

    # ── 1. Save to disk ──────────────────────────────────────────────────────
    try:
        unique_filename = save_file(file, upload_folder)
    except Exception as exc:
        return None, f"Could not save file: {exc}"

    filepath = os.path.join(upload_folder, unique_filename)

    # ── 2. Persist Photo row ─────────────────────────────────────────────────
    photo = Photo(filename=unique_filename, filepath=filepath)
    try:
        db.session.add(photo)
        db.session.commit()
    except Exception as exc:
        return None, f"Database error: {exc}"

    # ── 3. Face detection (non-blocking — errors won't fail the upload) ──────
    try:
        faces = detect_faces(filepath)

        # ── 4 + 5. Embedding + recognition per face ──────────────────────────
        # detect_faces() now returns cropped numpy arrays directly
        for face_img in faces:
            vector = generate_embedding(face_img)
            if vector is None:
                continue

            # ── 5. Try to recognise; create new Person if unknown ────────────
            matched_person_id = find_matching_person(vector)

            if matched_person_id is not None:
                person_id = matched_person_id
            else:
                # First time we see this face → create a new Person record
                new_person = Person()
                db.session.add(new_person)
                db.session.flush()   # get new_person.id before commit
                person_id = new_person.id
                print(f"New person created: {person_id}")

            # Stamp the photo row so it has a direct person link
            photo.person_id = person_id

            # ── 6. Save embedding linked to photo and person ──────────────────
            emb = Embedding(
                photo_id=photo.id,
                person_id=person_id,
                embedding=embedding_to_json(vector),
            )
            db.session.add(emb)

        db.session.commit()

    except Exception as exc:
        # Face pipeline failure must NOT roll back the photo record
        db.session.rollback()
        print(f"Face pipeline error (photo still saved): {exc}")

    return photo.to_dict(), None


def get_all_photos():
    """Return all photos ordered by upload date descending."""
    photos = Photo.query.order_by(Photo.uploaded_at.desc()).all()
    return [p.to_dict() for p in photos]
