from typing import List


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> List[str]:
    """
    Split text into overlapping chunks.

    Args:
        text: Input text
        chunk_size: Size of each chunk (characters)
        overlap: Overlap between chunks

    Returns:
        List of text chunks
    """

    if not text:
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks
