from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

# Load model ONCE globally (important)
model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(text_chunks: List[str]) -> List[List[float]]:
    """
    Convert text chunks into vector embeddings.

    Args:
        text_chunks: List of text strings

    Returns:
        List of embedding vectors
    """

    if not text_chunks:
        return []

    embeddings = model.encode(
        text_chunks,
        batch_size=32,
        show_progress_bar=False,
        convert_to_numpy=True
    )

    # Convert numpy arrays → Python lists (needed for Pinecone)
    return embeddings.tolist()
