from utils.db_util import get_db
from utils.user_util import get_current_teacher
from utils.class_code_util import gen_class_code
from schemas.classroom import CreateOrUpdateClassRoom
from fastapi import APIRouter, HTTPException, Depends, status, Path

router = APIRouter(prefix="/admin", tags=["Classroom Admin"])


@router.post("/classroom", status_code=status.HTTP_201_CREATED)
async def create_classroom(
    class_room: CreateOrUpdateClassRoom,
    db=Depends(get_db),
    teacher=Depends(get_current_teacher),
):
    try:
        class_code = await gen_class_code()
        db_classroom = await db.classroom.create(
            data={
                "name": class_room.name,
                "description": class_room.description,
                "teacherId": teacher.id,
                "code": class_code,
            }
        )
        if not db_classroom:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create classroom",
            )
        return {
            "message": "Classroom created successfully",
            "classroom": db_classroom,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get User Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get("/classrooms", status_code=status.HTTP_200_OK)
async def get_classrooms(db=Depends(get_db), teacher=Depends(get_current_teacher)):
    try:
        classrooms = await db.classroom.find_many(where={"teacherId": teacher.id})
        return {"classrooms": classrooms}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get User Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get("/classroom/{classId}", status_code=status.HTTP_200_OK)
async def get_classroom(
    db=Depends(get_db),
    classId: str = Path(..., description="ID of the classroom"),
    teacher=Depends(get_current_teacher),
):
    try:
        classroom = await db.classroom.find_unique(
            where={"teacherId": teacher.id, "id": classId}
        )
        return {"classroom": classroom}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get User Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.patch("/classroom/{classId}", status_code=status.HTTP_202_ACCEPTED)
async def update_classroom(
    class_data: CreateOrUpdateClassRoom,
    db=Depends(get_db),
    teacher=Depends(get_current_teacher),
    classId: str = Path(..., description="ID of the classroom"),
):
    try:
        existing_classroom = await db.classroom.find_unique(
            where={"id": classId, "teacherId": teacher.id}
        )
        if not existing_classroom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found"
            )
        classroom = await db.classroom.update(
            where={
                "id": classId,
            },
            data={
                "name": class_data.name,
                "description": class_data.description,
            },
        )
        return {"classroom": classroom}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get User Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.delete("/classroom/{classId}", status_code=status.HTTP_202_ACCEPTED)
async def delete_classroom(
    db=Depends(get_db),
    teacher=Depends(get_current_teacher),
    classId: str = Path(..., description="ID of the classroom"),
):
    try:
        existing_classroom = await db.classroom.find_unique(
            where={"id": classId, "teacherId": teacher.id}
        )
        if not existing_classroom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found"
            )
        await db.classroom.delete(where={"id": classId})
        return {"detail": "Classroom deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get User Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
