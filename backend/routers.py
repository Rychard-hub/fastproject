"""
Blog Post Router - Handles blog creation, reading, updating, and deletion
Uses R2Service for file storage with fallback to local uploads
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Path
from pydantic import BaseModel, Field
from typing import List, Optional, Any, cast
import os
import shutil
import asyncio
from concurrent.futures import ThreadPoolExecutor

from models import BlogPost, BlogPost_Pydantic, BlogPostIn_Pydantic
from r2_service import r2_service

router = APIRouter(
    prefix="/blog",
    tags=["blog"],
)

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Thread pool for blocking boto3 operations
executor = ThreadPoolExecutor(max_workers=3)


# ============ Pydantic Models ============

class PresignedUrlResponse(BaseModel):
    """Response containing presigned URL and file path"""
    url: str = Field(..., description="Presigned URL for direct upload to R2")
    file_path: str = Field(..., description="Public URL where file will be accessible")
    expires_in: int = Field(default=3600, description="URL expiration in seconds")


# ============ Helper Functions ============

def save_local_file(file: UploadFile) -> str:
    """Save uploaded file to local storage (sync version for thread pool)"""
    if not file.filename:
        raise ValueError("Filename is missing")
    
    # Ensure uploads directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(cast(Any, file.file), cast(Any, buffer))
    
    return f"/uploads/{file.filename}"


def upload_to_r2(file_data: bytes, filename: str, content_type: str) -> str:
    """Upload file to R2 storage (sync function for thread pool)"""
    if not r2_service.is_configured():
        raise ValueError("R2 storage not configured")
    
    file_url = r2_service.upload_file(file_data, filename, content_type)
    if file_url is None:
        raise RuntimeError(f"Failed to upload {filename} to R2")
    
    return file_url


def generate_presigned_upload_url(filename: str, expiration: int = 3600) -> tuple[str, str]:
    """Generate presigned URL for client-side upload to R2"""
    if not r2_service.is_configured():
        raise ValueError("R2 storage not configured")
    
    url = r2_service.generate_presigned_url(filename, expiration)
    if url is None:
        raise RuntimeError(f"Failed to generate presigned URL for {filename}")
    
    # Construct the public URL where file will be accessible
    if r2_service.public_domain:
        file_path = f"https://{r2_service.public_domain}/{filename}"
    else:
        file_path = f"{r2_service.endpoint_url}/{r2_service.bucket_name}/{filename}"
    
    return url, file_path


# ============ REST Endpoints ============

@router.get("/presigned-url", response_model=PresignedUrlResponse)
async def get_presigned_url(
    filename: str = Query(..., description="Filename for upload"),
    expiration: int = Query(3600, ge=60, le=86400, description="URL expiration in seconds (60-86400)")
):
    """
    Generate a presigned URL for direct file upload to R2
    
    Client can use this URL to upload directly to R2 without going through backend.
    Example:
    ```javascript
    const presignedData = await fetch('/blog/presigned-url?filename=photo.jpg').then(r => r.json());
    await fetch(presignedData.url, {
      method: 'PUT',
      body: fileData,
      headers: {'Content-Type': 'image/jpeg'}
    });
    ```
    """
    try:
        # Run blocking operation in thread pool
        url, file_path = await asyncio.get_event_loop().run_in_executor(
            executor,
            generate_presigned_upload_url,
            filename,
            expiration
        )
        return PresignedUrlResponse(url=url, file_path=file_path, expires_in=expiration)
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating presigned URL: {str(e)}")


@router.post("/", response_model=BlogPost_Pydantic)
async def create_post(
    title: str = Form(..., description="Post title"),
    content: str = Form(..., description="Post content"),
    author: str = Form(..., description="Author name"),
    file: Optional[UploadFile] = File(None, description="Optional image or attachment"),
    file_path_direct: Optional[str] = Form(None, description="Direct file path (from presigned upload)")
):
    """
    Create a new blog post with optional file attachment
    
    Can receive file in two ways:
    1. Direct upload: POST with file in multipart form
    2. Presigned upload: Use presigned URL first, then send file_path_direct
    """
    file_path = file_path_direct
    
    if file:
        # Validate file size
        try:
            file_content = await file.read()
            file_size = len(file_content)
            
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024):.1f}MB"
                )
            
            # Try R2 first, fallback to local storage
            if r2_service.is_configured():
                try:
                    content_type = file.content_type or "application/octet-stream"
                    file_path = await asyncio.get_event_loop().run_in_executor(
                        executor,
                        upload_to_r2,
                        file_content,
                        file.filename,
                        content_type
                    )
                    print(f"Uploaded {file.filename} to R2: {file_path}")
                except Exception as e:
                    print(f"R2 upload failed: {e}, falling back to local storage")
                    # Fallback to local storage
                    await file.seek(0)
                    file_path = await asyncio.get_event_loop().run_in_executor(
                        executor,
                        save_local_file,
                        file
                    )
            else:
                # No R2, use local storage
                await file.seek(0)
                file_path = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    save_local_file,
                    file
                )
        
        except HTTPException:
            raise
        except Exception as e:
            print(f"File processing error: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")
    
    # Create blog post
    try:
        post_obj = await BlogPost.create(
            title=title,
            content=content,
            author=author,
            file_path=file_path
        )
        return await BlogPost_Pydantic.from_tortoise_orm(post_obj)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create post: {str(e)}")


@router.get("/", response_model=List[BlogPost_Pydantic])
async def get_posts(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)):
    """Get all blog posts with pagination"""
    posts = await BlogPost_Pydantic.from_queryset(BlogPost.all().offset(skip).limit(limit))
    return posts


@router.get("/{post_id}", response_model=BlogPost_Pydantic)
async def get_post(post_id: int = Path(..., gt=0)):
    """Get a specific blog post by ID"""
    post = await BlogPost.get_or_none(id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail=f"Blog post {post_id} not found")
    return await BlogPost_Pydantic.from_tortoise_orm(post)


@router.put("/{post_id}", response_model=BlogPost_Pydantic)
async def update_post(
    post_id: int = Path(..., gt=0),
    post: BlogPostIn_Pydantic = None
):
    """Update an existing blog post"""
    # Validate post exists
    existing_post = await BlogPost.get_or_none(id=post_id)
    if existing_post is None:
        raise HTTPException(status_code=404, detail=f"Blog post {post_id} not found")
    
    # Update only provided fields
    try:
        await BlogPost.filter(id=post_id).update(**post.model_dump(exclude_unset=True))
        updated_post = await BlogPost.get(id=post_id)
        return await BlogPost_Pydantic.from_tortoise_orm(updated_post)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update post: {str(e)}")


@router.delete("/{post_id}")
async def delete_post(post_id: int = Path(..., gt=0)):
    """Delete a blog post by ID"""
    existing_post = await BlogPost.get_or_none(id=post_id)
    if existing_post is None:
        raise HTTPException(status_code=404, detail=f"Blog post {post_id} not found")
    
    try:
        await BlogPost.filter(id=post_id).delete()
        return {"message": f"Blog post {post_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete post: {str(e)}")


@router.get("/stats/count")
async def get_post_count():
    """Get total number of blog posts"""
    count = await BlogPost.all().count()
    return {"total_posts": count}
