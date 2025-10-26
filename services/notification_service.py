import firebase_admin
from typing import List
from firebase_admin import credentials
from firebase_admin.messaging import (
    Notification,
    AndroidConfig,
    MulticastMessage,
    AndroidNotification,
    send_each_for_multicast_async,
)

cred = credentials.Certificate(
    "lyceumai-notification-firebase-adminsdk-fbsvc-de004a5937.json"
)
firebase_admin.initialize_app(cred)


async def send_fcm_notification(title: str, body: str, route: str, tokens: List[str]):
    message = MulticastMessage(
        notification=Notification(
            title=title,
            body=body,
        ),
        data={
            "click_action": "FLUTTER_NOTIFICATION_CLICK",
            "route": route,
        },
        android=AndroidConfig(
            priority="high",
            notification=AndroidNotification(
                channel_id="high_importance_channel",
            ),
        ),
        tokens=tokens,
    )

    response = await send_each_for_multicast_async(message)

    print(
        f"FCM Notification :\n\nSuccess: {response.success_count}, Failure: {response.failure_count}"
    )
