"""Azure OpenAI client wrapper."""

import logging
from typing import Any, Dict, List

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
from openai.types.chat import ChatCompletionMessageParam

logger = logging.getLogger(__name__)


class OpenAIClient:
    """Wrapper for Azure OpenAI API."""

    def __init__(
        self,
        endpoint: str,
        deployment: str,
        api_version: str,
        credential: DefaultAzureCredential,
    ):
        token_provider = get_bearer_token_provider(
            credential, "https://cognitiveservices.azure.com/.default"
        )

        self.client = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_ad_token_provider=token_provider,
            api_version=api_version,
        )
        self.deployment = deployment

    def generate_completion(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Generate chat completion."""
        try:
            # Convert to proper message format
            typed_messages: List[ChatCompletionMessageParam] = []
            for msg in messages:
                typed_messages.append(msg)  # type: ignore[arg-type]

            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=typed_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
