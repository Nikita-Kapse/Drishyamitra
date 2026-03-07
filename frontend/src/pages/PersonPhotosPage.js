import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchPersonPhotos } from "../services/photoService";
import "./PeoplePage.css";

const API_BASE = "http://localhost:5000/api";

export default function PersonPhotosPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPersonPhotos(id)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="people-status">Loading photos…</div>;
  if (error)   return <div className="people-status error">⚠️ {error}</div>;

  const { person, photos } = data;

  return (
    <div className="people-page">
      <button className="person-back-btn" onClick={() => navigate("/people")}>
        ← Back to People
      </button>

      <h1 className="people-title">👤 {person.name}</h1>
      <p className="people-subtitle">
        {photos.length} {photos.length === 1 ? "photo" : "photos"}
      </p>

      {photos.length === 0 ? (
        <p className="people-empty">No photos found for this person.</p>
      ) : (
        <div className="person-photos-grid">
          {photos.map((photo) => (
            <div key={photo.id} className="person-photo-card">
              <div className="person-photo-wrap">
                <img
                  src={`${API_BASE}/uploads/${photo.filename}`}
                  alt={photo.filename}
                  className="person-photo-img"
                />
              </div>
              <div className="person-photo-info">
                <span className="person-photo-date">
                  {photo.uploaded_at
                    ? new Date(photo.uploaded_at).toLocaleString()
                    : "—"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
