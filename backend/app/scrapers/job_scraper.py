import asyncio
from typing import List, Dict
from pyppeteer import launch
from bs4 import BeautifulSoup


# ⭐ CHANGE if Chrome path different
CHROME_PATH = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"


# --------------------------------------------
# ⭐ Fetch LinkedIn page HTML
# --------------------------------------------
async def fetch_page_html(url: str) -> str:

    browser = await launch(
        headless=True,
        executablePath=CHROME_PATH,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage"
        ]
    )

    page = await browser.newPage()

    await page.setUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    )

    await page.goto(url, timeout=60000, waitUntil="networkidle2")

    # Scroll to load jobs
    await page.evaluate("""
        window.scrollTo(0, document.body.scrollHeight)
    """)

    await asyncio.sleep(3)

    html = await page.content()

    await browser.close()

    return html


# --------------------------------------------
# ⭐ Build LinkedIn Jobs URL
# --------------------------------------------
def build_linkedin_url(query: str) -> str:

    query = query.replace(" ", "%20")

    return (
        f"https://www.linkedin.com/jobs/search"
        f"?keywords={query}&location=Worldwide"
    )


# --------------------------------------------
# ⭐ Extract jobs from LinkedIn HTML
# --------------------------------------------
def extract_jobs_from_linkedin(html: str) -> List[Dict]:

    soup = BeautifulSoup(html, "lxml")

    jobs = []

    job_cards = soup.find_all("div", class_="base-card")

    for card in job_cards:

        try:
            title_elem = card.find("h3")
            company_elem = card.find("h4")
            location_elem = card.find("span", class_="job-search-card__location")
            link_elem = card.find("a", href=True)

            title = title_elem.get_text(strip=True) if title_elem else "N/A"
            company = company_elem.get_text(strip=True) if company_elem else "N/A"
            location = location_elem.get_text(strip=True) if location_elem else "N/A"
            link = link_elem["href"] if link_elem else "N/A"

            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "link": link,
                "source": "LinkedIn"
            })

        except Exception:
            continue

    return jobs[:30]


# --------------------------------------------
# ⭐ MAIN FUNCTION (used by FastAPI)
# --------------------------------------------
async def search_jobs(query: str) -> List[Dict]:

    url = build_linkedin_url(query)

    print("🔎 LinkedIn URL:", url)

    html = await fetch_page_html(url)

    jobs = extract_jobs_from_linkedin(html)

    print(f"✅ Found {len(jobs)} LinkedIn jobs")

    return jobs