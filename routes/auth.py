from utils.db_util import get_db
from schemas.auth import SignupUser, LoginUser
from utils.format_user_res import format_user_response
from fastapi import APIRouter, HTTPException, Depends, status
from utils.password_util import hash_password, verify_password
from utils.jwt_util import create_access_token, verify_token_bool, verify_token


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: SignupUser, db=Depends(get_db)):
    try:
        existing_user = await db.user.find_unique(where={"email": user.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        hashed_password = hash_password(user.password)
        created_user = await db.user.create(
            data={
                "name": user.name,
                "email": user.email,
                "password": hashed_password,
                "role": user.role.value,
            }
        )
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user",
            )
        return format_user_response(created_user)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(user: LoginUser, db=Depends(get_db)):
    try:
        db_user = await db.user.find_unique(where={"email": user.email})
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email or password",
            )
        if not verify_password(user.password, db_user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email or password",
            )
        token = create_access_token(
            data={"user": {"id": db_user.id, "email": db_user.email}}
        )
        return format_user_response(db_user, token=token)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get("/verify", status_code=status.HTTP_200_OK)
async def verify_user(db=Depends(get_db), data=Depends(verify_token_bool)):
    return data


@router.get("/user", status_code=status.HTTP_200_OK)
async def get_user(db=Depends(get_db), user_data: dict = Depends(verify_token)):
    try:
        userId = user_data.get("user")["id"]
        db_user = await db.user.find_unique(where={"id": userId})
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id"
            )
        token = create_access_token(
            data={"user": {"id": db_user.id, "email": db_user.email}}
        )
        return format_user_response(db_user, token=token)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get User Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
