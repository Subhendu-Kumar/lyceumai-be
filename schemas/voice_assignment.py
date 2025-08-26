from typing import List
from pydantic import BaseModel, Field


class VoiceAssignmentOutputFormat(BaseModel):
    score: int = Field(
        description="Score from 0-100 based on accuracy, completeness, and understanding demonstrated"
    )
    feedback: str = Field(
        description="Comprehensive feedback including strengths, weaknesses, and specific improvement suggestions"
    )
    strengths: List[str] = Field(
        description="List of positive aspects in the user's response"
    )
    areas_for_improvement: List[str] = Field(
        description="Specific areas where the response could be enhanced"
    )
