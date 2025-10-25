from pydantic import BaseModel
from utils.db_util import get_db
from utils.user_util import get_current_user
from fastapi import APIRouter, status, HTTPException, Depends

notification_service_router = APIRouter(
    prefix="/fcm", tags=["FCM Notification Service"]
)


class FCMTokenRequest(BaseModel):
    token: str


@notification_service_router.post("/add-token", status_code=status.HTTP_200_OK)
async def add_fcm_token(
    data: FCMTokenRequest, db=Depends(get_db), user=Depends(get_current_user)
):
    try:
        user_id = user.id
        new_token = data.token
        await db.fcmtoken.upsert(
            where={"userId": user_id},
            data={
                "create": {
                    "userId": user_id,
                    "fcmToken": new_token,
                },
                "update": {
                    "fcmToken": new_token,
                },
            },
        )
        return {"detail": "FCM token added/updated successfully"}
    except Exception as e:
        print(f"Error adding FCM token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
