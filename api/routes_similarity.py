from fastapi import APIRouter
from services.moodle_sync_service import search_similar, sync_posts, get_count

router = APIRouter()

@router.get("/similar")
def get_similar(q: str, k: int = 3):
    return search_similar(q, k)

@router.post("/sync")
def manual_sync():
    sync_posts()
    return {"status": "ok", "count": get_count()}