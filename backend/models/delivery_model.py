from datetime import datetime
from app.database import db


class DeliveryHistory(db.Model):
    """Tracks every successful photo-email delivery."""

    __tablename__ = "delivery_history"

    id          = db.Column(db.Integer, primary_key=True)
    person_id   = db.Column(db.Integer, nullable=True)
    person_name = db.Column(db.String(100), nullable=True)
    email       = db.Column(db.String(200), nullable=False)
    photo_count = db.Column(db.Integer, nullable=False, default=0)
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id":          self.id,
            "person_id":   self.person_id,
            "person_name": self.person_name,
            "email":       self.email,
            "photo_count": self.photo_count,
            "timestamp":   self.timestamp.isoformat() if self.timestamp else None,
        }
