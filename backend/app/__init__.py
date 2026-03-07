from flask import Flask
from flask_cors import CORS
from .config import Config
from .database import db
import os


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure the upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Enable CORS for all routes
    CORS(app)

    # Initialize database
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Register blueprints
    from routes.photo_routes import photo_bp
    app.register_blueprint(photo_bp, url_prefix="/api")

    @app.route("/")
    def index():
        return {"message": "Drishyamitra API is running 🚀", "status": "ok"}

    return app
