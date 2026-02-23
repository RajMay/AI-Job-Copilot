from fastapi import APIRouter
from pydantic import BaseModel

from app.services.job_search_service import search_jobs_from_resume

router = APIRouter()


# ⭐ Input schema
class ResumeProfile(BaseModel):
    profile: dict


# ⭐ Endpoint
@router.post("/jobs-from-resume")
async def jobs_from_resume(data: ResumeProfile):

    jobs = await search_jobs_from_resume(data.profile)

    return {"results": jobs}