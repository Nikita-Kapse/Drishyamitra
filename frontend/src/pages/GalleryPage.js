import React, { useEffect, useState, useCallback } from "react";
import "./GalleryPage.css";

const API_BASE = "http://localhost:5000/api";

export default function GalleryPage() {
  const [persons, setPersons] = useState([]);
  const [expanded, setExpanded] = useState({});   // personId → bool
  const [photos, setPhotos] = useState({});        // personId → [photo, …]
  const [loadingPhotos, setLoadingPhotos] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [renaming, setRenaming] = useState(null);  // personId being renamed
  const [renameVal, setRenameVal] = useState("");

  // Fetch person list
  const loadPersons = useCallback(() => {
    setLoading(true);
    fetch(`${API_BASE}/persons`)
      .then((r) => r.json())
      .then((data) => setPersons(data.persons || []))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadPersons(); }, [loadPersons]);

  // Toggle expand a person folder
  const toggleFolder = (id) => {
    const next = !expanded[id];
    setExpanded((prev) => ({ ...prev, [id]: next }));
    if (next && !photos[id]) {
      setLoadingPhotos((prev) => ({ ...prev, [id]: true }));
      fetch(`${API_BASE}/persons/${id}/photos`)
        .then((r) => r.json())
        .then((data) =>
          setPhotos((prev) => ({ ...prev, [id]: data.photos || [] }))
        )
        .finally(() =>
          setLoadingPhotos((prev) => ({ ...prev, [id]: false }))
        );
    }
  };

  // Start inline rename
  const startRename = (person, e) => {
    e.stopPropagation();
    setRenaming(person.id);
    setRenameVal(person.name);
  };

  // Commit rename
  const commitRename = async (personId) => {
    const name = renameVal.trim();
    if (!name) { setRenaming(null); return; }
    try {
      const res = await fetch(`${API_BASE}/persons/${personId}/rename`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      });
      if (!res.ok) throw new Error("Rename failed");
      setPersons((prev) =>
        prev.map((p) => (p.id === personId ? { ...p, name } : p))
      );
    } catch (err) {
      alert("Could not rename: " + err.message);
    } finally {
      setRenaming(null);
    }
  };

  const handleRenameKey = (e, personId) => {
    if (e.key === "Enter") commitRename(personId);
    if (e.key === "Escape") setRenaming(null);
  };

  if (loading)
    return <div className="gallery-status">Loading gallery…</div>;
  if (error)
    return <div className="gallery-status error">⚠️ {error}</div>;

  return (
    <div className="gallery-page">
      <h1 className="gallery-title">🖼️ Gallery</h1>
      <p className="gallery-count">
        {persons.length} person{persons.length !== 1 ? "s" : ""} detected
      </p>

      {persons.length === 0 ? (
        <p className="gallery-empty">No persons detected yet — go upload some photos! 📷</p>
      ) : (
        <div className="persons-list">
          {persons.map((person) => (
            <div key={person.id} className="person-folder">
              {/* ── Folder header ── */}
              <div
                className="person-header"
                onClick={() => toggleFolder(person.id)}
              >
                <span className="folder-icon">
                  {expanded[person.id] ? "📂" : "📁"}
                </span>

                {renaming === person.id ? (
                  <input
                    className="rename-input"
                    value={renameVal}
                    autoFocus
                    onChange={(e) => setRenameVal(e.target.value)}
                    onBlur={() => commitRename(person.id)}
                    onKeyDown={(e) => handleRenameKey(e, person.id)}
                    onClick={(e) => e.stopPropagation()}
                  />
                ) : (
                  <span className="person-name">{person.name}</span>
                )}

                <span className="photo-count-badge">
                  {person.photo_count} photo{person.photo_count !== 1 ? "s" : ""}
                </span>

                <button
                  className="rename-btn"
                  title="Rename person"
                  onClick={(e) => startRename(person, e)}
                >
                  ✏️ Rename
                </button>
              </div>

              {/* ── Photo grid (collapsed by default) ── */}
              {expanded[person.id] && (
                <div className="person-photos">
                  {loadingPhotos[person.id] ? (
                    <p className="loading-photos">Loading photos…</p>
                  ) : (photos[person.id] || []).length === 0 ? (
                    <p className="loading-photos">No photos found.</p>
                  ) : (
                    <div className="gallery-grid">
                      {(photos[person.id] || []).map((photo) => (
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
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
