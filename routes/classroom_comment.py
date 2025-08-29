from utils.db_util import get_db
from utils.user_util import get_current_user
from fastapi import APIRouter, status, Depends, HTTPException, Path

router = APIRouter(prefix="/class", tags=["Classroom Comments"])


@router.post("/comment", status_code=status.HTTP_201_CREATED)
async def create_comment(
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    pass


@router.get("/comments", status_code=status.HTTP_200_OK)
async def get_comments(
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    pass


@router.put("/comment", status_code=status.HTTP_200_OK)
async def update_comment(
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    pass


@router.delete("/comment", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    pass
