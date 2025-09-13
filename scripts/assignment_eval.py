from utils.gemini_util import gemini
from langchain.prompts import PromptTemplate
from schemas.assignment import AssignmentEvalOutput
from langchain_core.output_parsers import PydanticOutputParser

parser = PydanticOutputParser(pydantic_object=AssignmentEvalOutput)

prompt = PromptTemplate(
    template="""
    You are an expert examiner with extensive experience in educational assessment. Your role is to provide constructive, detailed feedback that helps students learn and improve.

    QUESTION: {question}

    REFERENCE ANSWER: {base_answer}

    STUDENT'S ANSWER: {user_answer}

    EVALUATION CRITERIA:
    - Accuracy: How factually correct is the response?
    - Completeness: Does it address all parts of the question?
    - Understanding: Does it demonstrate conceptual grasp?
    - Clarity: Is the explanation clear and well-organized?
    - Depth: Does it show appropriate level of detail?

    SCORING GUIDELINES:
    90-100: Exceptional - Comprehensive, accurate, well-explained
    80-89: Proficient - Good understanding with minor gaps
    70-79: Developing - Basic understanding but missing key elements
    60-69: Beginning - Some correct elements but significant gaps
    0-59: Inadequate - Major misconceptions or insufficient response

    FEEDBACK INSTRUCTIONS:
    1. Start with what the student did well (even if minimal)
    2. Identify specific gaps or errors without being harsh
    3. Explain WHY certain points are important
    4. Provide actionable suggestions for improvement
    5. If applicable, suggest additional resources or study areas
    6. Use encouraging language that motivates further learning
    7. Be specific rather than general in your comments
    8. Focus on learning outcomes, not just correct answers

    Provide your evaluation focusing on helping the student understand both their current performance and how to improve.

    {format_instruction}
    """,
    input_variables=["question", "base_answer", "user_answer"],
    partial_variables={"format_instruction": parser.get_format_instructions()},
)


async def evaluate_assignment(
    question: str, base_answer: str, user_answer: str
) -> AssignmentEvalOutput:
    chain = prompt | gemini | parser

    response = chain.invoke(
        {
            "question": question,
            "base_answer": base_answer,
            "user_answer": user_answer,
        }
    )

    return response
