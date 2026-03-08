import os
import smtplib
import mimetypes
from email.message import EmailMessage


def send_photos(recipient_email: str, photo_paths: list[str], person_name: str = "Someone") -> None:
    """
    Send photo files as email attachments via Gmail SMTP SSL.

    :param recipient_email: destination email address
    :param photo_paths:     list of absolute file paths to attach
    :param person_name:     used in the subject / body
    :raises RuntimeError:   if credentials are missing
    :raises Exception:      on SMTP / IO errors
    """
    # Read at call time so load_dotenv() has already run
    EMAIL_USER = os.getenv("GMAIL_USER", "").strip()
    EMAIL_PASS = os.getenv("GMAIL_APP_PASSWORD", "").strip()

    if not EMAIL_USER or not EMAIL_PASS:
        raise RuntimeError(
            "Gmail credentials are not configured. "
            "Set GMAIL_USER and GMAIL_APP_PASSWORD in backend/.env"
        )

    if not photo_paths:
        raise ValueError("No photos to send.")

    msg = EmailMessage()
    msg["Subject"] = f"Drishyamitra – Photos of {person_name}"
    msg["From"] = EMAIL_USER
    msg["To"] = recipient_email
    msg.set_content(
        f"Hi!\n\n"
        f"Here are {len(photo_paths)} photo(s) of {person_name} from Drishyamitra.\n\n"
        f"– Drishyamitra AI"
    )

    attached = 0
    for path in photo_paths:
        if not os.path.isfile(path):
            print(f"[email_service] Skipping missing file: {path}")
            continue

        mime_type, _ = mimetypes.guess_type(path)
        maintype, subtype = (mime_type or "image/jpeg").split("/", 1)
        filename = os.path.basename(path)

        with open(path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype=maintype,
                subtype=subtype,
                filename=filename,
            )
        attached += 1

    if attached == 0:
        raise FileNotFoundError("None of the photo files could be found on disk.")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)

    print(f"[email_service] Sent {attached} photo(s) to {recipient_email}")
