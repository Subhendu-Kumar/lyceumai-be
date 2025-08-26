import random
import string
from fastapi import Depends
from utils.db_util import get_db


async def gen_class_code(db=Depends(get_db)) -> str:
    while True:
        # Generate a 9-character random alphanumeric string
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=9))

        # Check if classroom with this code already exists
        existing = await db.classroom.find_first(where={"code": code})

        if not existing:
            return code
