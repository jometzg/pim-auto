"""Risk assessment module using Azure OpenAI."""
import logging
from enum import Enum
from typing import Any, List

logger = logging.getLogger(__name__)


class AlignmentLevel(Enum):
    """Activity alignment levels."""

    ALIGNED = "aligned"
    PARTIALLY_ALIGNED = "partially_aligned"
    NOT_ALIGNED = "not_aligned"
    UNKNOWN = "unknown"


class RiskAssessment:
    """Risk assessment result."""

    def __init__(self, level: AlignmentLevel, explanation: str):
        self.level = level
        self.explanation = explanation


class RiskAssessor:
    """Assesses alignment between PIM reasons and activities."""

    def __init__(self, openai_client: Any):
        self.openai_client = openai_client

    def assess_alignment(
        self, pim_reason: str, activities: List[Any]
    ) -> RiskAssessment:
        """Assess if activities align with PIM activation reason."""
        activities_text = "\n".join(
            [
                f"- {act.timestamp.strftime('%Y-%m-%d %H:%M:%S')}: {act.operation_name} on {act.resource_type}/{act.resource_name}"
                for act in activities
            ]
        )

        system_prompt = """You are a security analyst assessing Azure PIM (Privileged Identity Management) activations.
        Determine if the user's activities during their elevated access period align with their stated reason for activation.
        Respond with one of: ALIGNED, PARTIALLY_ALIGNED, NOT_ALIGNED, UNKNOWN.
        Then provide a brief explanation."""

        user_prompt = f"""
        PIM Activation Reason: {pim_reason}

        Activities during elevation:
        {activities_text if activities else "No activities recorded"}

        Does the activity align with the stated reason?
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self.openai_client.generate_completion(
            messages=messages,
            temperature=0.5,
        )

        # Parse response
        response_upper = response.upper()
        if "NOT_ALIGNED" in response_upper or "NOT ALIGNED" in response_upper:
            level = AlignmentLevel.NOT_ALIGNED
        elif (
            "PARTIALLY_ALIGNED" in response_upper
            or "PARTIALLY ALIGNED" in response_upper
        ):
            level = AlignmentLevel.PARTIALLY_ALIGNED
        elif "ALIGNED" in response_upper:
            level = AlignmentLevel.ALIGNED
        else:
            level = AlignmentLevel.UNKNOWN

        logger.info(f"Assessment: {level.value}")
        return RiskAssessment(level=level, explanation=response)
