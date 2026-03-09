from fastapi import APIRouter
from services.job_scraper_service import scrape_wuzzuf_jobs

router = APIRouter()

@router.get("/jobs")
def get_jobs(skill: str = "python", limit: int = 10):

    jobs = scrape_wuzzuf_jobs(skill, limit)

    return {
        "count": len(jobs),
        "jobs": jobs
    }