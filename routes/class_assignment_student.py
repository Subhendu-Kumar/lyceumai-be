import asyncio
from io import BytesIO
import cloudinary.uploader
from utils.db_util import get_db
from utils.cloudinary_util import *
from utils.aai_util import aai_transcriber
from utils.user_util import get_current_student
from scripts.assignment_eval import evaluate_assignment
from fastapi import APIRouter, HTTPException, Depends, status, Path, UploadFile, File
from schemas.assignment import (
    AssignmentTypeEnum,
    AssignmentEvalOutput,
    TextAssignmentSubmission,
)


router = APIRouter(prefix="/assignment", tags=["Class Assignment Student"])


@router.get("/{classId}/list", status_code=status.HTTP_200_OK)
async def list_assignments(
    classId: str = Path(..., description="ID of the class"),
    student=Depends(get_current_student),
    db=Depends(get_db),
):
    try:
        assignments = await db.assignment.find_many(
            where={"classroomId": classId},
            include={
                "submissions": {
                    "where": {"studentId": student.id},
                }
            },
            order={"createdAt": "desc"},
        )

        result = []
        for a in assignments:
            result.append(
                {
                    "id": a.id,
                    "type": a.type,
                    "title": a.title,
                    "dueDate": a.dueDate,
                    "question": a.question,
                    "createdAt": a.createdAt,
                    "isSubmitted": len(a.submissions) > 0,
                }
            )

        return {"assignments": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/s/{assignmentId}", status_code=status.HTTP_200_OK)
async def get_assignment(
    assignmentId: str = Path(..., description="ID of the assignment"),
    student=Depends(get_current_student),
    db=Depends(get_db),
):
    try:
        assignment_db = await db.assignment.find_unique(where={"id": assignmentId})
        assignment = {
            "id": assignment_db.id,
            "type": assignment_db.type,
            "title": assignment_db.title,
            "dueDate": assignment_db.dueDate,
            "question": assignment_db.question,
            "classroomId": assignment_db.classroomId,
        }
        return {"assignment": assignment}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/s/{assignmentId}/submission", status_code=status.HTTP_200_OK)
async def get_student_submission(
    assignmentId: str = Path(..., description="ID of the assignment"),
    student=Depends(get_current_student),
    db=Depends(get_db),
):
    try:
        assignment_db = await db.assignment.find_unique(where={"id": assignmentId})
        if not assignment_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found"
            )
        submission_db = await db.submission.find_first(
            where={"assignmentId": assignmentId, "studentId": student.id},
        )
        if not submission_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found"
            )

        textSubmission = None
        voiceSubmission = None

        if assignment_db.type == AssignmentTypeEnum.TEXT:
            text_submission = await db.textsubmission.find_first(
                where={"submissionId": submission_db.id},
            )
            textSubmission = {
                "id": text_submission.id,
                "score": text_submission.score,
                "content": text_submission.content,
                "feedback": text_submission.feedback,
                "strengths": text_submission.strengths,
                "improvements": text_submission.improvements,
            }
        else:
            voice_submission = await db.voicesubmission.find_first(
                where={"submissionId": submission_db.id},
            )
            voiceSubmission = {
                "id": voice_submission.id,
                "score": voice_submission.score,
                "fileUrl": voice_submission.fileUrl,
                "feedback": voice_submission.feedback,
                "strengths": voice_submission.strengths,
                "transcript": voice_submission.transcript,
                "improvements": voice_submission.improvements,
            }

        assignment = {
            "id": assignment_db.id,
            "type": assignment_db.type,
            "title": assignment_db.title,
            "dueDate": assignment_db.dueDate,
            "question": assignment_db.question,
            "classroomId": assignment_db.classroomId,
        }
        submission_data = {
            "id": submission_db.id,
            "textSubmission": textSubmission,
            "voiceSubmission": voiceSubmission,
            "submittedAt": submission_db.submittedAt,
        }

        return {
            "assignment": assignment,
            "submission": submission_data,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/{assignmentId}/submit/text", status_code=status.HTTP_201_CREATED)
async def submit_text_assignment(
    data: TextAssignmentSubmission,
    assignmentId: str = Path(..., description="ID of the assignment"),
    student=Depends(get_current_student),
    db=Depends(get_db),
):
    try:
        existing_assignment = await db.assignment.find_unique(
            where={"id": assignmentId, "type": "TEXT"}
        )
        if not existing_assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found"
            )
        submission = await db.submission.create(
            data={
                "studentId": student.id,
                "assignmentId": assignmentId,
            }
        )
        eval_result: AssignmentEvalOutput = await evaluate_assignment(
            existing_assignment.question, existing_assignment.referenceAns, data.content
        )
        await db.textsubmission.create(
            data={
                "content": data.content,
                "score": eval_result.score,
                "submissionId": submission.id,
                "feedback": eval_result.feedback,
                "strengths": eval_result.strengths,
                "improvements": eval_result.areas_for_improvement,
            }
        )
        return {
            "detail": "Text assignment submitted successfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/{assignmentId}/submit/voice", status_code=status.HTTP_201_CREATED)
async def submit_voice_assignment(
    voice_ans: UploadFile = File(...),
    assignmentId: str = Path(..., description="ID of the assignment"),
    student=Depends(get_current_student),
    db=Depends(get_db),
):
    try:
        existing_assignment = await db.assignment.find_unique(
            where={"id": assignmentId, "type": "VOICE"}
        )
        if not existing_assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found"
            )

        file_bytes = await voice_ans.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty audio file.")

        async def upload_file() -> str:
            file_res = cloudinary.uploader.upload(
                BytesIO(file_bytes),
                resource_type="auto",
                folder=f"submissions/{assignmentId}/{student.id}",
                access_mode="public",
            )
            if not file_res:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="file upload failed",
                )
            return file_res.get("secure_url")

        async def transcribe_file() -> str:
            transcript = aai_transcriber.transcribe(BytesIO(file_bytes))
            if transcript.status == "error":
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Transcription failed: {transcript.error}",
                )
            return transcript.text

        file_url, transcript_text = await asyncio.gather(
            upload_file(),
            transcribe_file(),
        )

        submission = await db.submission.create(
            data={
                "studentId": student.id,
                "assignmentId": assignmentId,
            }
        )

        eval_result: AssignmentEvalOutput = await evaluate_assignment(
            existing_assignment.question,
            existing_assignment.referenceAns,
            transcript_text,
        )

        await db.voicesubmission.create(
            data={
                "fileUrl": file_url,
                "score": eval_result.score,
                "transcript": transcript_text,
                "submissionId": submission.id,
                "feedback": eval_result.feedback,
                "strengths": eval_result.strengths,
                "improvements": eval_result.areas_for_improvement,
            }
        )

        return {
            "detail": "Voice assignment submitted successfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
