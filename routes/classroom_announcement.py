from utils.db_util import get_db
from utils.user_util import get_current_teacher
from fastapi import APIRouter, status, Depends, HTTPException, Path
from schemas.classroom import ClassAnnouncementCreate, ClassAnnouncementUpdate

router = APIRouter(prefix="/class", tags=["Classroom Announcements"])


@router.post("/announcement", status_code=status.HTTP_201_CREATED)
async def create_announcement(
    announcement: ClassAnnouncementCreate,
    teacher=Depends(get_current_teacher),
    db=Depends(get_db),
):
    try:
        existing_class = await db.classroom.find_unique(
            where={"id": announcement.class_id}
        )
        if not existing_class:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Classroom not found"
            )
        new_announcement = await db.announcement.create(
            data={
                "title": announcement.title,
                "message": announcement.message,
                "classroomId": announcement.class_id,
            }
        )
        # TODO implement notification
        return {"announcement": new_announcement}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/announcements/{classroom_id}", status_code=status.HTTP_200_OK)
async def get_announcements(
    classroom_id: str = Path(..., description="ID of the classroom"), db=Depends(get_db)
):
    try:
        announcements = await db.announcement.find_many(
            where={"classroomId": classroom_id}
        )
        return {"announcements": announcements}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/announcement/{announcement_id}", status_code=status.HTTP_200_OK)
async def update_announcement(
    announcement: ClassAnnouncementUpdate,
    announcement_id: str = Path(..., description="ID of the announcement"),
    teacher=Depends(get_current_teacher),
    db=Depends(get_db),
):
    try:
        existing_announcement = await db.announcement.find_unique(
            where={"id": announcement_id}
        )
        if not existing_announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found"
            )
        updated_announcement = await db.announcement.update(
            where={"id": announcement_id},
            data={
                "title": announcement.title,
                "message": announcement.message,
            },
        )
        return {"announcement": updated_announcement}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete(
    "/announcement/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_announcement(
    announcement_id: str = Path(..., description="ID of the announcement"),
    teacher=Depends(get_current_teacher),
    db=Depends(get_db),
):
    try:
        existing_announcement = await db.announcement.find_unique(
            where={"id": announcement_id}
        )
        if not existing_announcement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Announcement not found"
            )
        await db.announcement.delete(where={"id": announcement_id})
        return {"detail": "Announcement deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
