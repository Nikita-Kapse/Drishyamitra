from datetime import datetime
from app.database import db


class Photo(db.Model):
    __tablename__ = "photos"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(512), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # FK → persons.id (nullable: photo may have no detected face)
    person_id = db.Column(db.Integer, db.ForeignKey("persons.id"), nullable=True)

    # Relationships
    person = db.relationship("Person", back_populates="photos")
    embeddings = db.relationship("Embedding", back_populates="photo", cascade="all, delete-orphan")


    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "filepath": self.filepath,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }

    def __repr__(self):
        return f"<Photo id={self.id} filename={self.filename}>"
