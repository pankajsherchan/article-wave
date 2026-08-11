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
- Treat `../llm-twin-course` and `../medium articles` as read-only references.
- Record current status in this `COURSE_PLAN.md`.
- Keep secrets out of notes and tracked files.
- Prefer a working Article Wave slice over completing every course exercise.
- Keep the code layout close enough to `../llm-twin-course/src` that course
  articles, Makefile targets, and reference code remain easy to compare.
  Adapt behavior and scope to Article Wave instead of copying unsupported
  domains.

## Code Layout Direction

Article Wave should follow the course pipeline names where they help learning:

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
- Article Wave crawlers should output normalized article records, not
  author-imitation training data.
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
| 8. Refactor | Optional Superlinked/multi-index comparison | Articles 11-12 |

Phases 2-5 are the first useful MVP. Phases 6-8 are optional unless they help
the product.

NOTES
The installation and the initial setup foundation work will be taken care of by the engineers themselves, so no need to add in the MD plan. 

## Progress Tracker

Current phase: **Phase 4 — Indexing**.

| Phase | Status | Notes |
| --- | --- | --- |
| Phase 2 — Ingestion | Complete | Public Medium/Substack URLs can be crawled into normalized `ArticleDocument` records. Metadata, canonical URL dedupe, changed-content update behavior, MongoDB indexes, platform dispatch, and CLI URL input are implemented. |
| Phase 3 — Sync | Complete | MongoDB CDC emits `article.created`, `article.updated`, and `article.deleted` events to RabbitMQ. Update/delete policy is to remove stale chunks/vectors by `article_id` before reindexing or after deletion. |
| Phase 4 — Indexing | Current | Make article chunks searchable with citation metadata. |
| Phase 5 — Retrieval | Not started | Answer questions from article evidence with citations. |
| Phase 6 — Behavior | Not started | Decide whether fine-tuning/dataset generation is useful for stable answer style. |
| Phase 7 — Evaluation | Not started | Define direct, synthesis, filter, and unsupported-question evaluation cases. |
| Phase 8 — Optional Refactor | Not started | Compare alternate retrieval/indexing designs only after the basic MVP works. |

## Phase 2 — Ingestion

Goal: turn a public Medium/Substack URL into a normalized article record.

Use a course-like Phase 2 structure:

```text
src/
├── core/
│   └── db/
│       └── documents.py          # ArticleDocument schema/model
└── data_crawling/
    ├── dispatcher.py             # maps URLs to crawlers
    ├── main.py                   # local entry point for one URL
    └── crawlers/
        ├── base.py               # BaseCrawler interface
        ├── custom_article.py     # shared article extraction path
        ├── medium.py             # Medium-specific wrapper if needed
        └── substack.py           # Substack-specific wrapper if needed
```

Article records should preserve, when available:

- source URL and canonical URL;
- platform;
- title;
- author/publication;
- published date;
- content;
- content hash;
- ingestion time.

The first implementation can keep `MediumCrawler` and `SubstackCrawler` thin and
delegate most work to `CustomArticleCrawler`, as long as the dispatcher makes
the platform handling explicit.

Done when Article Wave has a documented schema and a working or clearly scoped
first ingestion path.

## Phase 3 — Sync

Goal: prevent stale downstream data.

Define:

- `article.created`;
- `article.updated`;
- `article.deleted`;
- how old chunks/vectors are replaced or removed.

Policy:

- `article.created`: clean, chunk, embed, and index the new article.
- `article.updated`: delete existing chunks/vectors by `article_id`, then clean,
  chunk, embed, and index the replacement article content.
- `article.deleted`: delete existing chunks/vectors by `article_id`.

Done: MongoDB change streams map article inserts, updates/replacements, and
deletes into Article Wave events and publish them to the `article_events`
RabbitMQ queue.

## Phase 4 — Indexing

Goal: make articles searchable with citeable chunks.

Every chunk should keep:

- article ID;
- title;
- URL;
- platform;
- author/publication;
- chunk position;
- heading or section when available.

Done when article chunks can be inspected in a local vector index with enough
metadata to cite their source.

## Phase 5 — Retrieval

Goal: answer questions from article evidence.

Test:

- one direct question;
- one cross-article synthesis question;
- one unsupported question.

Done when answers cite supporting passages and unsupported questions are
declined or qualified.

## Phase 6 — Behavior

Goal: decide whether dataset generation or fine-tuning is worth it.

Default answer: probably skip for the MVP.

Use this phase only for stable behavior like citation discipline, comparison
style, or answer structure. Do not fine-tune changing article facts.

Done when there is a clear keep/skip decision.

## Phase 7 — Evaluation

Goal: make quality visible.

Create a small evaluation set with:

- direct questions;
- synthesis questions;
- author/publication filters;
- unanswerable questions.

Done when expected source URLs/passages are recorded and failure categories are
defined.

## Phase 8 — Optional Refactor

Goal: compare Superlinked or multi-index retrieval only after the basic path
works.

Done only if the alternate design improves a real Article Wave use case enough
to justify the complexity.

## MVP Done

Article Wave MVP is done when:

- Medium/Substack URLs can be ingested;
- source metadata is preserved;
- chunks are searchable locally;
- answers cite source passages;
- unsupported questions are handled honestly;
- no paid cloud resource remains active.
