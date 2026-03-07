import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchPersons } from "../services/photoService";
import "./PeoplePage.css";

export default function PeoplePage() {
  const [persons, setPersons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchPersons()
      .then(setPersons)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="people-status">Loading people…</div>;
  if (error)   return <div className="people-status error">⚠️ {error}</div>;

  return (
    <div className="people-page">
      <h1 className="people-title">👤 People</h1>
      <p className="people-subtitle">
        {persons.length} {persons.length === 1 ? "person" : "people"} detected
      </p>

      {persons.length === 0 ? (
        <p className="people-empty">
          No people detected yet — upload some photos first! 📷
        </p>
      ) : (
        <div className="people-grid">
          {persons.map((person) => (
            <div
              key={person.id}
              className="person-card"
              onClick={() => navigate(`/people/${person.id}`)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === "Enter" && navigate(`/people/${person.id}`)}
            >
              <div className="person-avatar">
                <span className="person-avatar-icon">👤</span>
              </div>
              <div className="person-info">
                <span className="person-name">{person.name}</span>
                <span className="person-count">
                  {person.photo_count} {person.photo_count === 1 ? "photo" : "photos"}
                </span>
              </div>
              <div className="person-arrow">→</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
