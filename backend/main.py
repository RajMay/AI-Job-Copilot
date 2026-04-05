from fastapi import FastAPI
from app.routes import resume, jobs, company_jobs
import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(title="AI Job Copilot API")

app.include_router(resume.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(company_jobs.router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "running"}