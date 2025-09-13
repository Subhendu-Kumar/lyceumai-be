from utils.db_util import get_db
from schemas.assignment import AssignmentBase
from utils.user_util import get_current_teacher
from fastapi import APIRouter, HTTPException, Depends, status, Path

router = APIRouter(prefix="/assignment", tags=["Classroom Assignment Admin"])


@router.post("/create/{classroom_id}", status_code=status.HTTP_201_CREATED)
async def create_assignment(
    data: AssignmentBase,
    classroom_id: str = Path(..., description="ID of the classroom"),
    teacher=Depends(get_current_teacher),
    db=Depends(get_db),
):
    try:
        existing_class = await db.classroom.find_unique(where={"id": classroom_id})
        if not existing_class:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Classroom not found"
            )
        assignment = await db.assignment.create(
            data={
                "title": data.title,
                "dueDate": data.dueDate,
                "type": data.type.value,
                "teacherId": teacher.id,
                "question": data.question,
                "classroomId": classroom_id,
                "referenceAns": data.referenceAns,
            },
        )
        return {"assignment": assignment, "detail": "Assignment created successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/all/{classroom_id}", status_code=status.HTTP_200_OK)
async def get_all_assignments(
    classroom_id: str = Path(..., description="ID of the classroom"),
    teacher=Depends(get_current_teacher),
    db=Depends(get_db),
):
    try:
        assignments = await db.assignment.find_many(where={"classroomId": classroom_id})
        return {"assignments": assignments}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{assignment_id}", status_code=status.HTTP_200_OK)
async def get_assignment(
    assignment_id: str = Path(..., description="ID of the assignment"),
    teacher=Depends(get_current_teacher),
    db=Depends(get_db),
):
    try:
        assignment = await db.assignment.find_unique(where={"id": assignment_id})
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found"
            )
        return {"assignment": assignment}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{assignment_id}", status_code=status.HTTP_200_OK)
async def delete_assignment(
    assignment_id: str = Path(..., description="ID of the assignment"),
    teacher=Depends(get_current_teacher),
    db=Depends(get_db),
):
    try:
        existing_assignment = await db.assignment.find_unique(
            where={"id": assignment_id}
        )
        if not existing_assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found"
            )
        await db.assignment.delete(where={"id": assignment_id})
        return {"detail": f"Assignment {assignment_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
