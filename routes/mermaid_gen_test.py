from utils.gemini_util import gemini
from langchain.prompts import PromptTemplate
from fastapi import APIRouter, HTTPException, status
from langchain_core.output_parsers import PydanticOutputParser
from schemas.mermaid import MermaidCodeResponse, MermaidRequest

parser = PydanticOutputParser(pydantic_object=MermaidCodeResponse)

prompt = PromptTemplate(
    input_variables=["user_query"],
    partial_variables={"format_instruction": parser.get_format_instructions()},
    template="""
    You are a professional Mermaid diagram expert and code generator. Your role is to create clean, well-structured Mermaid diagrams based on user requirements.

    Guidelines:
    - Generate syntactically correct Mermaid code
    - Use appropriate diagram types (flowchart, sequence, class, gantt, pie, etc.)
    - Follow Mermaid best practices for readability
    - Include proper node IDs, labels, and connections
    - Use meaningful styling when appropriate
    - Ensure the diagram is logically structured and easy to understand

    Common Mermaid diagram types you can create:
    1. Flowchart (graph TD, graph LR)
    2. Sequence diagrams (sequenceDiagram)
    3. Class diagrams (classDiagram)
    4. State diagrams (stateDiagram-v2)
    5. Entity Relationship diagrams (erDiagram)
    6. User Journey (journey)
    7. Gantt charts (gantt)
    8. Pie charts (pie)
    9. Requirement diagrams (requirementDiagram)
    10. Gitgraph (gitGraph)

    User Request: {user_query}

    Instructions:
    1. Analyze the user's request to determine the most appropriate diagram type
    2. Generate clean, valid Mermaid syntax

    Some example Mermaid code snippets for reference:

    Flowchart:
    flowchart LR
    A[Hard] -->|Text| B(Round)
    B --> C
    C -->|One| D[Result 1]
    C -->|Two| E[Result 2]
    

    Sequence diagram:
    sequenceDiagram
    Alice->>John: Hello John, how are you?
    loop HealthCheck
        John->>John: Fight against hypochondria
    end
    Note right of John: Rational thoughts!
    John-->>Alice: Great!
    John->>Bob: How about you?
    Bob-->>John: Jolly good!
    

    Gantt chart:
    gantt
    section Section
    Completed :done,    des1, 2014-01-06,2014-01-08
    Active        :active,  des2, 2014-01-07, 3d
    Parallel 1   :         des3, after des1, 1d
    Parallel 2   :         des4, after des1, 1d
    Parallel 3   :         des5, after des3, 1d
    Parallel 4   :         des6, after des4, 1d
    

    Class diagram:
    classDiagram
    Class01 <|-- AveryLongClass : Cool
    <<Interface>> Class01
    Class09 --> C2 : Where am I?
    Class09 --* C3
    Class09 --|> Class07
    Class07 : equals()
    Class07 : Object[] elementData
    Class01 : size()
    Class01 : int chimp
    Class01 : int gorilla
    

    State diagram:
    stateDiagram-v2
    [*] --> Still
    Still --> [*]
    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]
    

    Pie chart:
    pie
    "Dogs" : 386
    "Cats" : 85.9
    "Rats" : 15
    

    If the request is unclear, ask for clarification about:
    - What type of diagram they want
    - What entities/processes/relationships to include
    - Any specific styling preferences
    - The level of detail required

    **important**
    - don't include any type of html tags
    - don't include any type of markdown formatting

    {format_instruction}
    """,
)

router = APIRouter(prefix="/mermaid", tags=["Mermaid Generation"])


@router.post("/generate", status_code=status.HTTP_200_OK)
async def gen_mermaid(data: MermaidRequest):
    try:
        chain = prompt | gemini | parser

        result = chain.invoke(
            {
                "user_query": data.query,
            }
        )

        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
