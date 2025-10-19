from utils.db_util import get_db
from utils.stream_util import stream_create_meeting
from schemas.meetings import CreateMeeting, MeetingStatus
from utils.user_util import get_current_user, get_current_teacher
from fastapi import APIRouter, HTTPException, Depends, status, Path

router = APIRouter(prefix="/meeting", tags=["Classroom Meetings"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_meeting(
    meet: CreateMeeting, db=Depends(get_db), teacher=Depends(get_current_teacher)
):
    try:
        call = await stream_create_meeting(
            user_id=teacher.id,
            class_id=meet.classroomId,
            start_time=meet.meetingTime,
            description=meet.description,
        )
        await db.classmeetings.create(
            data={
                "meetId": call["id"],
                "meetStatus": meet.meetStatus,
                "classroomId": call["classId"],
                "MeetingTime": call["start_time"],
                "description": call["description"],
            }
        )
        return {"detail": "meeting created successfully", "meetId": call["id"]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{meetingId}/status", status_code=status.HTTP_200_OK)
async def get_meeting(
    meetingId: str = Path(..., description="ID of the meeting"),
    db=Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        pass
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.patch("/{meetingId}/status", status_code=status.HTTP_200_OK)
async def update_meeting_status(
    status: MeetingStatus,
    meetingId: str = Path(..., description="ID of the meeting"),
    db=Depends(get_db),
    teacher=Depends(get_current_teacher),
):
    try:
        pass
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
