from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter


def recursive_chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[str]:
    """
    Chunk text using LangChain RecursiveCharacterTextSplitter.

    Best general-purpose chunking for RAG systems.
    """

    if not text:
        return []

    splitter = RecursiveCharacterTextSplitter(

        # Order matters (largest semantic → smallest)
        separators=[
            "\n\n",  # Paragraphs
            "\n",    # Lines
            ". ",    # Sentences
            " ",     # Words
            ""       # Characters
        ],

        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = splitter.split_text(text)

    return chunks