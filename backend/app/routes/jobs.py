from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from app.services.job_search_service import search_jobs_from_resume

router = APIRouter()


class ResumeProfile(BaseModel):
    roles: List[str] = []
    skills: List[str] = []
    experience_years: int = 0
    education: List[str] = []
    preferred_locations: List[str] = []
    seniority_level: str = ""


@router.post("/jobs")
async def find_jobs(profile: ResumeProfile):
    """
    Step 2 of the pipeline:
    - Receives parsed profile from /upload-resume
    - Generates search queries
    - Scrapes LinkedIn
    - Returns deduplicated job listings
    """

    # ✅ Guard against empty profile — nothing useful to search with
    if not profile.roles and not profile.skills:
        raise HTTPException(
            status_code=400,
            detail="Profile must contain at least roles or skills to search jobs."
        )

    try:
        jobs = await search_jobs_from_resume(profile.dict())

        return {
            "total": len(jobs),
            "results": jobs
        }

    except Exception as e:
        print(f"❌ Job search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Job search failed: {str(e)}"
        )