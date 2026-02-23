from fastapi import APIRouter, UploadFile, File
import os
from app.rag.pinecone_store import store_resume_embeddings


from app.services.parser import extract_text
from app.services.gemini_service import extract_resume_profile

from app.rag.chunker import chunk_text
from app.rag.embeddding import create_embeddings


router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):

    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Step 1 — Extract text
    try:
        resume_text = extract_text(file_path)
    except Exception as e:
        return {"error": f"Text extraction failed: {str(e)}"}

    # Step 2 — Structured profile via Gemini
    profile = extract_resume_profile(resume_text)

    # Step 3 — Chunk text
    from app.utils.chunking import recursive_chunk_text
    chunks = recursive_chunk_text(resume_text)

    # Step 4 — Create embeddings
    embeddings = create_embeddings(chunks)

    return {
        "filename": file.filename,
        "profile": profile,
        "num_chunks": len(chunks),
        "embedding_dim": len(embeddings[0])
    }
    
    
