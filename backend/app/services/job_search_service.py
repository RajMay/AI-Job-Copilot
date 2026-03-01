from app.services.groq_service import generate_job_queries
from app.scrapers.job_scraper import search_jobs
from typing import List, Dict


async def search_jobs_from_resume(profile: dict) -> List[Dict]:
    """
    Generate job search queries from a parsed resume profile,
    scrape LinkedIn for each, deduplicate, and return results.
    """

    

    queries = generate_job_queries(profile)
    print(f"🧠 Generated {len(queries)} queries: {queries}")

    all_jobs = []
    seen_links = set()  # ✅ Track seen job links to deduplicate

    for query in queries:
        try:
            jobs = await search_jobs(query)

            for job in jobs:
                link = job.get("link", "")
                # ✅ Skip duplicates based on job link
                if link and link != "N/A" and link not in seen_links:
                    seen_links.add(link)
                    all_jobs.append(job)

        except Exception as e:
            # ✅ One failing query doesn't crash the entire search
            print(f"⚠️ Query '{query}' failed: {e}")
            continue

    print(f"✅ Total unique jobs found: {len(all_jobs)}")
    return all_jobs