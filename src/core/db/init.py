from core.db.documents import ArticleDocument


DOCUMENT_MODELS = [ArticleDocument]


def init_db() -> None:
    for model in DOCUMENT_MODELS:
        model.ensure_indexes()


if __name__ == "__main__":
    init_db()
    print("MongoDB indexes initialized.")
