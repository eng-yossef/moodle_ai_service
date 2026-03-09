from fastapi import APIRouter
from services.job_scraper_service import scrape_remotive

router = APIRouter()

@router.get("/jobs")
def get_jobs(skill: str = "python", limit: int = 10):

    jobs = scrape_remotive(skill, limit)

    return {
        "count": len(jobs),
        "jobs": jobs
    }