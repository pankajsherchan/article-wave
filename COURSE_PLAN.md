# article-wave build plan

## North Star

Build Article Wave: a Medium/Substack article intelligence app that can ingest
articles, search across them, and answer with traceable citations.

Use `../llm-twin-course` as a reference implementation, not as the product to
rebuild. Each phase asks:

> What should Article Wave keep, change, or skip?

## Boundaries

In scope:

- public Medium articles;
- public Substack posts;
- user notes created inside Article Wave;
- RAG with source citations;
- local-first development.

Out of scope unless explicitly changed:

- GitHub or LinkedIn ingestion;
- email, calendar, chat, or social connectors;
- personal-author imitation;
- paid cloud resources without approval;
- features copied only because the reference repo has them.

## Working Rules

- Build in this repository.
- Treat `../llm-twin-course` and local course PDFs as read-only references.
- Record current status in this `COURSE_PLAN.md`.
- Keep secrets out of notes and tracked files.
- Prefer a working Article Wave slice over completing every course exercise.
- Keep the code layout close enough to `../llm-twin-course/src` that course
  articles, Makefile targets, and reference code remain easy to compare.
  Adapt behavior and scope to Article Wave instead of copying unsupported
  domains.

## Code Layout Direction

Article Wave follows the course pipeline names where they help learning:

```text
src/
├── core/                 # shared config, logging, storage models/helpers
├── data_crawling/        # Phase 2: crawl explicit Medium/Substack URLs
├── data_cdc/             # Phase 3: article created/updated/deleted events
├── feature_pipeline/     # Phase 4: clean, chunk, embed, index articles
└── inference_pipeline/   # Phase 5: cited RAG answers
```

Differences from the reference repo:

- `data_crawling` crawls public Medium/Substack article URLs only.
- Do not add GitHub, LinkedIn, or private profile crawlers unless scope changes.
- Article Wave crawlers output normalized article records, not author-imitation
  training data.
- Local-first storage is acceptable for the MVP; paid cloud resources still
  require approval.

## Phase Map

| Phase | Outcome | Reference |
| --- | --- | --- |
| 2. Ingestion | Medium/Substack article records | Article 2 |
| 3. Sync | Create/update/delete event policy | Article 3 |
| 4. Indexing | Searchable chunks with source metadata | Article 4 |
| 5. Retrieval | Answers with citations | Article 5 |
| 6. Behavior | Optional dataset/fine-tuning decision | Articles 6-7 |
| 7. Evaluation | Test set, monitoring, optional deploy plan | Articles 8-10 |
| 8. Optional Refactor | Optional Superlinked/multi-index comparison | Articles 11-12 |

Phases 2-5 are the first useful MVP. Phases 6-8 are optional unless they help
the product.

## Progress Tracker

Current phase: **Phase 6 — Behavior**.

| Phase | Status | Notes |
| --- | --- | --- |
| Phase 2 — Ingestion | Complete | Public Medium/Substack URLs can be crawled into normalized `ArticleDocument` records. Metadata, canonical URL dedupe, changed-content update behavior, MongoDB indexes, platform dispatch, and CLI URL input are implemented. |
| Phase 3 — Sync | Complete | MongoDB CDC emits `article.created`, `article.updated`, and `article.deleted` events to RabbitMQ. Created/updated events include article payloads; deleted events identify the article for downstream cleanup. |
| Phase 4 — Indexing | Complete | Bytewax consumes RabbitMQ article events, cleans article text, chunks it with course-style LangChain splitters, embeds chunks with a cached SentenceTransformer model, and writes citeable chunk metadata to local Qdrant `article_chunks`. Stale chunks are removed for `article.updated` and `article.deleted`. Local create flow was verified end to end: MongoDB -> CDC -> RabbitMQ -> feature pipeline -> Qdrant. |
| Phase 5 — Retrieval | Complete | Article Wave retrieves Qdrant article chunks, builds grounded prompts, generates local Ollama answers, cites sources, handles unsupported questions, and passes direct, cross-article synthesis, and unsupported-question tests. |
| Phase 6 — Behavior | Current | Decide whether fine-tuning/dataset generation is useful for stable answer style. |
| Phase 7 — Evaluation | Not started | Define direct, synthesis, filter, and unsupported-question evaluation cases. |
| Phase 8 — Optional Refactor | Not started | Compare alternate retrieval/indexing designs only after the basic MVP works. |

## Phase 4 — Indexing Summary

Implemented:

- local Qdrant service and `article_chunks` collection;
- `src/feature_pipeline` course-style layout;
- RabbitMQ Bytewax source;
- raw, cleaning, stale-cleanup, chunking, and embedding dispatchers/handlers;
- Qdrant Bytewax output sink;
- Make targets for local crawling, CDC, and feature pipeline execution.

Event behavior:

```text
article.created -> clean -> chunk -> embed -> upsert chunks
article.updated -> delete old chunks by article_id -> clean -> chunk -> embed -> upsert fresh chunks
article.deleted -> delete chunks by article_id -> stop
```

Done when article chunks can be inspected in a local vector index with enough
metadata to cite their source.

Status: **Done**.

## Phase 5 — Retrieval

Goal: answer questions from article evidence.

Every retrieved passage should preserve:

- article ID;
- title;
- URL;
- platform;
- author/publication;
- chunk position;
- content excerpt.

Test:

- one direct question;
- one cross-article synthesis question;
- one unsupported question.

Done when answers cite supporting passages and unsupported questions are
declined or qualified.

Status: **Done**.

Implemented:

- `src/inference_pipeline` retrieval, prompting, generation, and CLI flow;
- Qdrant similarity search over local `article_chunks`;
- local Ollama generation with `qwen3.5:9b`;
- numbered citations that map answers back to source snippets;
- minimum-score unsupported-question handling.

Verified:

- direct question;
- cross-article synthesis question;
- unsupported question.

## MVP Done

Article Wave MVP is done when:

- Medium/Substack URLs can be ingested;
- source metadata is preserved;
- chunks are searchable locally;
- answers cite source passages;
- unsupported questions are handled honestly;
- no paid cloud resource remains active.
