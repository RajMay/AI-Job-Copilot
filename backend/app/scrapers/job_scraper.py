# import asyncio
# from typing import List, Dict
# import requests
# from bs4 import BeautifulSoup


# HEADERS = {
#     "User-Agent": (
#         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#         "AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/120.0.0.0 Safari/537.36"
#     ),
#     "Accept-Language": "en-US,en;q=0.9",
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
# }


# def build_linkedin_url(query: str) -> str:
#     encoded_query = query.replace(" ", "%20")
#     return (
#         f"https://www.linkedin.com/jobs/search"
#         f"?keywords={encoded_query}&location=Worldwide&trk=public_jobs_jobs-search-bar_search-submit"
#     )


# def build_indeed_url(query: str) -> str:
#     encoded_query = query.replace(" ", "+")
#     return f"https://www.indeed.com/jobs?q={encoded_query}&l=&sort=date"


# def fetch_linkedin_jobs(query: str) -> List[Dict]:
#     """Scrape LinkedIn public jobs page using requests (no browser needed)."""
#     url = build_linkedin_url(query)
#     print(f"🔎 LinkedIn URL: {url}")

#     try:
#         response = requests.get(url, headers=HEADERS, timeout=15)
#         print(f"📡 LinkedIn status: {response.status_code}")

#         if response.status_code != 200:
#             print(f"⚠️ LinkedIn returned {response.status_code}")
#             return []

#         soup = BeautifulSoup(response.text, "lxml")
#         job_cards = soup.find_all("div", class_="base-card")

#         if not job_cards:
#             job_cards = soup.find_all("li", class_="jobs-search-results__list-item")

#         print(f"📦 Found {len(job_cards)} LinkedIn job cards")

#         jobs = []
#         for card in job_cards:
#             try:
#                 title = card.find("h3")
#                 company = card.find("h4")
#                 location = card.find("span", class_="job-search-card__location")
#                 link = card.find("a", href=True)

#                 job = {
#                     "title": title.get_text(strip=True) if title else "N/A",
#                     "company": company.get_text(strip=True) if company else "N/A",
#                     "location": location.get_text(strip=True) if location else "N/A",
#                     "link": link["href"] if link else "N/A",
#                     "source": "LinkedIn"
#                 }

#                 if job["title"] == "N/A" and job["company"] == "N/A":
#                     continue

#                 jobs.append(job)

#             except Exception:
#                 continue

#         return jobs[:30]

#     except Exception as e:
#         print(f"❌ LinkedIn scrape failed: {e}")
#         return []


# def fetch_indeed_jobs(query: str) -> List[Dict]:
#     """Scrape Indeed jobs as fallback."""
#     url = build_indeed_url(query)
#     print(f"🔎 Indeed URL: {url}")

#     try:
#         response = requests.get(url, headers=HEADERS, timeout=15)
#         print(f"📡 Indeed status: {response.status_code}")

#         if response.status_code != 200:
#             return []

#         soup = BeautifulSoup(response.text, "lxml")
#         job_cards = soup.find_all("div", class_="job_seen_beacon")

#         print(f"📦 Found {len(job_cards)} Indeed job cards")

#         jobs = []
#         for card in job_cards:
#             try:
#                 title = card.find("h2", class_="jobTitle")
#                 company = card.find("span", {"data-testid": "company-name"})
#                 location = card.find("div", {"data-testid": "text-location"})
#                 link_tag = card.find("a", href=True)

#                 link = (
#                     "https://www.indeed.com" + link_tag["href"]
#                     if link_tag and link_tag["href"].startswith("/")
#                     else link_tag["href"] if link_tag else "N/A"
#                 )

#                 job = {
#                     "title": title.get_text(strip=True) if title else "N/A",
#                     "company": company.get_text(strip=True) if company else "N/A",
#                     "location": location.get_text(strip=True) if location else "N/A",
#                     "link": link,
#                     "source": "Indeed"
#                 }

#                 if job["title"] == "N/A" and job["company"] == "N/A":
#                     continue

#                 jobs.append(job)

#             except Exception:
#                 continue

#         return jobs[:30]

#     except Exception as e:
#         print(f"❌ Indeed scrape failed: {e}")
#         return []


# async def search_jobs(query: str) -> List[Dict]:
#     """
#     Search for jobs using requests (no browser required).
#     Tries LinkedIn first, falls back to Indeed if LinkedIn returns nothing.
#     """
#     loop = asyncio.get_event_loop()

#     # ✅ Run blocking requests in thread pool so we don't block FastAPI
#     jobs = await loop.run_in_executor(None, fetch_linkedin_jobs, query)

#     if not jobs:
#         print(f"⚠️ LinkedIn returned 0 jobs, trying Indeed...")
#         jobs = await loop.run_in_executor(None, fetch_indeed_jobs, query)

#     print(f"✅ Total jobs found for '{query}': {len(jobs)}")
#     return jobs

import asyncio
from typing import List, Dict
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com/",
}


# ============================================================
# 🔗 URL BUILDERS
# ============================================================

def build_linkedin_url(query: str) -> str:
    q = query.replace(" ", "%20")
    return f"https://www.linkedin.com/jobs/search?keywords={q}&location=Worldwide"

def build_indeed_url(query: str) -> str:
    q = query.replace(" ", "+")
    return f"https://www.indeed.com/jobs?q={q}&l=&sort=date"

def build_glassdoor_url(query: str) -> str:
    q = query.replace(" ", "-")
    return f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query.replace(' ', '%20')}&locT=N&locId=1"

def build_remoteok_url(query: str) -> str:
    q = query.replace(" ", "-").lower()
    return f"https://remoteok.com/remote-{q}-jobs"

def build_weworkremotely_url(query: str) -> str:
    q = query.replace(" ", "+")
    return f"https://weworkremotely.com/remote-jobs/search?term={q}"

def build_naukri_url(query: str) -> str:
    q = query.replace(" ", "-").lower()
    return f"https://www.naukri.com/{q}-jobs"

def build_foundit_url(query: str) -> str:
    q = query.replace(" ", "%20")
    return f"https://www.foundit.in/srp/results?query={q}"

def build_github_jobs_url(query: str) -> str:
    q = query.replace(" ", "+")
    return f"https://jobs.github.com/positions?description={q}&location=worldwide"

def build_simplyhired_url(query: str) -> str:
    q = query.replace(" ", "+")
    return f"https://www.simplyhired.com/search?q={q}&l="

def build_careerjet_url(query: str) -> str:
    q = query.replace(" ", "+")
    return f"https://www.careerjet.com/search/jobs?s={q}&l=worldwide"


# ============================================================
# 🕷️ SCRAPERS
# ============================================================

def fetch_linkedin_jobs(query: str) -> List[Dict]:
    url = build_linkedin_url(query)
    print(f"🔎 [LinkedIn] {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        print(f"📡 [LinkedIn] Status: {r.status_code}")
        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.find_all("div", class_="base-card") or \
                soup.find_all("li", class_="jobs-search-results__list-item")
        print(f"📦 [LinkedIn] {len(cards)} cards found")

        jobs = []
        for card in cards:
            try:
                title = card.find("h3")
                company = card.find("h4")
                location = card.find("span", class_="job-search-card__location")
                link = card.find("a", href=True)
                job = {
                    "title": title.get_text(strip=True) if title else "N/A",
                    "company": company.get_text(strip=True) if company else "N/A",
                    "location": location.get_text(strip=True) if location else "N/A",
                    "link": link["href"] if link else "N/A",
                    "source": "LinkedIn"
                }
                if job["title"] != "N/A" or job["company"] != "N/A":
                    jobs.append(job)
            except Exception:
                continue
        return jobs[:30]
    except Exception as e:
        print(f"❌ [LinkedIn] {e}")
        return []


def fetch_indeed_jobs(query: str) -> List[Dict]:
    url = build_indeed_url(query)
    print(f"🔎 [Indeed] {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        print(f"📡 [Indeed] Status: {r.status_code}")
        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.find_all("div", class_="job_seen_beacon")
        print(f"📦 [Indeed] {len(cards)} cards found")

        jobs = []
        for card in cards:
            try:
                title = card.find("h2", class_="jobTitle")
                company = card.find("span", {"data-testid": "company-name"})
                location = card.find("div", {"data-testid": "text-location"})
                link_tag = card.find("a", href=True)
                link = (
                    "https://www.indeed.com" + link_tag["href"]
                    if link_tag and link_tag["href"].startswith("/")
                    else link_tag["href"] if link_tag else "N/A"
                )
                job = {
                    "title": title.get_text(strip=True) if title else "N/A",
                    "company": company.get_text(strip=True) if company else "N/A",
                    "location": location.get_text(strip=True) if location else "N/A",
                    "link": link,
                    "source": "Indeed"
                }
                if job["title"] != "N/A" or job["company"] != "N/A":
                    jobs.append(job)
            except Exception:
                continue
        return jobs[:30]
    except Exception as e:
        print(f"❌ [Indeed] {e}")
        return []


def fetch_remoteok_jobs(query: str) -> List[Dict]:
    url = build_remoteok_url(query)
    print(f"🔎 [RemoteOK] {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        print(f"📡 [RemoteOK] Status: {r.status_code}")
        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.find_all("tr", class_="job")
        print(f"📦 [RemoteOK] {len(cards)} cards found")

        jobs = []
        for card in cards:
            try:
                title = card.find("h2", itemprop="title")
                company = card.find("h3", itemprop="name")
                location = card.find("div", class_="location")
                link_tag = card.find("a", class_="preventLink", href=True)
                link = "https://remoteok.com" + link_tag["href"] if link_tag else "N/A"

                job = {
                    "title": title.get_text(strip=True) if title else "N/A",
                    "company": company.get_text(strip=True) if company else "N/A",
                    "location": location.get_text(strip=True) if location else "Remote",
                    "link": link,
                    "source": "RemoteOK"
                }
                if job["title"] != "N/A" or job["company"] != "N/A":
                    jobs.append(job)
            except Exception:
                continue
        return jobs[:30]
    except Exception as e:
        print(f"❌ [RemoteOK] {e}")
        return []


def fetch_weworkremotely_jobs(query: str) -> List[Dict]:
    url = build_weworkremotely_url(query)
    print(f"🔎 [WeWorkRemotely] {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        print(f"📡 [WeWorkRemotely] Status: {r.status_code}")
        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.find_all("li", class_="feature")
        print(f"📦 [WeWorkRemotely] {len(cards)} cards found")

        jobs = []
        for card in cards:
            try:
                title = card.find("span", class_="title")
                company = card.find("span", class_="company")
                region = card.find("span", class_="region")
                link_tag = card.find("a", href=True)
                link = (
                    "https://weworkremotely.com" + link_tag["href"]
                    if link_tag and link_tag["href"].startswith("/")
                    else "N/A"
                )
                job = {
                    "title": title.get_text(strip=True) if title else "N/A",
                    "company": company.get_text(strip=True) if company else "N/A",
                    "location": region.get_text(strip=True) if region else "Remote",
                    "link": link,
                    "source": "WeWorkRemotely"
                }
                if job["title"] != "N/A" or job["company"] != "N/A":
                    jobs.append(job)
            except Exception:
                continue
        return jobs[:30]
    except Exception as e:
        print(f"❌ [WeWorkRemotely] {e}")
        return []


def fetch_naukri_jobs(query: str) -> List[Dict]:
    url = build_naukri_url(query)
    print(f"🔎 [Naukri] {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        print(f"📡 [Naukri] Status: {r.status_code}")
        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.find_all("article", class_="jobTuple")
        print(f"📦 [Naukri] {len(cards)} cards found")

        jobs = []
        for card in cards:
            try:
                title = card.find("a", class_="title")
                company = card.find("a", class_="subTitle")
                location = card.find("li", class_="location")
                job = {
                    "title": title.get_text(strip=True) if title else "N/A",
                    "company": company.get_text(strip=True) if company else "N/A",
                    "location": location.get_text(strip=True) if location else "N/A",
                    "link": title["href"] if title and title.get("href") else "N/A",
                    "source": "Naukri"
                }
                if job["title"] != "N/A" or job["company"] != "N/A":
                    jobs.append(job)
            except Exception:
                continue
        return jobs[:30]
    except Exception as e:
        print(f"❌ [Naukri] {e}")
        return []


def fetch_simplyhired_jobs(query: str) -> List[Dict]:
    url = build_simplyhired_url(query)
    print(f"🔎 [SimplyHired] {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        print(f"📡 [SimplyHired] Status: {r.status_code}")
        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.find_all("div", attrs={"data-jobkey": True})
        print(f"📦 [SimplyHired] {len(cards)} cards found")

        jobs = []
        for card in cards:
            try:
                title = card.find("a", class_="chakra-button")
                company = card.find("span", attrs={"data-testid": "company-name"})
                location = card.find("span", attrs={"data-testid": "job-location"})
                link_tag = card.find("a", href=True)
                link = (
                    "https://www.simplyhired.com" + link_tag["href"]
                    if link_tag and link_tag["href"].startswith("/")
                    else link_tag["href"] if link_tag else "N/A"
                )
                job = {
                    "title": title.get_text(strip=True) if title else "N/A",
                    "company": company.get_text(strip=True) if company else "N/A",
                    "location": location.get_text(strip=True) if location else "N/A",
                    "link": link,
                    "source": "SimplyHired"
                }
                if job["title"] != "N/A" or job["company"] != "N/A":
                    jobs.append(job)
            except Exception:
                continue
        return jobs[:30]
    except Exception as e:
        print(f"❌ [SimplyHired] {e}")
        return []


def fetch_careerjet_jobs(query: str) -> List[Dict]:
    url = build_careerjet_url(query)
    print(f"🔎 [CareerJet] {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        print(f"📡 [CareerJet] Status: {r.status_code}")
        if r.status_code != 200:
            return []

        soup = BeautifulSoup(r.text, "lxml")
        cards = soup.find_all("article", class_="job")
        print(f"📦 [CareerJet] {len(cards)} cards found")

        jobs = []
        for card in cards:
            try:
                title = card.find("h2")
                company = card.find("p", class_="company")
                location = card.find("ul", class_="location")
                link_tag = card.find("a", href=True)
                link = (
                    "https://www.careerjet.com" + link_tag["href"]
                    if link_tag and link_tag["href"].startswith("/")
                    else link_tag["href"] if link_tag else "N/A"
                )
                job = {
                    "title": title.get_text(strip=True) if title else "N/A",
                    "company": company.get_text(strip=True) if company else "N/A",
                    "location": location.get_text(strip=True) if location else "N/A",
                    "link": link,
                    "source": "CareerJet"
                }
                if job["title"] != "N/A" or job["company"] != "N/A":
                    jobs.append(job)
            except Exception:
                continue
        return jobs[:30]
    except Exception as e:
        print(f"❌ [CareerJet] {e}")
        return []


# ============================================================
# 🚀 MAIN FUNCTION
# ============================================================

async def search_jobs(query: str) -> List[Dict]:
    """
    Search all job sources concurrently.
    Returns deduplicated combined results.
    """
    loop = asyncio.get_event_loop()

    # ✅ Run all scrapers concurrently in thread pool
    results = await asyncio.gather(
        loop.run_in_executor(None, fetch_linkedin_jobs, query),
        loop.run_in_executor(None, fetch_indeed_jobs, query),
        loop.run_in_executor(None, fetch_remoteok_jobs, query),
        loop.run_in_executor(None, fetch_weworkremotely_jobs, query),
        loop.run_in_executor(None, fetch_naukri_jobs, query),
        loop.run_in_executor(None, fetch_simplyhired_jobs, query),
        loop.run_in_executor(None, fetch_careerjet_jobs, query),
        return_exceptions=True  # ✅ One source failing won't crash others
    )

    # ✅ Flatten all results and deduplicate by link
    all_jobs = []
    seen_links = set()

    for source_jobs in results:
        if isinstance(source_jobs, Exception):
            print(f"⚠️ A source raised an exception: {source_jobs}")
            continue
        for job in source_jobs:
            link = job.get("link", "N/A")
            if link not in seen_links:
                seen_links.add(link)
                all_jobs.append(job)

    print(f"✅ Total unique jobs from all sources: {len(all_jobs)}")
    return all_jobs