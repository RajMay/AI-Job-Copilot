from app.services.query_generator import generate_job_queries
from app.scrapers.job_scraper import search_jobs


async def search_jobs_from_resume(profile: dict):

    queries = generate_job_queries(profile)

    all_jobs = []

    for q in queries:
        jobs = await search_jobs(q)
        all_jobs.extend(jobs)

    return all_jobs