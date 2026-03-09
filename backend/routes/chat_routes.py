import logging
import os
from datetime import date, datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from services.chatbot_service import parse_query
from services.email_service import send_photos

chat_bp = Blueprint("chat", __name__)
logger = logging.getLogger(__name__)

API_BASE = os.environ.get("API_BASE_URL", "").rstrip("/")


@chat_bp.route("/chat", methods=["POST"])
def chat():
    """
    POST /api/chat
    Body: { "message": "<user query>" }
    Returns: { "reply": "...", "photos": [...] }
    """
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a message!", "photos": []}), 400

    # ── Load known persons so LLM can resolve names ───────────────────────────
    try:
        from models.person_model import Person
        from models.photo_model import Photo

        persons = [
            {"id": p.id, "name": p.name or f"Person {p.id}"}
            for p in Person.query.order_by(Person.id).all()
        ]
    except Exception as exc:
        logger.error("DB error loading persons: %s", exc)
        print("CHATBOT ERROR (DB load):", exc)
        return jsonify({"reply": "Database error. Please try again.", "photos": []}), 500

    # ── Parse intent via Groq ─────────────────────────────────────────────────
    try:
        intent_data = parse_query(user_message, persons)
        print("Groq intent:", intent_data)
    except RuntimeError as exc:
        print("CHATBOT ERROR (key):", exc)
        return jsonify({"reply": str(exc), "photos": []}), 503
    except Exception as exc:
        print("CHATBOT ERROR (groq):", exc)
        logger.error("Groq error: %s", exc)
        return jsonify({"reply": "AI service error. Please try again later.", "photos": []}), 503

    intent = intent_data.get("intent", "unknown")
    photos = []
    reply = ""

    # ── Resolve intent → DB query ─────────────────────────────────────────────
    if intent == "search_person":
        person_id = intent_data.get("person_id")

        # Fallback: LLM sometimes returns person_name instead of person_id
        if person_id is None:
            person_name = intent_data.get("person_name") or intent_data.get("name", "")
            matched = _find_person_by_name(person_name, persons)
            if matched:
                person_id = matched["id"]

        if person_id is None:
            reply = "I couldn't identify which person you meant. Try 'Show photos of Person 1'."
        else:
            try:
                person_id = int(person_id)
                person = Person.query.get(person_id)
                if person is None:
                    reply = f"I don't know anyone with id={person_id} yet."
                else:
                    name = person.name or f"Person {person.id}"
                    date_filter = intent_data.get("date_filter")  # e.g. "yesterday", "last_week", "last_month"
                    cutoff, filter_label = _date_cutoff(date_filter)

                    query = Photo.query.filter_by(person_id=person_id)
                    if cutoff:
                        query = query.filter(Photo.uploaded_at >= cutoff)
                    person_photos = query.order_by(Photo.uploaded_at.desc()).all()

                    photos = [_photo_dict(p) for p in person_photos]
                    scope = f" from {filter_label}" if filter_label else ""
                    reply = (
                        f"Found {len(photos)} photo(s) of {name}{scope}."
                        if photos
                        else f"No photos found for {name}{scope}."
                    )
            except Exception as exc:
                print("CHATBOT ERROR (search_person):", exc)
                logger.error("DB error for search_person: %s", exc)
                reply = "Database error while searching."

    elif intent == "search_date":
        target_date_str = intent_data.get("date", "")
        try:
            target_date = date.fromisoformat(target_date_str)
            next_day = target_date + timedelta(days=1)
            from sqlalchemy import and_
            day_photos = (
                Photo.query
                .filter(
                    and_(
                        Photo.uploaded_at >= target_date.isoformat(),
                        Photo.uploaded_at < next_day.isoformat(),
                    )
                )
                .order_by(Photo.uploaded_at.desc())
                .all()
            )
            photos = [_photo_dict(p) for p in day_photos]
            friendly = target_date.strftime("%B %d, %Y")
            reply = (
                f"Found {len(photos)} photo(s) from {friendly}."
                if photos
                else f"No photos found from {friendly}."
            )
        except ValueError:
            reply = (
                "I couldn't figure out the date. "
                "Try 'Show photos from yesterday' or 'Show photos from 2024-03-07'."
            )

    elif intent == "search_all":
        try:
            all_photos = Photo.query.order_by(Photo.uploaded_at.desc()).all()
            photos = [_photo_dict(p) for p in all_photos]
            reply = (
                f"Here are all {len(photos)} photo(s) in your gallery."
                if photos
                else "Your gallery is empty. Upload some photos to get started!"
            )
        except Exception as exc:
            print("CHATBOT ERROR (search_all):", exc)
            reply = "Database error while fetching photos."

    elif intent == "send_email":
        recipient = (intent_data.get("email") or "").strip()
        person_id  = intent_data.get("person_id")

        # Fallback: resolve by name when person_id is missing
        if person_id is None:
            person_name_hint = intent_data.get("person_name") or intent_data.get("name", "")
            matched = _find_person_by_name(person_name_hint, persons)
            if matched:
                person_id = matched["id"]

        if not recipient or "@" not in recipient:
            reply = "Please include a valid email address. Example: 'Send Person 1 photos to you@gmail.com'"
        elif person_id is None:
            reply = "I couldn't identify which person to send. Try 'Send Person 1 photos to you@gmail.com'"
        else:
            try:
                person_id = int(person_id)
                person = Person.query.get(person_id)
                if person is None:
                    reply = f"No person found with id={person_id}."
                else:
                    person_photos = (
                        Photo.query
                        .filter_by(person_id=person_id)
                        .order_by(Photo.uploaded_at.desc())
                        .all()
                    )
                    name = person.name or f"Person {person.id}"
                    if not person_photos:
                        reply = f"No photos found for {name} to send."
                    else:
                        paths = [p.filepath for p in person_photos if p.filepath]
                        try:
                            send_photos(recipient, paths, person_name=name)
                            reply = f"Done! Sent {len(paths)} photo(s) of {name} to {recipient}."
                            # ── Log delivery to database ──────────────────────
                            try:
                                from models.delivery_model import DeliveryHistory
                                from app.database import db
                                record = DeliveryHistory(
                                    person_id=person_id,
                                    person_name=name,
                                    email=recipient,
                                    photo_count=len(paths),
                                )
                                db.session.add(record)
                                db.session.commit()
                                print(f"[delivery] Logged delivery: {name} → {recipient} ({len(paths)} photos)")
                            except Exception as log_exc:
                                print(f"[delivery] WARNING: could not log delivery: {log_exc}")
                        except RuntimeError as exc:
                            print("CHATBOT ERROR (email creds):", exc)
                            reply = str(exc)
                        except Exception as exc:
                            print("CHATBOT ERROR (send_photos):", exc)
                            reply = f"Failed to send email: {exc}"
            except Exception as exc:
                print("CHATBOT ERROR (send_email DB):", exc)
                reply = "Database error while preparing photos for email."

    elif intent == "send_whatsapp":
        phone     = (intent_data.get("phone") or "").strip()
        person_id = intent_data.get("person_id")

        # Fallback: resolve by name when person_id is missing
        if person_id is None:
            person_name_hint = intent_data.get("person_name") or intent_data.get("name", "")
            matched = _find_person_by_name(person_name_hint, persons)
            if matched:
                person_id = matched["id"]

        if not phone or not phone.startswith("+"):
            reply = "Please include a phone number in international format. Example: 'Send Mom photos to WhatsApp +919876543210'"
        elif person_id is None:
            reply = "I couldn't identify which person to send. Try 'Send Mom photos to WhatsApp +919876543210'"
        else:
            try:
                person_id = int(person_id)
                person = Person.query.get(person_id)
                if person is None:
                    reply = f"No person found with id={person_id}."
                else:
                    person_photos = (
                        Photo.query
                        .filter_by(person_id=person_id)
                        .order_by(Photo.uploaded_at.desc())
                        .all()
                    )
                    name = person.name or f"Person {person.id}"
                    if not person_photos:
                        reply = f"No photos found for {name} to send."
                    else:
                        # Build public URLs (Twilio needs externally reachable URLs)
                        urls = [
                            f"{API_BASE}/uploads/{p.filename}"
                            for p in person_photos if p.filename
                        ]
                        try:
                            from services.whatsapp_service import send_whatsapp_photos
                            sent = send_whatsapp_photos(phone, urls, person_name=name)
                            reply = f"Done! Sent {sent} photo(s) of {name} to WhatsApp {phone}."
                            # ── Log delivery ──────────────────────────────────
                            try:
                                from models.delivery_model import DeliveryHistory
                                from app.database import db
                                db.session.add(DeliveryHistory(
                                    person_id=person_id,
                                    person_name=name,
                                    email=f"whatsapp:{phone}",
                                    photo_count=sent,
                                ))
                                db.session.commit()
                            except Exception as log_exc:
                                print(f"[delivery] WARNING: could not log WA delivery: {log_exc}")
                        except RuntimeError as exc:
                            print("CHATBOT ERROR (whatsapp creds):", exc)
                            reply = str(exc)
                        except Exception as exc:
                            print("CHATBOT ERROR (send_whatsapp):", exc)
                            reply = f"Failed to send WhatsApp message: {exc}"
            except Exception as exc:
                print("CHATBOT ERROR (send_whatsapp DB):", exc)
                reply = "Database error while preparing photos for WhatsApp."

    else:
        reply = (
            "I'm not sure what you're looking for. Try:\n"
            "- \"Show photos of Person 1\"\n"
            "- \"Show photos from yesterday\"\n"
            "- \"Show all photos\"\n"
            "- \"Send Person 1 photos to you@gmail.com\"\n"
            "- \"Send Mom photos to WhatsApp +919876543210\""
        )

    return jsonify({"reply": reply, "photos": photos}), 200


def _find_person_by_name(name: str, persons: list) -> dict | None:
    """
    Match a name string against the loaded persons list.
    Handles 'Person 1' style names and partial matches.
    """
    if not name:
        return None
    name_lower = name.strip().lower()
    for p in persons:
        if p["name"].lower() == name_lower:
            return p
    # Try partial match (e.g. "Mom" inside "Mom Smith")
    for p in persons:
        if name_lower in p["name"].lower():
            return p
    return None


def _photo_dict(photo) -> dict:
    """Convert a Photo model instance to a serialisable dict for the frontend."""
    return {
        "id": photo.id,
        "filename": photo.filename,
        "url": f"{API_BASE}/uploads/{photo.filename}",
        "uploaded_at": photo.uploaded_at.isoformat() if photo.uploaded_at else None,
    }


def _date_cutoff(date_filter: str | None):
    """
    Return (cutoff_datetime, label) for a named date filter.
    cutoff_datetime is UTC-naive and matches the stored `uploaded_at` values.
    Returns (None, None) when no filter is provided.
    """
    now = datetime.utcnow()
    filters = {
        "today":      (now.replace(hour=0, minute=0, second=0, microsecond=0), "today"),
        "yesterday":  (now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1), "yesterday"),
        "last_week":  (now - timedelta(days=7),  "the last 7 days"),
        "last_month": (now - timedelta(days=30), "the last 30 days"),
    }
    if date_filter and date_filter in filters:
        return filters[date_filter]
    return None, None
