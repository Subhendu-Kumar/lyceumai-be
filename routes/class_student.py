import select
from fastapi import APIRouter, Depends, HTTPException, status, Path
from utils.user_util import get_current_student
from utils.db_util import get_db

router = APIRouter(prefix="/classes", tags=["Class Students"])


@router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_class_students(
    student=Depends(get_current_student), db=Depends(get_db)
):
    try:
        enrollments = await db.enrollment.find_many(
            where={"studentId": student.id},
            include={"classroom": True},
            order={"joinedAt": "desc"},
        )
        classes = [enrollment.classroom for enrollment in enrollments]
        return {"classes": classes}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
