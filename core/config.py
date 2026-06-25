import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
# OPENROUTER_API_KEY = "REMOVED_OPENROUTER_KEY"
# OPENROUTER_API_KEY = "REMOVED_OPENROUTER_KEY"
OPENROUTER_API_KEY = "REMOVED_OPENROUTER_KEY"


SITE_URL = "http://localhost:8000"
SITE_NAME = "Moodle Chatbot"

MOODLE_POSTS_URL = "http://moodle.local/local/community/ajax/export_posts.php"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "meta-llama/llama-3-8b-instruct"


load_dotenv()

class Settings(BaseSettings):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()