import os
import cloudinary
from dotenv import load_dotenv

load_dotenv()

CLOUDINARY_CLIENT_NAME = os.getenv("CLOUDINARY_CLIENT_NAME")
CLOUDINARY_CLIENT_API = os.getenv("CLOUDINARY_CLIENT_API")
CLOUDINARY_CLIENT_SECRET = os.getenv("CLOUDINARY_CLIENT_SECRET")


cloudinary.config(
    cloud_name=CLOUDINARY_CLIENT_NAME,
    api_key=CLOUDINARY_CLIENT_API,
    api_secret=CLOUDINARY_CLIENT_SECRET,
    secure=True,
)
