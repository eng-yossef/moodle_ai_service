import requests
from bs4 import BeautifulSoup


def scrape_wuzzuf_jobs(skill: str = "python", limit: int = 20):
    jobs = []

    base_url = "https://wuzzuf.net"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    page = 0

    while len(jobs) < limit:

        url = f"https://wuzzuf.net/search/jobs?q={skill}&start={page*10}"

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")

        job_cards = soup.find_all("div", class_="css-pkv5jc")

        if not job_cards:
            break

        for card in job_cards:

            title_tag = card.find("h2", class_="css-193uk2c")
            company_tag = card.find("a", class_="css-ipsyv7")
            location_tag = card.find("span", class_="css-16x61xq")

            date_tag = card.find("div", class_="css-1jldrig")
            if not date_tag:
                date_tag = card.find("div", class_="css-eg55jf")

            link = None
            title = None

            if title_tag:
                link_tag = title_tag.find("a")
                if link_tag and link_tag.get("href"):
                    title = link_tag.text.strip()
                    link = base_url + link_tag.get("href")

            if not title or not link:
                continue

            job = {
                "title": title,
                "company": company_tag.text.strip().replace("-", "") if company_tag else None,
                "location": location_tag.text.strip() if location_tag else None,
                "date": date_tag.text.strip() if date_tag else None,
                "url": link,
            }

            jobs.append(job)

            if len(jobs) >= limit:
                break

        page += 1

    return jobs