from typing import List
from fastapi import Depends
from utils.db_util import get_db


async def get_fcm_tokens(class_id: str, db=Depends(get_db)) -> List[str]:
    try:
        tokens = await db.fcmtoken.find_many(
            where={"user": {"enrollments": {"some": {"classroomId": class_id}}}},
        )

        token_list = [t.fcmToken for t in tokens]

        return token_list
    except Exception as e:
        print(f"Error fetching FCM tokens: {e}")
        return []
