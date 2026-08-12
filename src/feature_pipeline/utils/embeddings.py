from functools import lru_cache

from sentence_transformers import SentenceTransformer
from core.config import settings


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer: 
    return SentenceTransformer(settings.EMBEDDING_MODEL_ID)

def embed_text(text: str) -> list[float]:
    model = get_embedding_model()
    embedding = model.encode(text)

    return embedding.tolist()