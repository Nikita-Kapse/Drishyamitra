const API_BASE = "http://localhost:5000/api";

/**
 * Upload a single image file to the backend.
 * @param {File} file
 */
export async function uploadPhoto(file) {
  const formData = new FormData();
  formData.append("photo", file);

  const res = await fetch(`${API_BASE}/upload-photo`, {
    method: "POST",
    body: formData,
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.message || "Upload failed");
  return data;
}

/**
 * Fetch all photos from the backend.
 */
export async function fetchPhotos() {
  const res = await fetch(`${API_BASE}/photos`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.message || "Failed to fetch photos");
  return data.photos; // array of photo objects
}

/**
 * Fetch all detected persons with photo counts.
 */
export async function fetchPersons() {
  const res = await fetch(`${API_BASE}/persons`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.message || "Failed to fetch persons");
  return data.persons;
}

/**
 * Fetch all photos belonging to a specific person.
 * @param {number} personId
 */
export async function fetchPersonPhotos(personId) {
  const res = await fetch(`${API_BASE}/persons/${personId}/photos`);
  const data = await res.json();
  if (!res.ok) throw new Error(data.message || "Failed to fetch person photos");
  return data; // { person, photos }
}

