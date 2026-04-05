from typing import Dict, List

from app.scrapers.job_scraper import search_jobs
from app.services.groq_service import generate_job_queries
from app.services.location_filter import filter_jobs_by_india_options


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
    st_list = [s.strip() for s in (profile.get("india_states") or []) if s and str(s).strip()]
    if profile.get("india_only") or st_list:
        all_jobs = filter_jobs_by_india_options(
            all_jobs,
            india_only=bool(profile.get("india_only")),
            india_states=st_list if st_list else None,
        )
        print(f"✅ After India / state filter: {len(all_jobs)}")
    return all_jobs