from typing import Optional
from pydantic import BaseModel, Field


class MermaidRequest(BaseModel):
    query: str


class MermaidCodeResponse(BaseModel):
    mermaid_code: Optional[str] = Field(
        None, description="Generated Mermaid diagram code"
    )
    description: str = Field(
        description="Description of the generated diagram, if applicable & if the user query is not clear ask for clarification"
    )
