from fastapi import FastAPI
from core.cors import add_cors
from api.routes_ask import router as ask_router
from api.routes_similarity import router as similarity_router
from api.routes_helpdesk import router as helpdesk_router
from api.routes_jobs import router as jobs_router
from services.moodle_sync_service import sync_posts
from api.routes_interview import router as interview_router

app = FastAPI()

add_cors(app)

app.include_router(ask_router)
app.include_router(similarity_router)
app.include_router(helpdesk_router)
app.include_router(jobs_router)
app.include_router(interview_router)


@app.on_event("startup")
def startup_event():
    sync_posts()