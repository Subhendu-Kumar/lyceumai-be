from utils.db_util import get_db
from utils.user_util import get_current_student
from schemas.assignment import TextAssignmentSubmission
from fastapi import APIRouter, HTTPException, Depends, status, Path

router = APIRouter(prefix="/assignment", tags=["Class Assignment Student"])


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
        await db.textsubmission.create(
            data={
                "content": data.content,
                "submissionId": submission.id,
            }
        )
        return {
            "detail": "Text assignment submitted successfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
