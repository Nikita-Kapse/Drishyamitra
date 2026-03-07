import json
import logging
import numpy as np

logger = logging.getLogger(__name__)


def detect_faces(image_path: str) -> list:
    """
    Run face detection on *image_path* using DeepFace + RetinaFace.

    Returns a list of cropped face numpy arrays — one per detected face.
    Returns [] if no faces are found or if DeepFace raises an error.
    """
    try:
        from deepface import DeepFace
        import cv2

        img = cv2.imread(image_path)
        if img is None:
            logger.warning("cv2 could not read image %s", image_path)
            return []

        faces = DeepFace.extract_faces(
            img_path=image_path,
            detector_backend="retinaface",
            enforce_detection=False,   # don't raise if no face found
        )

        detected_faces = []
        for face in faces:
            if face.get("confidence", 1.0) < 0.5:
                continue
                
            # Extract coordinates
            area = face.get("facial_area", {})
            x = area.get("x", 0)
            y = area.get("y", 0)
            w = area.get("w", 0)
            h = area.get("h", 0)

            # Ensure valid dimensions
            if w <= 0 or h <= 0:
                continue

            # Crop directly from the original image array
            cropped = img[y:y+h, x:x+w]
            detected_faces.append(cropped)

        print(f"Faces detected: {len(detected_faces)}")
        logger.info("Faces detected: %d", len(detected_faces))
        return detected_faces

    except Exception as exc:
        logger.warning("Face detection failed for %s: %s", image_path, exc)
        print(f"Face detection skipped: {exc}")
        return []


def generate_embedding(face_img) -> list | None:
    """
    Generate a Facenet512 embedding vector for a single cropped face numpy array.

    `face_img` is a numpy array returned directly by detect_faces().
    Returns the embedding as a Python list, or None on failure.
    """
    try:
        from deepface import DeepFace
        import cv2

        # Resize the face exactly to the size FaceNet expects, and log it
        face_img = cv2.resize(face_img, (160, 160))
        print("Face crop shape:", face_img.shape)

        result = DeepFace.represent(
            img_path=face_img,
            model_name="Facenet512",
            enforce_detection=False,
        )

        embedding_vector = result[0]["embedding"]
        
        # Unit-normalize the embedding so Euclidean distance operates on a hypersphere
        # This makes the distance threshold much more stable across photos
        arr = np.array(embedding_vector, dtype=np.float64)
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr = arr / norm
        embedding_vector = arr.tolist()

        logger.info("Embedding created and normalized (dim=%d)", len(embedding_vector))
        print("Embedding created and normalized")
        return embedding_vector

    except Exception as exc:
        logger.warning("Embedding generation failed: %s", exc)
        print(f"Embedding generation failed: {exc}")
        return None


def embedding_to_json(vector: list) -> str:
    """Serialise a float list to a compact JSON string for DB storage."""
    return json.dumps(vector)


def json_to_embedding(text: str) -> list:
    """Deserialise a JSON string back to a float list."""
    return json.loads(text)
