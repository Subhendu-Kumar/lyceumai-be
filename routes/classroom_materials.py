import cloudinary.uploader
from utils.db_util import get_db
from utils.cloudinary_util import *
import os
import tempfile
from io import BytesIO
from dotenv import load_dotenv
from utils.chroma_util import class_material_vector_store
from prisma.errors import RecordNotFoundError
from utils.user_util import get_current_teacher
from langchain_community.document_loaders import PyPDFLoader
from fastapi import (
    Form,
    Path,
    File,
    status,
    Depends,
    APIRouter,
    UploadFile,
    HTTPException,
)

load_dotenv()

router = APIRouter(prefix="/class", tags=["Classroom Materials"])


@router.post("/material", status_code=status.HTTP_201_CREATED)
async def create_material(
    title: str = Form(...),
    file: UploadFile = File(...),
    classroomId: str = Form(...),
    teacher=Depends(get_current_teacher),
    db=Depends(get_db),
):
    try:
        existing_class = await db.classroom.find_unique(where={"id": classroomId})
        if not existing_class:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Classroom not found"
            )
        file_bytes = await file.read()
        file_res = cloudinary.uploader.upload(
            BytesIO(file_bytes),
            resource_type="auto",
            folder=f"materials/{classroomId}",
            access_mode="public",
        )
        if not file_res:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="file upload failed",
            )
        file_url = file_res.get("secure_url")
        material = await db.material.create(
            data={
                "title": title,
                "fileUrl": file_url,
                "classroomId": classroomId,
            }
        )
        if not material:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Material creation failed",
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        for doc in docs:
            doc.metadata["material_id"] = material.id
            doc.metadata["class_id"] = existing_class.id
        class_material_vector_store.add_documents(docs)

        return {"material": material}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.get("/materials/{classroom_id}", status_code=status.HTTP_200_OK)
async def get_materials(
    classroom_id: str = Path(..., description="ID of the classroom"), db=Depends(get_db)
):
    try:
        materials = await db.material.find_many(where={"classroomId": classroom_id})
        if not materials:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No materials found"
            )
        return {"materials": materials}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.put("/material/{material_id}", status_code=status.HTTP_200_OK)
async def update_material(
    material_id: str = Path(..., description="ID of the classroom")
):
    try:
        pass
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/material/{material_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_material(
    material_id: str = Path(..., description="ID of the classroom"),
    teacher=Depends(get_current_teacher),
    db=Depends(get_db),
):
    try:
        await db.material.delete(where={"id": material_id})
        return {"detail": "Material deleted successfully"}
    except RecordNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Material not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# @router.get("/from-chroma", status_code=status.HTTP_200_OK)
# async def get_from_chroma():
#     try:
#         docs = vector_store.similarity_search(
#             query="types of os",  # empty query to fetch all docs matching filter
#             k=2,
#             filter={
#                 "$and": [
#                     {"class_id": "4b838eb5-d8aa-4d9e-9f8b-165fcc499b72"},
#                     {"material_id": "fbfc8e8a-8834-44c4-a88a-b1674bc49ba0"},
#                 ]
#             },
#         )

#         return [
#             {"page_content": doc.page_content, "metadata": doc.metadata} for doc in docs
#         ]
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
#         )
