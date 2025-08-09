from typing import Optional


def format_user_response(user, token: Optional[str] = None) -> dict:
    response = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "createdAt": user.createdAt,
        "updatedAt": user.updatedAt,
    }
    if token:
        response["token"] = token
    return response
