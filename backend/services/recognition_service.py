import logging
import json
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
import numpy as np

logger = logging.getLogger(__name__)

# Distance threshold — faces with Euclidean distance <= 0.8 are considered the same person
DISTANCE_THRESHOLD = 0.8


def compute_distance(vec1: list, vec2: list) -> float:
    """
    Compute Euclidean distance between two embedding vectors.
    Returns a float >= 0; lower = more similar (closer).
    """
    a = np.array(vec1, dtype=np.float64)
    b = np.array(vec2, dtype=np.float64)
    distance = np.linalg.norm(a - b)
    return float(distance)


def find_matching_person(new_embedding: list) -> int | None:
    """
    Compare *new_embedding* against every stored embedding in the database.

    Returns the `person_id` whose stored embedding is most similar to
    *new_embedding* (and whose similarity exceeds SIMILARITY_THRESHOLD).
    Returns None if no match is found.
    """
    # Import inside function to avoid circular-import issues at module load time
    from models.embedding_model import Embedding

    all_embeddings = Embedding.query.filter(Embedding.person_id.isnot(None)).all()

    best_score = float("inf")
    best_person_id = None

    for stored in all_embeddings:
        try:
            stored_vector = json.loads(stored.embedding)
        except (json.JSONDecodeError, TypeError):
            logger.warning("Skipping malformed embedding id=%d", stored.id)
            continue

        distance = compute_distance(new_embedding, stored_vector)
        print(f"New embedding sample:    {[round(x,4) for x in new_embedding[:5]]}")
        print(f"Stored embedding sample: {[round(x,4) for x in stored_vector[:5]]}")
        print(f"Distance score: {distance:.4f}  (embedding id={stored.id}, person_id={stored.person_id})")
        logger.debug(
            "Comparing with embedding id=%d (person_id=%d): distance=%.4f",
            stored.id,
            stored.person_id,
            distance,
        )

        if distance < best_score:
            best_score = distance
            best_person_id = stored.person_id

    if best_score <= DISTANCE_THRESHOLD:
        logger.info(
            "Matched existing person: %d (distance=%.4f)", best_person_id, best_score
        )
        print(f"Matched existing person with distance {best_score:.4f} → person_id={best_person_id}")
        return best_person_id

    logger.info("No matching person found (best distance=%.4f)", best_score)
    print("No matching person found")
    return None
