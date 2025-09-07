from utils.db_util import get_db
from utils.user_util import get_current_student
from fastapi import APIRouter, Depends, HTTPException, status, Path

router = APIRouter(prefix="/class", tags=["Class Students"])


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


@router.get("/{classId}", status_code=status.HTTP_200_OK)
async def get_class_by_id_student(
    classId: str = Path(..., description="ID of the classroom"),
    student=Depends(get_current_student),
    db=Depends(get_db),
):
    try:
        enrollment = await db.enrollment.find_unique(
            where={
                "studentId_classroomId": {
                    "studentId": student.id,
                    "classroomId": classId,
                }
            },
            include={"classroom": True},
        )
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Classroom not found or not enrolled",
            )
        return {"class": enrollment.classroom}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/materials/{classId}", status_code=status.HTTP_200_OK)
async def get_all_materials_student(
    classId: str = Path(..., description="ID of the classroom"),
    student=Depends(get_current_student),
    db=Depends(get_db),
):
    try:
        materials = await db.material.find_many(
            where={"classroomId": classId},
            order={"uploadedAt": "desc"},
        )
        return {"materials": materials}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/quizzes/{classId}", status_code=status.HTTP_200_OK)
async def get_all_quizzes_student(
    classId: str = Path(..., description="ID of the classroom"),
    student=Depends(get_current_student),
    db=Depends(get_db),
):
    try:
        quizzes = await db.quiz.find_many(
            where={
                "AND": [
                    {"classroomId": classId},
                    {"published": True},
                ]
            },
            order={"updatedAt": "desc"},
        )
        return {"quizzes": quizzes}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
