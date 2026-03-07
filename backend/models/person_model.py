from datetime import datetime
from app.database import db


class Person(db.Model):
    __tablename__ = "persons"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)   # filled later during recognition
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship: one Person has many Embeddings
    embeddings = db.relationship("Embedding", back_populates="person", cascade="all, delete-orphan")

    # Relationship: one Person appears in many Photos
    photos = db.relationship("Photo", back_populates="person")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Person id={self.id} name={self.name}>"
