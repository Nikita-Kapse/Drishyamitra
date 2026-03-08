import os
from twilio.rest import Client


def send_whatsapp_photos(phone: str, photo_urls: list[str], person_name: str = "Someone") -> int:
    """
    Send photos via WhatsApp using Twilio Sandbox / Business API.

    :param phone:       Destination phone number, e.g. "+919876543210"
    :param photo_urls:  Publicly-accessible URLs for each photo
    :param person_name: Used in the caption message
    :returns:           Number of messages sent
    :raises RuntimeError: if Twilio credentials are missing
    :raises Exception:    on Twilio API errors
    """
    # Read at call time so load_dotenv() has already run
    sid    = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    token  = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    sender = os.getenv("TWILIO_WHATSAPP_NUMBER", "").strip()

    if not sid or not token or not sender:
        raise RuntimeError(
            "Twilio credentials are not configured. "
            "Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_WHATSAPP_NUMBER in backend/.env"
        )

    if not phone.startswith("+"):
        raise ValueError(f"Phone number must be in E.164 format (e.g. +919876543210), got: {phone!r}")

    if not photo_urls:
        raise ValueError("No photo URLs to send.")

    client = Client(sid, token)
    from_wa = f"whatsapp:{sender}"
    to_wa   = f"whatsapp:{phone}"

    sent = 0
    for i, url in enumerate(photo_urls):
        body = (
            f"📷 Photo {i + 1}/{len(photo_urls)} of {person_name} — from Drishyamitra"
            if i == 0
            else f"📷 Photo {i + 1}/{len(photo_urls)} of {person_name}"
        )
        client.messages.create(
            from_=from_wa,
            to=to_wa,
            body=body,
            media_url=[url],
        )
        sent += 1

    print(f"[whatsapp_service] Sent {sent} photo(s) to {phone}")
    return sent
