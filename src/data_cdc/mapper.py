from uuid import UUID

from data_cdc.events import ArticleChangeEvent, ArticleEventType


def map_article_change(change: dict) -> ArticleChangeEvent | None:
    operation_type = change.get("operationType")

    if operation_type == "insert":
        document = change["fullDocument"]

        return ArticleChangeEvent(
            event_type=ArticleEventType.CREATED,
            article_id=UUID(document["_id"]),
            canonical_url=document["canonical_url"],
            content_hash=document.get("content_hash"),
            payload=document,
        )
    if operation_type in {"replace", "update"}:
        document = change.get("fullDocument")
        if not document:
            return None

        return ArticleChangeEvent(
            event_type=ArticleEventType.UPDATED,
            article_id=UUID(document["_id"]),
            canonical_url=document["canonical_url"],
            content_hash=document.get("content_hash"),
            payload=document,
        )

    if operation_type == "delete":
        document_key = change["documentKey"]

        return ArticleChangeEvent(
            event_type=ArticleEventType.DELETED,
            article_id=UUID(document_key["_id"]),
            canonical_url="",
        )

    return None