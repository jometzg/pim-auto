"""KQL query generation using Azure OpenAI."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class QueryGenerator:
    """Generates Kusto queries using Azure OpenAI."""

    def __init__(self, openai_client: Any):
        self.openai_client = openai_client

    def generate_query(self, natural_language: str, max_retries: int = 2) -> str:
        """Generate KQL query from natural language."""
        system_prompt = """You are an expert in Kusto Query Language (KQL) for Azure Log Analytics.
        Generate valid KQL queries based on user requests.
        Focus on AuditLogs and AzureActivity tables.
        Return only the KQL query, no explanations."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate KQL query for: {natural_language}"},
        ]

        for attempt in range(max_retries + 1):
            try:
                query: str = self.openai_client.generate_completion(
                    messages=messages,
                    temperature=0.3,  # Lower temperature for more deterministic output
                )

                # Basic validation: check if it looks like KQL
                if any(
                    keyword in query for keyword in ["AuditLogs", "AzureActivity", "where", "|"]
                ):
                    logger.info(f"Generated query on attempt {attempt + 1}")
                    return query.strip()
                else:
                    if attempt < max_retries:
                        logger.warning(
                            f"Generated query looks invalid, retrying (attempt {attempt + 1})"
                        )
                        messages.append({"role": "assistant", "content": query})
                        messages.append(
                            {
                                "role": "user",
                                "content": "That doesn't look like valid KQL. Please try again.",
                            }
                        )
                    else:
                        raise ValueError(
                            f"Failed to generate valid query after {max_retries + 1} attempts"
                        )

            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Query generation failed (attempt {attempt + 1}): {e}")
                else:
                    raise

        raise ValueError("Query generation failed")
