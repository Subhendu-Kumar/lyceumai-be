import random
import string
from datetime import datetime

from utils.db_util import get_db
from fastapi import Depends


async def gen_class_code(db=Depends(get_db)) -> str:
    while True:
        # Generate a 9-character random alphanumeric string
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=9))

        # Check if classroom with this code already exists
        existing = await db.classroom.find_first(where={"code": code})

        if not existing:
            return code


async def gen_class_code_recommended():
    """Recommended: 12-character code with timestamp and random parts"""
    now = datetime.now()

    # YYMMSS (6 digits) + 6 random characters
    time_part = now.strftime("%H%M%S")
    random_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    code = f"{time_part}-{random_part}"

    return code
