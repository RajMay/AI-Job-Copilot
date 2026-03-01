import os
import shutil
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.parser import extract_text
from app.services.groq_service import extract_resume_profile  # ✅ Fixed import path

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Step 1 of the pipeline:
    - Accept resume file
    - Extract raw text
    - Parse structured profile via Groq
    - Return profile (jobs.py handles the scraping step)
    """

    # ✅ Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: .pdf, .docx, .txt"
        )

    # ✅ Unique filename to prevent collisions between concurrent uploads
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # ✅ Stream file to disk instead of loading it all into memory
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"📄 Resume saved: {file_path}")

        # Step 1: Extract text
        resume_text = extract_text(file_path)

        if not resume_text.strip():
            raise HTTPException(
                status_code=422,
                detail="No text could be extracted. Is this a scanned image PDF?"
            )

        print(f"📝 Extracted {len(resume_text)} characters")

        # Step 2: Parse profile via Groq
        profile = extract_resume_profile(resume_text)

        if "error" in profile:
            raise HTTPException(
                status_code=502,
                detail=f"LLM profile extraction failed: {profile['error']}"
            )

        return {
            "filename": file.filename,  # ✅ Original name for display purposes
            "profile": profile
        }

    except HTTPException:
        raise  # ✅ Re-raise HTTP exceptions as-is without wrapping

    except Exception as e:
        print(f"❌ Resume processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error processing resume: {str(e)}"
        )

    finally:
        # ✅ Always delete the file from disk after processing
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Cleaned up: {file_path}")