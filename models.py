from pydantic import BaseModel, Field
from typing import Literal, Optional

class ExtractionPayload(BaseModel):
    """Structured output for user input extraction."""
    department: Literal['Revenue', 'Police', 'Health', 'Education', 'Transport', 'Agriculture', None] = Field(
        description="Exact department match or None if unclear"
    )
    prompt: str = Field(description="Cleaned user query")

class ClarificationResponse(BaseModel):
    """For guardrail responses."""
    needs_clarification: bool
    response: str
