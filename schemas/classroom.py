from pydantic import BaseModel


class CreateOrUpdateClassRoom(BaseModel):
    name: str
    description: str
