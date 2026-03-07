from datetime import datetime
from app.database import db


class Embedding(db.Model):
    __tablename__ = "embeddings"

    id = db.Column(db.Integer, primary_key=True)

    # FK → persons.id  (nullable: embedding saved before person is identified)
    person_id = db.Column(db.Integer, db.ForeignKey("persons.id"), nullable=True)

    # FK → photos.id
    photo_id = db.Column(db.Integer, db.ForeignKey("photos.id"), nullable=False)

    # JSON-serialised float list, e.g. "[0.123, -0.456, …]"
    embedding = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    person = db.relationship("Person", back_populates="embeddings")
    photo  = db.relationship("Photo",  back_populates="embeddings")

    def to_dict(self):
        return {
            "id": self.id,
            "person_id": self.person_id,
            "photo_id": self.photo_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            # embedding vector deliberately omitted from public dict (very large)
        }

    def __repr__(self):
        return f"<Embedding id={self.id} photo_id={self.photo_id} person_id={self.person_id}>"
