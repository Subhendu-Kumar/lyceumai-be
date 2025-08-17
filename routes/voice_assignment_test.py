# from uuid import uuid4
# import cloudinary.uploader

from fastapi import APIRouter, HTTPException, status, UploadFile, File
from elevenlabs.client import ElevenLabs
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import os
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()

gemini = ChatGoogleGenerativeAI(model="gemini-2.5-pro")

elevenlabs = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

question = (
    "What is the difference between a process and a thread in an operating system?"
)

base_answer = """A process is an independent program in execution with its own memory space, resources, and scheduling.

A thread is a lightweight unit of execution within a process that shares the same memory and resources of the process but has its own execution path (program counter, stack, and registers).

Threads are faster to create and switch between compared to processes because they avoid the overhead of separate memory allocation."""


class OutputFormat(BaseModel):
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


parser = PydanticOutputParser(pydantic_object=OutputFormat)

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


router = APIRouter(prefix="/voice", tags=["Voice Assignment"])


@router.post("/eval", status_code=status.HTTP_200_OK)
async def voice_assignment(audio_ans: UploadFile = File(...)):
    try:
        # audio_ans_id = str(uuid4())
        # audio_ans_res = await cloudinary.uploader.upload(
        #     audio_ans.file, resource_type="auto", folder=f"songs/{audio_ans_id}"
        # )
        # if not audio_ans_res:
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail="song upload failed",
        #     )

        audio_bytes = await audio_ans.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty audio file.")

        a_file = BytesIO(audio_bytes)
        a_file.name = "Recording.m4a"

        transcription = elevenlabs.speech_to_text.convert(
            file=a_file,
            model_id="scribe_v1",  # Model to use, for now only "scribe_v1" is supported
            tag_audio_events=True,  # Tag audio events like laughter, applause, etc.
            language_code="eng",  # Language of the audio file. If set to None, the model will detect the language automatically.
            diarize=True,  # Whether to annotate who is speaking
        )

        chain = prompt | gemini | parser

        result = chain.invoke(
            {
                "question": question,
                "base_answer": base_answer,
                "user_answer": transcription.text,
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
