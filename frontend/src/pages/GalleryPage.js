import React, { useEffect, useState } from "react";
import { fetchPhotos } from "../services/photoService";
import "./GalleryPage.css";

const API_BASE = "http://localhost:5000/api";

export default function GalleryPage() {
  const [photos, setPhotos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPhotos()
      .then(setPhotos)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="gallery-status">Loading gallery…</div>;
  }

  if (error) {
    return (
      <div className="gallery-status error">
        ⚠️ {error}
      </div>
    );
  }

  return (
    <div className="gallery-page">
      <h1 className="gallery-title">🖼️ Gallery</h1>
      <p className="gallery-count">{photos.length} photo{photos.length !== 1 ? "s" : ""}</p>

      {photos.length === 0 ? (
        <p className="gallery-empty">No photos yet — go upload some! 📷</p>
      ) : (
        <div className="gallery-grid">
          {photos.map((photo) => (
            <div key={photo.id} className="gallery-card">
              <div className="gallery-img-wrap">
                <img
                  src={`${API_BASE}/uploads/${photo.filename}`}
                  alt={photo.filename}
                  className="gallery-img"
                />
              </div>
              <div className="gallery-info">
                <span className="gallery-filename" title={photo.filename}>
                  {photo.filename}
                </span>
                <span className="gallery-date">
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
