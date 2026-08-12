from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    SentenceTransformersTokenTextSplitter,
)

from core.config import settings


def chunk_text(text: str) -> list[str]:
    character_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n"],
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=0,
    )
    text_split = character_splitter.split_text(text)

    token_splitter = SentenceTransformersTokenTextSplitter(
        chunk_overlap=settings.CHUNK_OVERLAP,
        tokens_per_chunk=settings.EMBEDDING_MODEL_MAX_INPUT_LENGTH,
        model_name=settings.EMBEDDING_MODEL_ID,
    )

    chunks = []
    for section in text_split:
        chunks.extend(token_splitter.split_text(section))

    return chunks