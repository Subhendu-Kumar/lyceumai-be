from utils.db_util import get_db
from utils.stream_util import (
    stream_create_meeting,
    CallbackData,
    get_meetings,
    get_recording_by_meet_id,
    Recording,
)
from schemas.meetings import CreateMeeting, MeetingStatus
from utils.user_util import get_current_user, get_current_teacher
from fastapi import APIRouter, HTTPException, Depends, status, Path
from enum import Enum
from typing import List
from datetime import datetime

router = APIRouter(prefix="/meeting", tags=["Classroom Meetings"])


class MeetingType(str, Enum):
    ended = "ended"
    upcoming = "upcoming"


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_meeting(
    meet: CreateMeeting, db=Depends(get_db), teacher=Depends(get_current_teacher)
):
    try:
        call: CallbackData = await stream_create_meeting(
            user_id=teacher.id,
            class_id=meet.classroomId,
            start_time=meet.meetingTime,
            description=meet.description,
        )
        await db.classmeetings.create(
            data={
                "meetId": call.id,
                "meetStatus": meet.meetStatus,
                "classroomId": call.classId,
                "MeetingTime": call.start_time,
                "description": call.description,
            }
        )
        return {"detail": "meeting created successfully", "meetId": call.id}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/list/{class_id}/{type}", status_code=status.HTTP_200_OK)
async def get_all_meets_by_class_id(
    class_id: str = Path(..., description="ID of the class"),
    type: MeetingType = Path(..., description="Type of the meeting"),
    user=Depends(get_current_user),
):
    try:
        meetings: List[CallbackData] = await get_meetings(
            class_id=class_id, user_id=user.id
        )
        now = datetime.now().isoformat()
        filtered: List[CallbackData] = []
        if type == MeetingType.ended:
            filtered = [m for m in meetings if m.end_time is not None]
        elif type == MeetingType.upcoming:
            filtered = [
                m
                for m in meetings
                if (m.start_time and m.start_time > now) or m.end_time is None
            ]
        else:
            filtered = meetings

        return {"meetings": filtered}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{meet_id}", status_code=status.HTTP_200_OK)
async def get_meeting_details(
    meet_id: str = Path(..., description="ID of the meeting"),
    db=Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        meeting = await db.classmeetings.find_first(where={"meetId": meet_id})
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found"
            )

        recordings: List[Recording] = await get_recording_by_meet_id(
            meet_id=meet_id, user_id=user.id
        )

        rec_data = []
        for rec in recordings:
            url = rec.url
            meet_date = rec.date
            session_id = rec.session_id

            meeting_data = await db.meetingdata.find_first(
                where={"sessionId": session_id}
            )
            if not meeting_data:
                rec_data.append(
                    {
                        "url": url,
                        "meet_date": meet_date,
                        "session_id": session_id,
                        "transcript": None,
                        "summary": None,
                    }
                )
            else:
                rec_data.append(
                    {
                        "url": url,
                        "meet_date": meet_date,
                        "session_id": session_id,
                        "transcript": meeting_data.transcript,
                        "summary": meeting_data.summary,
                    }
                )

        meeting_response_data = {
            "meetId": meeting.meetId,
            "meetStatus": meeting.meetStatus,
            "classroomId": meeting.classroomId,
            "MeetingTime": meeting.MeetingTime,
            "description": meeting.description,
            "recordings": rec_data,
        }

        return {"meeting": meeting_response_data}
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
