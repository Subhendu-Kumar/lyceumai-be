from fastapi import APIRouter, HTTPException, Depends, status

router = APIRouter(prefix="/class", tags=["Classroom Materials"])


@router.post("/materials", status_code=status.HTTP_201_CREATED)
async def create_material():
    try:
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/materials", status_code=status.HTTP_200_OK)
async def get_materials():
    try:
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/materials/{material_id}", status_code=status.HTTP_200_OK)
async def update_material(material_id: str):
    try:
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/materials/{material_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_material(material_id: str):
    try:
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
