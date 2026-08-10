# Article Wave

**Read across sources. Trace every claim.**

Article Wave is an evidence-grounded learning assistant for public Medium and
Substack articles. The project follows the Decoding AI LLM Twin course as a
reference implementation while adapting the scope to a focused product: ingest
articles, preserve source metadata, search across them, and answer with
traceable citations.

This repository is intentionally local-first and course-aligned. It keeps a
similar pipeline vocabulary to `llm-twin-course` so the learning path is easy to
compare, but it does not copy unsupported domains such as GitHub, LinkedIn,
email, private profiles, or author-imitation data.

## Current Status

Phase 3, **Sync / CDC**, is complete. Phase 4 indexing is next.

Implemented so far:

- `ArticleDocument` schema in `src/core/db/documents.py`
- `BaseCrawler` interface in `src/data_crawling/crawlers/base.py`
- Course-like source layout for the ingestion pipeline
- Project dependencies declared for article crawling and validation
- `CustomArticleCrawler` for shared public article extraction
- Thin `MediumCrawler` and `SubstackCrawler` wrappers for course-aligned dispatch
- CLI entry point for crawling an explicit article URL
- MongoDB deduplication/update behavior based on canonical URL and content hash
- MongoDB indexes for canonical URL, content hash, and platform/canonical URL lookup
- RabbitMQ service for local event transport
- Article CDC events for create, update, and delete changes
- Compact CDC terminal summaries while full event payloads are queued

Next implementation phase:

- Phase 4, **Indexing**, to consume article events and build citeable chunks.

## Course-To-Project Skill Map

| Course / Engineering Skill | How Article Wave Uses It | Status |
| --- | --- | --- |
| Data ingestion | Crawl explicit public Medium/Substack URLs and normalize them into article records. | Complete |
| Schema design | Define a durable `ArticleDocument` contract for downstream indexing and retrieval. | Implemented |
| Pipeline architecture | Keep course-style stages: `data_crawling`, `data_cdc`, `feature_pipeline`, `inference_pipeline`. | Started |
| Abstraction design | Use `BaseCrawler` so Medium, Substack, and shared article crawlers follow one interface. | Implemented |
| Source metadata preservation | Store URL, canonical URL, platform, title, author, publication, publish date, content hash, and ingestion time. | Implemented |
| Deduplication strategy | Use canonical URL and content hash to avoid duplicate or stale article records. | Implemented |
| Change data capture | Model `article.created`, `article.updated`, and `article.deleted` events for downstream cleanup. | Implemented |
| Text cleaning and chunking | Convert article text into citeable chunks with source metadata. | Planned |
| Vector search / RAG | Retrieve article chunks and answer questions with citations. | Planned |
| Evaluation | Test direct questions, cross-article synthesis, filters, and unsupported questions. | Planned |
| Product scoping | Adapt a broad reference architecture into a focused Article Wave MVP. | Ongoing |

## Packages And Tools

| Package / Tool | Purpose In This Project | Status |
| --- | --- | --- |
| Python 3.12+ | Main implementation language. | Active |
| Pydantic | Validates structured article records through `ArticleDocument`. | Active |
| httpx | Fetches article HTML from public URLs. | Declared for Phase 2 |
| trafilatura | Extracts readable article text and metadata from HTML. | Declared for Phase 2 |
| uv | Manages Python dependencies and lockfile. | Active |
| RabbitMQ | Carries article CDC events from sync into the feature pipeline. | Active |
| Git | Tracks project history and implementation progress. | Active |
| VS Code | Development environment, configured to hide generated Python cache/build files. | Active |

Potential later packages will be chosen when their phase begins:

- local storage or database package for article persistence;
- vector database or local vector index for searchable chunks;
- embedding model/provider for retrieval;
- evaluation tooling for RAG quality checks.

## Architecture Direction

The project keeps the course-like folder layout:

```text
src/
├── core/                 # shared config, schemas, storage helpers
├── data_crawling/        # Phase 2: crawl explicit Medium/Substack URLs
├── data_cdc/             # Phase 3: article create/update/delete events
├── feature_pipeline/     # Phase 4: clean, chunk, embed, and index
└── inference_pipeline/   # Phase 5: cited RAG answers
```

The first MVP path is:

```text
Medium/Substack URL
-> data_crawling
-> ArticleDocument
-> change event
-> clean/chunk/embed
-> vector index
-> cited RAG answer
```

## Scope

In scope:

- public Medium articles;
- public Substack posts;
- user notes created inside Article Wave;
- cited retrieval-augmented generation;
- local-first development.

Out of scope:

- GitHub or LinkedIn ingestion;
- email, calendar, chat, browser history, or social feeds;
- private or paywalled content obtained by bypassing access controls;
- personal author imitation.

## Phase Roadmap

| Phase | Outcome |
| --- | --- |
| Phase 2: Ingestion | Medium/Substack URLs become normalized article records. Complete. |
| Phase 3: Sync | Article create/update/delete events prevent stale downstream data. Complete. |
| Phase 4: Indexing | Articles become searchable citeable chunks. Current. |
| Phase 5: Retrieval | Questions are answered from article evidence with citations. |
| Phase 6: Behavior | Decide whether fine-tuning is useful for stable answer style. |
| Phase 7: Evaluation | Make retrieval and answer quality visible through test cases. |
| Phase 8: Optional Refactor | Compare alternate indexing approaches only after the MVP works. |

## Employer-Relevant Highlights

This project demonstrates:

- translating a reference architecture into a scoped product;
- designing typed data models for AI pipelines;
- building crawler abstractions and ingestion contracts;
- preserving source provenance for trustworthy AI answers;
- separating facts in retrieval from optional behavior tuning;
- planning an MVP around RAG, citations, and evaluation instead of model hype.
