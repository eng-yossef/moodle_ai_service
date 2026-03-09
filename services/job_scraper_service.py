import requests

def scrape_remotive(keyword="python", limit=10):
    url = "https://remotive.com/api/remote-jobs"
    params = {"search": keyword}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code}")

    data = response.json()
    jobs = []

    for job in data.get("jobs", [])[:limit]:
        jobs.append({
            "title": job.get("title"),
            "company": job.get("company_name"),
            "category": job.get("category"),
            "location": job.get("candidate_required_location"),
            "salary": job.get("salary"),
            "published": job.get("publication_date"),
            "link": job.get("url"),
            "source": "Remotive"
        })

    return jobs

if __name__ == "__main__":
    results = scrape_remotive("python", limit=5)
    for job in results:
        print(job)
