from utils.get_fcm_tokens import get_fcm_tokens
from services.notification_service import send_fcm_notification


async def get_tokens_and_send_notification(
    title: str, body: str, class_id: str, db, sub_route: str = ""
):
    tokens = await get_fcm_tokens(class_id, db)

    await send_fcm_notification(
        title=title, body=body, route=f"/class/{class_id}{sub_route}", tokens=tokens
    )
