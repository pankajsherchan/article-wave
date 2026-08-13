from core.config import settings
from core.db.qdrant import QdrantDatabaseConnector
from feature_pipeline.utils.embeddings import embed_text
from inference_pipeline.models import EvidenceSnippet


class ArticleRetriever:
    def __init__(self, limit: int = 5) -> None:
        self.limit = limit
        self.qdrant = QdrantDatabaseConnector()

    def retrieve(self, question: str) -> list[EvidenceSnippet]:
        query_vector = embed_text(question)
        hits = self.qdrant.search(query_vector=query_vector, limit=self.limit)

        evidence_items = [EvidenceSnippet.from_qdrant_hit(hit) for hit in hits]
        return [
            evidence
            for evidence in evidence_items
            if evidence.score >= settings.MIN_RETRIEVAL_SCORE
        ]
