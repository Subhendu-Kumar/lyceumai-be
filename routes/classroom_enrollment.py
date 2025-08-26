from fastapi import APIRouter, HTTPException, Depends, status, Path
from utils.user_util import get_current_user
from utils.db_util import get_db


router = APIRouter(prefix="/class", tags=["Class Room Enrollment"])


@router.post("/enroll/{code}", status_code=status.HTTP_200_OK)
async def enroll_student(
    code: str = Path(..., description="code of the classroom"),
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    try:
        class_room = await db.classroom.find_unique(where={"code": code})
        if not class_room:
            raise HTTPException(status_code=404, detail="Classroom not found")
        existing_enrollment = await db.enrollment.find_first(
            where={"studentId": user.id, "classroomId": class_room.id}
        )
        if existing_enrollment:
            raise HTTPException(
                status_code=400, detail="Student is already enrolled in this classroom"
            )
        enrolled = await db.enrollment.create(
            data={"studentId": user.id, "classroomId": class_room.id}
        )
        return {"detail": "Student enrolled successfully", "enrollment": enrolled}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
