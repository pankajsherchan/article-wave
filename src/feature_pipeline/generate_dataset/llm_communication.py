import json
import logging

from core.config import settings
from openai import OpenAI

MAX_LENGTH = 16384

SYSTEM_PROMPT = (
    "You are a technical writer generating instruction data for an article "
    "intelligence app."
)


class GptCommunicator:
    def __init__(self, gpt_model: str = settings.OPENAI_MODEL_ID) -> None:
        self.api_key = settings.OPENAI_API_KEY
        self.gpt_model = gpt_model

    def send_prompt(self, prompt: str) -> list:
        try:
            client = OpenAI(api_key=self.api_key)

            chat_completion = client.chat.completions.create(
                messages=[
                    { "role": "system", "content": SYSTEM_PROMPT},
                    { "role": "user", "content": prompt[:MAX_LENGTH]}
                ],
                model=self.gpt_model
            )

            response = chat_completion.choices[0].message.content or ""
            return json.loads(self.clean_response(response))
        except Exception:
            print('GPT failed')
            return []

    @staticmethod
    def clean_response(response: str) -> str:
        start_index = response.find("[")
        end_index = response.rfind("]")

        return response[start_index : end_index + 1]