from fastapi import FastAPI
from app.routes import resume
from app.routes import query
from app.routes import jobs
from app.routes import ai_job
import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )



app = FastAPI(title="AI Job Copilot API")

app.include_router(resume.router)

app.include_router(query.router)
app.include_router(jobs.router)
app.include_router(ai_job.router)

