from utils.db_util import get_db
from utils.jwt_util import verify_token
from fastapi import Depends, HTTPException, status


async def get_current_user(user_data: dict = Depends(verify_token), db=Depends(get_db)):
    user_id = user_data.get("user")["id"]
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id"
        )
    return user


async def get_current_teacher(user=Depends(get_current_user)):
    if user.role != "TEACHER":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is not a teacher"
        )
    return user


async def get_current_student(user=Depends(get_current_user)):
    if user.role != "STUDENT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User is not a student"
        )
    return user
