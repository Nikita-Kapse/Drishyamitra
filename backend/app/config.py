import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "drishyamitra-secret-key")
    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///drishyamitra.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload folder
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads"))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "bmp", "tiff"}

    # Groq API
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

    # Gmail (for photo delivery)
    GMAIL_USER = os.getenv("GMAIL_USER", "")
    GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
