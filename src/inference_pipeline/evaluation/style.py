import json
from typing import Any
from core.config import settings
from pydantic import BaseModel
from opik.evaluation.metrics import base_metric, exceptions, score_result
from opik.evaluation.models import litellm_chat_model

class LLMJudgeStyleOutputResult(BaseModel):
    score: int
    reason: str

class Style(base_metric.BaseMetric):
    def __init__(
        self,
        name: str = "article_wave_style_metric",
        model_name: str = settings.OPENAI_MODEL_ID,
    ) -> None:
        self.name = name
        self.llm_client = litellm_chat_model.LiteLLMChatModel(model_name=model_name)
        self.prompt_template = """
You are an impartial expert judge. Evaluate whether an Article Wave answer has the right style.

Article Wave answers should be:
- concise
- evidence-grounded
- citation-aware
- honest about uncertainty
- clear for a technical reader
- free of unsupported claims

Style scale:
1 (Poor): The answer is vague, unsupported, missing citations, or confidently speculates beyond the evidence.
2 (Good): The answer is mostly clear and grounded, but has minor citation, uncertainty, or concision issues.
3 (Excellent): The answer is concise, well-grounded, cites evidence appropriately, and avoids unsupported claims.

Question: {input}

Answer: {output}

Provide your evaluation in JSON format with this structure:
{{
    "score": 0,
    "reason": "..."
}}
"""


    def score(self, input: str, output: str, **ignored_kwargs: Any):
        prompt = self.prompt_template.format(input=input, output=output)

        model_output = self.llm_client.generate_string(
            input=prompt,
            response_format=LLMJudgeStyleOutputResult
        )

        return self._parse_model_output(model_output)

    def _parse_model_output(self, content: str) -> score_result.ScoreResult:
        try:
            dict_content = json.loads(content)
        except Exception:
            raise exceptions.MetricComputationError("Failed to parse the model output.")

        score = dict_content["score"]
        try:
            assert 1 <= score <= 3, f"Invalid score value: {score}"
        except AssertionError as e:
            raise exceptions.MetricComputationError(str(e))

        score = (score - 1) / 2.0  # Normalize the score to be between 0 and 1

        return score_result.ScoreResult(
            name=self.name,
            value=score,
            reason=dict_content["reason"],
        )