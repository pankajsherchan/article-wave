# Phase 7 Evaluation Plan

## Goal

Build Article Wave's evaluation phase to match the LLM Twin course structure as
closely as possible.

Phase 7 maps to LLM Twin Article 8, "LLM & RAG Evaluation", and prepares the
ground for Article 10, "Prompt Monitoring".

The target is not a custom local-only test harness. The target is an
Opik/Comet-based evaluation pipeline with Article Wave-specific datasets,
prompts, retrieval context, and style criteria.

## LLM Twin Alignment

Use this reference folder as the source of truth:

```text
../llm-twin-course/src/inference_pipeline/evaluation/
```

LLM Twin files to mirror:

```text
evaluate.py             # LLM evaluation without RAG
evaluate_rag.py         # RAG evaluation with retrieved context
evaluate_monitoring.py  # Monitoring dataset evaluation
style.py                # Custom LLM judge metric
```

Article Wave should create the same folder shape:

```text
src/inference_pipeline/evaluation/
├── __init__.py
├── evaluate.py
├── evaluate_rag.py
├── evaluate_monitoring.py
└── style.py
```

## Article Wave Adaptations

Keep the mechanism the same as LLM Twin, but adapt the domain.

LLM Twin evaluates generated blog/social content and personal-author behavior.
Article Wave evaluates evidence-grounded answers over public Medium/Substack
articles.

Article Wave evaluation should prioritize:

- citation-grounded answers;
- retrieved context relevance;
- refusal when retrieved evidence is insufficient;
- concise answer style;
- no invented titles, authors, URLs, or claims;
- cross-article synthesis when the question requires multiple sources.

## Required Configuration

Phase 7 follows LLM Twin's Opik/Comet path, so these values should be available
through `.env` or settings before running the evaluation scripts:

```text
COMET_API_KEY
COMET_WORKSPACE
COMET_PROJECT=article-wave
OPENAI_MODEL_ID
MODEL_ID
EMBEDDING_MODEL_ID
```

Use Article Wave settings names where they already exist. Add missing settings
only when the evaluation scripts need them.

## Dataset Source

LLM Twin creates Opik datasets from Comet artifacts generated in the feature
pipeline.

Article Wave should use the Phase 6 article instruction dataset:

```text
articles-instruct-dataset
```

Do not add LLM Twin's repository or social post artifacts unless Article Wave's
scope changes.

Initial Article Wave artifact list:

```python
artifact_names = [
    "articles-instruct-dataset",
]
```

If Phase 6 stores local JSON first, the Phase 7 implementation should still
preserve the LLM Twin direction: upload or register that dataset through
Opik/Comet, then evaluate from the tracked dataset.

## Evaluation Scripts

### 1. `evaluate.py`

Purpose: evaluate Article Wave's base or fine-tuned LLM behavior without RAG.

Mirror LLM Twin's `evaluate.py`.

The task should:

- load the Article Wave evaluation dataset from Opik/Comet artifacts;
- call the inference path with retrieval disabled, or call the relevant model
  generation function directly if Article Wave does not expose a non-RAG mode
  yet;
- return `input`, `output`, `expected_output`, and `reference`;
- score model behavior using Opik metrics.

Initial metrics:

```python
LevenshteinRatio()
Hallucination()
Moderation()
Style()
```

### 2. `evaluate_rag.py`

Purpose: evaluate Article Wave's full retrieval-augmented answer path.

Mirror LLM Twin's `evaluate_rag.py`.

The task should:

- load the Article Wave evaluation dataset;
- call Article Wave inference with RAG enabled;
- return `input`, `output`, `context`, `expected_output`, and `reference`;
- score retrieval context quality and answer grounding.

Initial metrics:

```python
Hallucination()
ContextRecall()
ContextPrecision()
```

This is the most important Phase 7 script for Article Wave because the product
promise is cited answers over indexed article evidence.

### 3. `style.py`

Purpose: define Article Wave's custom style metric using the same LLM-judge
pattern as LLM Twin.

The rubric should evaluate whether the answer is:

- concise;
- evidence-grounded;
- citation-aware;
- clear for a technical reader;
- honest about uncertainty;
- free of unsupported claims.

The metric should penalize answers that:

- invent facts;
- omit citations when evidence is used;
- sound like generic article generation instead of source-grounded QA;
- answer unsupported questions with confident speculation.

### 4. `evaluate_monitoring.py`

Purpose: evaluate previously logged prompts and responses from Opik.

Mirror LLM Twin's `evaluate_monitoring.py`.

This belongs after the basic evaluation scripts work and after Article Wave
logs inference traces to Opik.

Initial metrics:

```python
Hallucination()
Moderation()
AnswerRelevance()
Style()
```

## Makefile Targets

Mirror LLM Twin's targets with Article Wave's package manager:

```makefile
evaluate-llm:
	cd src/inference_pipeline && uv run python -m evaluation.evaluate

evaluate-rag:
	cd src/inference_pipeline && uv run python -m evaluation.evaluate_rag

evaluate-llm-monitoring:
	cd src/inference_pipeline && uv run python -m evaluation.evaluate_monitoring
```

Add these only when the corresponding scripts exist.

## Implementation Order

1. Confirm Phase 6 has produced or selected an article evaluation dataset.
2. Add any missing Opik/Comet dependencies and settings.
3. Create `src/inference_pipeline/evaluation/__init__.py`.
4. Port and adapt `style.py` from LLM Twin.
5. Implement `evaluate_rag.py`.
6. Implement `evaluate.py`.
7. Add Makefile targets for `evaluate-llm` and `evaluate-rag`.
8. Run the RAG evaluation against the Article Wave dataset.
9. Record findings in `COURSE_PLAN.md`.
10. Implement `evaluate_monitoring.py` once prompt traces are logged to Opik.

## Known Article Wave Risks To Measure

Phase 5 surfaced these behaviors, so Phase 7 should make them visible:

- broad synthesis questions may retrieve chunks from only one article;
- increasing retrieval limit may improve cross-article evidence coverage;
- Ollama may occasionally return an empty response;
- unsupported-question behavior depends on retrieval score thresholds;
- citations may not always map cleanly to the evidence needed by the answer.

## Done Criteria

Phase 7 is complete when:

- Article Wave has the LLM Twin-style evaluation package under
  `src/inference_pipeline/evaluation/`;
- `evaluate_rag.py` runs against an Article Wave dataset through Opik/Comet;
- RAG evaluation records hallucination, context recall, and context precision;
- `evaluate.py` exists for non-RAG/fine-tuned model evaluation;
- `style.py` contains an Article Wave-specific judge rubric;
- `COURSE_PLAN.md` records the evaluation results and next product decision;
- monitoring evaluation is either implemented or explicitly deferred until
  prompt tracing exists.

## Scope Guardrails

Stay aligned with Article Wave's product scope:

- evaluate public Medium/Substack article QA;
- do not add GitHub, LinkedIn, or repository datasets;
- do not deploy paid cloud resources without approval;
- do not treat style tuning as a substitute for retrieval quality;
- keep LLM Twin structure, but adapt the data and rubric to Article Wave.
