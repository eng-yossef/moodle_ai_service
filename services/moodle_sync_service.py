import requests
import faiss
from core.config import MOODLE_POSTS_URL
from models.embedding_model import model

corpus = []
index = None

def sync_posts():
    global corpus, index

    try:
        resp = requests.get(MOODLE_POSTS_URL)
        resp.raise_for_status()

        if not resp.text.strip():
            corpus = []
            return

        corpus = resp.json()

    except Exception as e:
        print("Error fetching posts:", e)
        corpus = []
        return

    if not corpus:
        return

    titles = [p["title"] for p in corpus]
    embeddings = model.encode(titles, convert_to_numpy=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

def search_similar(q, k):
    global index

    if index is None:
        return []

    query_emb = model.encode([q], convert_to_numpy=True)
    distances, indices = index.search(query_emb, k)

    return [corpus[i] for i in indices[0]]

def get_count():
    return len(corpus)