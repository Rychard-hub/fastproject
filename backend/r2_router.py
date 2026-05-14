from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from typing import Optional
from r2_service import r2_service
import uuid

router = APIRouter(
    prefix="/r2",
    tags=["r2"],
)

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Query("uploads"),
    custom_key: Optional[str] = Query(None)
):
    if not r2_service.is_configured():
        raise HTTPException(status_code=500, detail="R2 service not configured")
    
    file_content = await file.read()
    
    if custom_key:
        object_key = custom_key
    else:
        file_extension = file.filename.split(".")[-1] if "." in file.filename else ""
        object_key = f"{folder}/{uuid.uuid4()}{'.' + file_extension if file_extension else ''}"
    
    url = r2_service.upload_file(file_content, object_key, file.content_type)
    if not url:
        raise HTTPException(status_code=500, detail="Failed to upload file to R2")
    
    # Generate a signed URL for immediate use
    signed_url = r2_service.generate_signed_url(object_key)
    
    return {
        "url": signed_url or url,
        "object_key": object_key
    }

@router.get("/url")
async def get_signed_url(
    object_key: str = Query(..., description="The key of the object in R2")
):
    if not r2_service.is_configured():
        raise HTTPException(status_code=500, detail="R2 service not configured")
    
    url = r2_service.generate_signed_url(object_key)
    if not url:
        raise HTTPException(status_code=404, detail="Could not generate signed URL")
    
    return {"url": url}

@router.delete("/delete")
async def delete_file(
    object_key: str = Query(..., description="The key of the object in R2")
):
    if not r2_service.is_configured():
        raise HTTPException(status_code=500, detail="R2 service not configured")
    
    success = r2_service.delete_file(object_key)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete file from R2")
    
    return {"message": "File deleted successfully"}
