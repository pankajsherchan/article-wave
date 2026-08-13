from pydantic import BaseModel


class EvidenceSnippet(BaseModel):
    article_id: str
    chunk_id: str
    chunk_index: int
    content: str

    score: float

    source_url: str
    canonical_url: str
    platform: str

    title: str | None = None
    author: str | None = None
    publication: str | None = None
    published_at: str | None = None
    heading: str | None = None

    @classmethod
    def from_qdrant_hit(cls, hit) -> "EvidenceSnippet":
        payload = hit.payload or {}

        return cls(
            article_id=payload["article_id"],
            chunk_id=payload["chunk_id"],
            chunk_index=payload["chunk_index"],
            content=payload["content"],
            score=hit.score,
            source_url=payload["source_url"],
            canonical_url=payload["canonical_url"],
            platform=payload["platform"],
            title=payload.get("title"),
            author=payload.get("author"),
            publication=payload.get("publication"),
            published_at=payload.get("published_at"),
            heading=payload.get("heading"),
        )


class CitedAnswer(BaseModel):
    question: str
    answer: str
    evidences: list[EvidenceSnippet]
