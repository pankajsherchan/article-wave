from inference_pipeline.models import EvidenceSnippet


def format_evidence_snippet(index: int, evidence: EvidenceSnippet) -> str:
    title = evidence.title or "Untitled article"
    url = evidence.canonical_url or evidence.source_url
    author = f" by {evidence.author}" if evidence.author else ""

    return f"""
[{index}] {title}{author}
URL: {url}
Platform: {evidence.platform}
Chunk: {evidence.chunk_index}
Excerpt:
{evidence.content}
""".strip()


def build_rag_prompt(question: str, evidence_items: list[EvidenceSnippet]) -> str:
    if not evidence_items:
        return f"""
You are Article Wave, an evidence-grounded article assistant.

The user asked:
{question}

There is no retrieved evidence available.

Answer:
I do not have enough evidence in the indexed articles to answer that.
""".strip()

    evidence_text = "\n\n".join(
        format_evidence_snippet(index, evidence)
        for index, evidence in enumerate(evidence_items, start=1)
    )

    return f"""
You are Article Wave, an evidence-grounded article assistant.

Answer the user's question using only the evidence snippets below.

Rules:
- Cite sources using bracket numbers like [1] or [2].
- If the evidence does not support an answer, say you do not have enough evidence.
- Do not invent facts, URLs, titles, or authors.
- Keep the answer concise.

Question:
{question}

Evidence:
{evidence_text}

Answer:
""".strip()
