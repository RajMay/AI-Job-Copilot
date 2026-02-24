from fastapi import APIRouter, UploadFile, File
import os

from app.services.parser import extract_text
from app.services.gemini_service import extract_resume_profile

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):

    # ✅ Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # ✅ Step 1 — Extract text from resume
    try:
        resume_text = extract_text(file_path)
    except Exception as e:
        return {"error": f"Text extraction failed: {str(e)}"}

    # ✅ Step 2 — Extract structured profile using LLM
    profile = extract_resume_profile(resume_text)

    # ✅ Return ONLY useful data
    return {
        "filename": file.filename,
        "profile": profile
    }