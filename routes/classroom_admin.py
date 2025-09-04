import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from utils.gemini_util import embeddings
from utils.db_util import get_db
from utils.user_util import get_current_teacher
from schemas.classroom import CreateOrUpdateClassRoom
from utils.class_code_util import gen_class_code_recommended
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Path,
    File,
    UploadFile,
    Form,
)
import tempfile
from io import BytesIO
from utils.cloudinary_util import *
import cloudinary.uploader
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()

router = APIRouter(prefix="/admin", tags=["Classroom Admin"])

vector_store = Chroma(
    collection_name="class-syllabus",
    embedding_function=embeddings,
    chroma_cloud_api_key=os.getenv("CHROMA_API_KEY"),
    tenant=os.getenv("CHROMA_TENANT"),
    database=os.getenv("CHROMA_DATABASE"),
)


@router.post("/classroom", status_code=status.HTTP_201_CREATED)
async def create_classroom(
    name: str = Form(...),
    description: str = Form(...),
    syllabus: UploadFile = File(...),
    db=Depends(get_db),
    teacher=Depends(get_current_teacher),
):
    try:
        code = await gen_class_code_recommended()
        existing_class = await db.classroom.find_first(where={"code": code})
        if existing_class:
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Classroom with this code already exists",
            )
        file_bytes = await syllabus.read()
        file_res = cloudinary.uploader.upload(
            BytesIO(file_bytes),
            resource_type="auto",
            folder=f"syllabus/{code}",
            access_mode="public",
        )
        if not file_res:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="file upload failed",
            )
        file_url = file_res.get("secure_url")
        db_classroom = await db.classroom.create(
            data={
                "name": name,
                "description": description,
                "teacherId": teacher.id,
                "code": code,
                "syllabusUrl": file_url,
            }
        )
        if not db_classroom:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create classroom",
            )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        for doc in docs:
            doc.metadata["class_id"] = db_classroom.id
        vector_store.add_documents(docs)
        return {
            "message": "Classroom created successfully",
            "classroom": db_classroom,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get User Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.get("/classrooms", status_code=status.HTTP_200_OK)
async def get_classrooms(db=Depends(get_db), teacher=Depends(get_current_teacher)):
    try:
        classrooms = await db.classroom.find_many(where={"teacherId": teacher.id})
        return {"classrooms": classrooms}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get User Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get("/classroom/{classId}", status_code=status.HTTP_200_OK)
async def get_classroom(
    db=Depends(get_db),
    classId: str = Path(..., description="ID of the classroom"),
    teacher=Depends(get_current_teacher),
):
    try:
        classroom = await db.classroom.find_unique(
            where={"teacherId": teacher.id, "id": classId}
        )
        return {"classroom": classroom}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get User Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.patch("/classroom/{classId}", status_code=status.HTTP_202_ACCEPTED)
async def update_classroom(
    class_data: CreateOrUpdateClassRoom,
    db=Depends(get_db),
    teacher=Depends(get_current_teacher),
    classId: str = Path(..., description="ID of the classroom"),
):
    try:
        existing_classroom = await db.classroom.find_unique(
            where={"id": classId, "teacherId": teacher.id}
        )
        if not existing_classroom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found"
            )
        classroom = await db.classroom.update(
            where={
                "id": classId,
            },
            data={
                "name": class_data.name,
                "description": class_data.description,
            },
        )
        return {"classroom": classroom}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get User Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.delete("/classroom/{classId}", status_code=status.HTTP_202_ACCEPTED)
async def delete_classroom(
    db=Depends(get_db),
    teacher=Depends(get_current_teacher),
    classId: str = Path(..., description="ID of the classroom"),
):
    try:
        existing_classroom = await db.classroom.find_unique(
            where={"id": classId, "teacherId": teacher.id}
        )
        if not existing_classroom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found"
            )
        await db.classroom.delete(where={"id": classId})
        return {"detail": "Classroom deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get User Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
