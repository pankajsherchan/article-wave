# article-wave context

Durable project memory. Update when scope, architecture, references, or major decisions change. Current phase progress belongs in `COURSE_PLAN.md`.

## Identity

`article-wave` is an evidence-grounded assistant for learning from public Medium and Substack articles while following Decoding AI's LLM Twin course. It is not an author-imitation system or feature-for-feature clone.

Tagline: **Read across sources. Trace every claim.**

Status: Phase 2 data crawling and Phase 3 sync are complete; Phase 4 indexing is next. Unqualified status, phase, progress, blocker, or "where are we?" questions mean `article-wave`.

## References

```text
llm/
├── article-wave/        # edit here
├── llm-twin-course/     # reference implementation; read-only
└── medium articles/     # 12 course PDFs; read-only
```

- Reference repo: `../llm-twin-course`
- Upstream: `https://github.com/decodingai-magazine/llm-twin-course`
- Pinned local commit: `04e12f374f7f4a42bf6b848f8e99b89364fa23a6`
- Key files: `README.md`, `INSTALL_AND_USAGE.md`, `Makefile`, `src/`, `data/links.txt`
- Course PDFs: `../medium articles`, read `01` through `12`
- Phase plan: `COURSE_PLAN.md`

If references disagree, prefer local code, then install docs/Makefile, then the matching PDF, then the reference README. Document important mismatches.

## Scope

Application data is limited to public Medium articles, public Substack posts, and user annotations/reflections created inside Article Wave.

Do not ingest GitHub repos/artifacts, LinkedIn, email, calendars, chats, browser history, social feeds, private content, or paywalled content obtained by bypassing access controls. GitHub may host this source code, and `../llm-twin-course` may be studied as reference.

## Product Requirements

The first useful system should ingest explicit Medium/Substack URLs; store canonical URL, platform, title, author, publication date, content, ingestion time, and content hash when available; deduplicate articles; remove stale chunks; preserve citation metadata; answer direct and cross-article questions with citations; separate article claims from user notes; decline unsupported answers; and expose retrieval/generation traces.

North-star query: compare how several authors explain an AI engineering concept, distinguish agreement from disagreement, and cite support for each claim.

## Architecture and Workflow

```text
Medium/Substack URL -> collection -> article store -> change event
  -> clean/chunk/embed -> vector index -> cited RAG answer -> evaluation
```

Article Wave should keep a course-like source layout for learning continuity:
`src/core`, `src/data_crawling`, `src/data_cdc`, `src/feature_pipeline`, and
`src/inference_pipeline`. The contents remain Article Wave-specific:
`data_crawling` handles public Medium/Substack article URLs only, not GitHub,
LinkedIn, private sources, or author-imitation data.

Article facts belong in retrieval. Fine-tuning is optional and only for stable behavior such as answer structure, comparison style, or citation discipline.

Follow `COURSE_PLAN.md`: read, restate, inspect reference code, predict, verify, adapt in `article-wave`, and record evidence. Build only here; keep reference folders read-only. Use `course-material/extracted/` only as ignored PDF study text. Keep secrets in ignored env files, require RAG citation and unsupported-question tests, and get approval before billable cloud resources.

Collaboration rule: by default, guide the user step by step and let the user do
the coding. Do not modify project code unless the user explicitly asks Codex to
make the change.

Course-following rule: when guiding implementation, follow the same path and
sequence as `../llm-twin-course` first, then adapt only the product domain to
Article Wave. Do not substitute a simpler generic path, package choice, storage
setup, or folder structure unless the user explicitly chooses that deviation.

## Environment and Next Action

Captured on 2026-08-09: Python 3.12 project managed with `uv`; local MongoDB
replica set available through `docker-compose.yml`; Phase 2 code can crawl an
explicit public Medium/Substack URL into an `ArticleDocument`.

Next: start Phase 4 by consuming `article_events` from RabbitMQ, cleaning article
text, and chunking articles with citation metadata.
