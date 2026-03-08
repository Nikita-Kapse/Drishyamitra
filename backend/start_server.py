import sys
import os
from dotenv import load_dotenv

# Load .env before anything else so os.getenv() works everywhere (incl. Groq key)
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# Ensure backend root is on the path so app/ can import models/, routes/, etc.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.database import db
from routes.photo_routes import photo_bp

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")


def _run_migrations(app):
    """
    Safe, idempotent schema migrations for SQLite.
    SQLAlchemy's create_all() only creates missing *tables* — it never alters
    existing ones.  We handle new columns here with plain SQL so the server
    starts cleanly even against an older database file.
    """
    with app.app_context():
        from app.database import db
        conn = db.engine.raw_connection()
        try:
            cur = conn.cursor()
            # Add person_id to photos if it doesn't exist yet
            cur.execute("PRAGMA table_info(photos)")
            col_names = [row[1] for row in cur.fetchall()]
            if "person_id" not in col_names:
                cur.execute(
                    "ALTER TABLE photos ADD COLUMN person_id INTEGER REFERENCES persons(id)"
                )
                conn.commit()
                print("[OK] Migration: added person_id column to photos table.")
            else:
                print("[OK] Migration: person_id column already present.")
        finally:
            conn.close()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Explicit CORS — allows the React dev server on port 3000 and any other origin
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        supports_credentials=False,
    )

    db.init_app(app)

    with app.app_context():
        # Import all models so SQLAlchemy registers them before create_all
        from models.photo_model import Photo               # noqa: F401
        from models.person_model import Person             # noqa: F401
        from models.embedding_model import Embedding       # noqa: F401
        from models.delivery_model import DeliveryHistory  # noqa: F401
        db.create_all()
        print("[OK] Database tables created / verified.")

    # Run incremental schema migrations (safe to call every startup)
    _run_migrations(app)

    app.register_blueprint(photo_bp, url_prefix="/api")

    from routes.person_routes import person_bp
    app.register_blueprint(person_bp, url_prefix="/api")

    from routes.chat_routes import chat_bp
    app.register_blueprint(chat_bp, url_prefix="/api")

    @app.route("/")
    def index():
        return {"message": "Drishyamitra API is running", "status": "ok"}

    return app


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 10000))
    print(f"[OK] Drishyamitra backend running on port {port}")
    app.run(host="0.0.0.0", port=port)
