"""
Blog Post Router - Handles blog creation, reading, updating, and deletion
Uses R2Service for file storage with fallback to local uploads
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Path
from pydantic import BaseModel, Field
from typing import List, Optional, Any, cast
import os
import shutil
import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor

from models import BlogPost, BlogPost_Pydantic, BlogPostIn_Pydantic, Benefit, Routine, ProTip, Benefit_Pydantic, Routine_Pydantic, ProTip_Pydantic
from r2_service import r2_service
from auth import require_admin

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

    # Use only the basename and prefix with a UUID so a filename like
    # "../../etc/passwd" can't escape UPLOAD_DIR and same-name uploads
    # can't overwrite each other.
    safe_name = os.path.basename(file.filename)
    unique_name = f"{uuid.uuid4()}_{safe_name}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(cast(Any, file.file), cast(Any, buffer))

    return f"/uploads/{unique_name}"


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

@router.get("/presigned-url", response_model=PresignedUrlResponse, dependencies=[Depends(require_admin)])
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


@router.post("/", response_model=BlogPost_Pydantic, dependencies=[Depends(require_admin)])
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


@router.put("/{post_id}", response_model=BlogPost_Pydantic, dependencies=[Depends(require_admin)])
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


@router.delete("/{post_id}", dependencies=[Depends(require_admin)])
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

@router.get("/face-exercises/data")
async def get_face_exercise_data():
    """Get all face exercise data: benefits, routines, and pro tips"""
    benefits = await Benefit.all()
    routines = await Routine.all()
    tips = await ProTip.all()
    
    # If database is empty, we can return the initial data or empty lists
    return {
        "benefits": [await Benefit_Pydantic.from_tortoise_orm(b) for b in benefits],
        "routines": [await Routine_Pydantic.from_tortoise_orm(r) for r in routines],
        "proTips": [await ProTip_Pydantic.from_tortoise_orm(t) for t in tips]
    }

@router.post("/face-exercises/seed")
async def seed_face_exercise_data():
    """Seed the database with initial face exercise data if empty"""
    if await Benefit.all().count() == 0:
        benefits_data = [
            {"title": "Improved Circulation", "description": "Facial exercises increase blood flow to skin cells, delivering oxygen and nutrients that give you a natural, healthy glow."},
            {"title": "Reduced Wrinkles", "description": "Strengthening facial muscles from underneath plumps the skin, smoothing fine lines and preventing new ones from forming."},
            {"title": "Better Muscle Tone", "description": "Just like body workouts, regular face yoga tones and lifts the 57 muscles in your face and neck for a naturally youthful look."},
            {"title": "Stress Relief", "description": "Mindful facial movements release jaw tension, relax tight muscles, and activate the parasympathetic nervous system to calm your mind."}
        ]
        for b in benefits_data:
            await Benefit.create(**b)

    if await Routine.all().count() == 0:
        routines_data = [
            {
                "icon": "🦁", "level": "Beginner", "title": "The Lion's Yawn", "target": "Jaw & Neck",
                "steps": ["Sit comfortably and inhale deeply through your nose.", "Open your mouth as wide as possible, stick your tongue out and down.", "Roll your eyes upward and hold the stretch.", "Exhale with a 'haaa' sound and relax."],
                "timing": "Hold 10 sec, repeat 5×"
            },
            {
                "icon": "🍎", "level": "Beginner", "title": "Cheek Sculptor", "target": "Cheeks",
                "steps": ["Puff your cheeks full of air.", "Transfer the air from one cheek to the other slowly.", "Hold the air in each cheek for 3 seconds.", "Release and repeat 10 times."],
                "timing": "30 sec each side"
            },
            {
                "icon": "✨", "level": "Beginner", "title": "Brow Smoother", "target": "Forehead",
                "steps": ["Place your fingertips on your forehead, spanning from brow to hairline.", "Gently press down while trying to raise your eyebrows.", "Hold the tension for 3 seconds.", "Relax and repeat."],
                "timing": "Repeat 10×"
            },
            {
                "icon": "😮", "level": "Intermediate", "title": "Jaw Release", "target": "Jawline",
                "steps": ["Sit straight and move your jaw as if chewing while keeping your lips closed.", "Hum as you do this, then open your mouth wide.", "Press your tongue against your lower teeth.", "Hold 5 seconds, close and repeat 10 times."],
                "timing": "2 min daily"
            },
            {
                "icon": "👁️", "level": "Beginner", "title": "Eye Opener", "target": "Eyes",
                "steps": ["Make a large 'O' shape with your mouth to open your face.", "Raise your eyebrows as high as you can.", "Hold and stare at a point in the distance.", "Relax and repeat without moving your forehead."],
                "timing": "Hold 5 sec, repeat 10×"
            },
            {
                "icon": "🐟", "level": "Beginner", "title": "Fish Lips", "target": "Cheeks",
                "steps": ["Suck in your cheeks and lips to make a 'fish face'.", "Try to smile while holding the position.", "Hold for 5 seconds and feel the burn.", "Relax completely and repeat."],
                "timing": "Hold 5 sec, repeat 10×"
            },
            {
                "icon": "🦢", "level": "Intermediate", "title": "Neck Toner", "target": "Neck",
                "steps": ["Sit or stand straight with shoulders back.", "Tilt your head back and look at the ceiling.", "Press your tongue firmly to the roof of your mouth.", "Swallow and hold — feel the neck muscles engage."],
                "timing": "Hold 10 sec, repeat 5×"
            },
            {
                "icon": "🌊", "level": "Intermediate", "title": "Forehead Smoother", "target": "Forehead",
                "steps": ["Place both palms flat against your forehead.", "Apply gentle outward pressure as you raise your brows.", "Slide your hands gently toward your temples.", "Hold 2 seconds at the temples and release."],
                "timing": "Repeat 15× daily"
            }
        ]
        for r in routines_data:
            await Routine.create(**r)

    if await ProTip.all().count() == 0:
        tips_data = [
            {"title": "Start with Clean Hands", "content": "Always wash your hands thoroughly before touching your face to prevent transferring bacteria and causing breakouts."},
            {"title": "Use a Mirror", "content": "Practicing in front of a mirror ensures proper form and helps you target the correct muscle groups for maximum benefit."},
            {"title": "Consistency Is Key", "content": "Aim for 10–20 minutes daily. Like any fitness routine, results come from regular, dedicated practice over weeks and months."},
            {"title": "Pair with Facial Massage", "content": "After your routine, massage your face with a few drops of facial oil using upward strokes to boost circulation and lymphatic drainage."}
        ]
        for t in tips_data:
            await ProTip.create(**t)
            
    return {"message": "Data seeded successfully"}
