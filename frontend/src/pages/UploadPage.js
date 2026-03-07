import React, { useState } from "react";
import { uploadPhoto } from "../services/photoService";
import "./UploadPage.css";

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null); // { type: "success"|"error", text }

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));
    setMessage(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage({ type: "error", text: "Please select a photo first." });
      return;
    }
    setUploading(true);
    setMessage(null);
    try {
      await uploadPhoto(selectedFile);
      setMessage({ type: "success", text: "✅ Photo uploaded successfully!" });
      setSelectedFile(null);
      setPreview(null);
      // Reset the file input
      document.getElementById("photo-input").value = "";
    } catch (err) {
      setMessage({ type: "error", text: err.message || "Upload failed." });
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="upload-page">
      <div className="upload-card">
        <h1 className="upload-title">📸 Upload Photo</h1>
        <p className="upload-subtitle">Add photos to your Drishyamitra gallery</p>

        <label className="drop-zone" htmlFor="photo-input">
          {preview ? (
            <img src={preview} alt="Preview" className="preview-image" />
          ) : (
            <div className="drop-placeholder">
              <span className="drop-icon">🖼️</span>
              <span>Click to select a photo</span>
              <small>JPG, JPEG or PNG only</small>
            </div>
          )}
        </label>

        <input
          id="photo-input"
          type="file"
          accept=".jpg,.jpeg,.png"
          onChange={handleFileChange}
          style={{ display: "none" }}
        />

        {selectedFile && (
          <p className="file-name">
            Selected: <strong>{selectedFile.name}</strong>
          </p>
        )}

        <button
          className="upload-btn"
          onClick={handleUpload}
          disabled={uploading}
        >
          {uploading ? "Uploading…" : "Upload Photo"}
        </button>

        {message && (
          <div className={`upload-message ${message.type}`}>{message.text}</div>
        )}
      </div>
    </div>
  );
}
