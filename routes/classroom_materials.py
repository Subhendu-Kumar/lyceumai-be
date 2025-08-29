import cloudinary.uploader
from utils.db_util import get_db
from utils.cloudinary_util import *
from prisma.errors import RecordNotFoundError
from utils.user_util import get_current_teacher
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
        file_res = cloudinary.uploader.upload(
            file.file,
            resource_type="auto",
            folder=f"materials/{classroomId}",
            access_mode="public",
        )
        if not file_res:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="file upload failed",
            )
        print("file_res:   ", file_res)
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
        return {"material": material}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


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
