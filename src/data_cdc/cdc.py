import json

from bson import json_util

from core.config import settings
from core.db.mongo import connection
from core.mq import publish_to_rabbitmq
from data_cdc.mapper import map_article_change


def stream_article_changes() -> None:
    db = connection.get_database()
    collection = db["articles"]

    change_stream = collection.watch(
        [
            {
                "$match": {
                    "operationType": {
                        "$in": ["insert", "replace", "update", "delete"]
                    }
                }
            }
        ],
        full_document="updateLookup",
    )

    for change in change_stream:
        event = map_article_change(change)

        if event is None:
            continue

        serialized = json.dumps(event.model_dump(mode="json"), default=json_util.default)
        publish_to_rabbitmq(queue_name=settings.RABBITMQ_QUEUE_NAME, data=serialized)

        summary = {
            "event_type": event.event_type,
            "article_id": str(event.article_id),
            "canonical_url": event.canonical_url,
            "content_hash": event.content_hash,
            "occurred_at": event.occurred_at.isoformat(),
        }

        print(json.dumps(summary, default=json_util.default))


if __name__ == "__main__":
    stream_article_changes()
