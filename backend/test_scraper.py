import asyncio
import sys

# ⭐ CRITICAL FIX FOR WINDOWS + PYTHON 3.12 + PLAYWRIGHT
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

from app.scrapers.job_scraper import search_jobs


async def main():

    query = "AI engineer jobs Bangalore"

    results = await search_jobs(query)

    print("\n===== SCRAPER RESULTS =====\n")

    for job in results:
        print(job)


# ⭐ DO NOT use asyncio.run() on Windows here
if __name__ == "__main__":
    import sys

    # ⭐ REQUIRED for Windows + Python 3.12 + Playwright
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy()
        )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
