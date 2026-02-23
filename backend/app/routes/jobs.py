from fastapi import APIRouter
from pydantic import BaseModel
from app.scrapers.job_scraper import search_jobs

router = APIRouter()


class JobQuery(BaseModel):
    query: str


@router.post("/jobs")
async def find_jobs(data: JobQuery):

    print("🔎 Query:", data.query)

    jobs = await search_jobs(data.query)

    print("📦 Jobs returned:", jobs)

    return {"results": jobs}



   