import asyncio
from utils.db_util import get_db
from utils.user_util import get_current_user, get_current_teacher
from fastapi import APIRouter, HTTPException, Depends, status, Path
from schemas.classroom import AddStudentToClass, RemoveStudentFromClass


router = APIRouter(prefix="/class", tags=["Class Room Enrollment"])


@router.post("/enroll/s/{code}", status_code=status.HTTP_200_OK)
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


@router.delete("/unenroll/s/{classId}", status_code=status.HTTP_202_ACCEPTED)
async def unenroll_student(
    classId: str = Path(..., description="ID of the classroom"),
    user: dict = Depends(get_current_user),
    db=Depends(get_db),
):
    try:
        existing_enrollment = await db.enrollment.find_first(
            where={"studentId": user.id, "classroomId": classId}
        )
        if not existing_enrollment:
            raise HTTPException(
                status_code=400, detail="Student is not enrolled in this classroom"
            )
        await db.enrollment.delete(
            where={
                "studentId_classroomId": {"studentId": user.id, "classroomId": classId}
            }
        )
        return {"detail": "Student unenrolled successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/add/student", status_code=status.HTTP_201_CREATED)
async def add_student_to_class(
    data: AddStudentToClass, teacher=Depends(get_current_teacher), db=Depends(get_db)
):
    try:
        class_room, student = await asyncio.gather(
            db.classroom.find_unique(where={"id": data.class_id}),
            db.user.find_first(where={"email": data.email}),
        )
        if not class_room:
            raise HTTPException(status_code=404, detail="Classroom not found")
        if not student:
            # send invitation email to the student
            raise HTTPException(status_code=404, detail="Student not found")
        existing_enrollment = await db.enrollment.find_first(
            where={"studentId": student.id, "classroomId": class_room.id}
        )
        if existing_enrollment:
            raise HTTPException(
                status_code=404, detail="Student is already enrolled in this classroom"
            )
        enrollment = await db.enrollment.create(
            data={"studentId": student.id, "classroomId": class_room.id}
        )
        return {
            "detail": "Student added to class successfully",
            "enrollment": enrollment,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/remove/student", status_code=status.HTTP_202_ACCEPTED)
async def remove_student_from_class(
    data: RemoveStudentFromClass,
    teacher=Depends(get_current_teacher),
    db=Depends(get_db),
):
    try:
        existing_enrollment = await db.enrollment.find_first(
            where={"studentId": data.student_id, "classroomId": data.class_id}
        )
        if not existing_enrollment:
            raise HTTPException(
                status_code=404, detail="Student is not enrolled in this classroom"
            )
        await db.enrollment.delete(
            where={
                "studentId_classroomId": {
                    "studentId": data.student_id,
                    "classroomId": data.class_id,
                }
            }
        )
        return {"detail": "Student removed from class successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/peoples/{classId}", status_code=status.HTTP_200_OK)
async def get_class_peoples(
    classId: str = Path(..., description="ID of the classroom"),
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    try:
        class_room = await db.classroom.find_unique(where={"id": classId})
        if not class_room:
            raise HTTPException(status_code=404, detail="Classroom not found")
        students = await db.enrollment.find_many(
            where={"classroomId": class_room.id},
            include={"student": True},
            order={"joinedAt": "desc"},
        )
        return {"students": students}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
