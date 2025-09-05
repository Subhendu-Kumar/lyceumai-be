from dotenv import load_dotenv
from utils.db_util import get_db
from utils.gemini_util import gemini
from utils.user_util import get_current_user
from langchain.prompts import PromptTemplate
from schemas.classroom import ClassQuizBody, QuizResponse
from langchain.output_parsers import PydanticOutputParser
from fastapi import APIRouter, HTTPException, Depends, status, Path
from utils.chroma_util import syllabus_vector_store, class_material_vector_store
import asyncio

load_dotenv()

router = APIRouter(prefix="/quiz", tags=["Classroom Quiz"])


parser = PydanticOutputParser(pydantic_object=QuizResponse)

template = PromptTemplate(
    input_variables=[
        "title",
        "topic",
        "syllabus",
        "materials",
        "difficulty",
        "description",
        "number_of_questions",
    ],
    partial_variables={"format_instruction": parser.get_format_instructions()},
    template="""
        You are an expert educational content creator.

        Task: Generate {number_of_questions} high-quality questions based on the given details.

        Title: {title}
        Topic: {topic}
        Difficulty: {difficulty}
        Description: {description}
        Syllabus: {syllabus}
        Materials: {materials}

        Guidelines:
        - Ensure all questions are strictly within the provided syllabus, class materials and aligned with the description and topic.
        - Match the difficulty level accurately:
            - Easy: basic recall or understanding
            - Medium: requires some reasoning or multi-step thinking
            - Hard: advanced critical thinking, problem-solving, or application
        - Questions should be diverse (not repeating the same structure).
        - Avoid vague or ambiguous wording.

        {format_instruction}
    """,
)


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_quiz(
    data: ClassQuizBody, user=Depends(get_current_user), db=Depends(get_db)
):
    try:
        existing_class = await db.classroom.find_first(where={"id": data.class_id})
        if not existing_class:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Classroom with this {data.class_id} is not exists",
            )
        query = f"{data.title}, {data.topic}, {data.description}"
        docs_syllabus, docs_materials = await asyncio.gather(
            asyncio.to_thread(
                syllabus_vector_store.similarity_search,
                query,
                2,
                {"class_id": data.class_id},
            ),
            asyncio.to_thread(
                class_material_vector_store.similarity_search,
                query,
                4,
                {"class_id": data.class_id},
            ),
        )
        syllabus = "\n".join([doc.page_content for doc in docs_syllabus])
        materials = "\n".join([doc.page_content for doc in docs_materials])
        chain = template | gemini | parser
        result = chain.invoke(
            {
                "title": data.title,
                "topic": data.topic,
                "syllabus": syllabus,
                "materials": materials,
                "difficulty": data.difficulty,
                "description": data.description,
                "number_of_questions": data.number_of_questions,
            }
        )
        formatted_questions = [q.dict() for q in result.questions]
        quiz = await db.quiz.create(
            data={
                "title": result.title,
                "description": result.description,
                "creatorId": user.id,
                "classroomId": data.class_id,
                "questions": {"create": formatted_questions},
            }
        )
        return {"quiz": quiz, "detail": "Quiz generated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/all/{class_id}", status_code=status.HTTP_200_OK)
async def get_all_quizzes_of_class(
    class_id: str = Path(..., description="ID of the classroom"), db=Depends(get_db)
):
    try:
        quizzes = await db.quiz.find_many(
            where={"classroomId": class_id}, order={"createdAt": "desc"}
        )
        return {"quizzes": quizzes}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{quiz_id}", status_code=status.HTTP_200_OK)
async def get_quiz_by_id(
    quiz_id: str = Path(..., description="ID of the quiz"), db=Depends(get_db)
):
    try:
        quiz = await db.quiz.find_first(
            where={"id": quiz_id}, include={"questions": True}
        )
        return {"quiz": quiz}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.patch("/publish/{quiz_id}", status_code=status.HTTP_202_ACCEPTED)
async def publish_quiz(
    quiz_id: str = Path(..., description="Id of the quiz"), db=Depends(get_db)
):
    try:
        await db.quiz.update(where={"id": quiz_id}, data={"published": True})
        return {"detail": "Quiz published successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.patch("/question/{question_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_quiz_question():
    try:
        pass
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
