import httpx

from core.config import settings
from inference_pipeline.models import CitedAnswer
from inference_pipeline.prompting import build_rag_prompt
from inference_pipeline.retrieval import ArticleRetriever


class ArticleAnswerGenerator:
    def __init__(self, retriever: ArticleRetriever | None = None) -> None:
        self.retriever = retriever or ArticleRetriever()

    def generate(self, question: str) -> CitedAnswer:
        evidence_items = self.retriever.retrieve(question)
        if not evidence_items:
            return CitedAnswer(
                question=question,
                answer="I do not have enough evidence in the indexed articles to answer that.",
                evidences=[],
            )

        prompt = build_rag_prompt(question, evidence_items)

        answer = self._call_ollama(prompt)

        return CitedAnswer(
            question=question,
            answer=answer,
            evidences=evidence_items,
        )

    def _call_ollama(self, prompt: str) -> str:
        response = httpx.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL_ID,
                "prompt": prompt,
                "stream": False,
            },
            timeout=300,
        )
        response.raise_for_status()

        data = response.json()
        return data["response"].strip()
