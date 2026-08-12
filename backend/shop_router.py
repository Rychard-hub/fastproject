"""
Shop Router - E-commerce endpoints with Stripe integration and R2 image uploads
"""
import stripe
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from models import Product, Product_Pydantic
from r2_service import r2_service
from auth import require_admin

load_dotenv = __import__('dotenv').load_dotenv
load_dotenv()

stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
if stripe_secret_key:
    stripe.api_key = stripe_secret_key

# Thread pool for R2 uploads
executor = ThreadPoolExecutor(max_workers=2)

router = APIRouter(
    prefix="/shop",
    tags=["shop"],
)

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB for product/banner images


# ============ Pydantic Models ============

class CreateCheckoutSessionRequest(BaseModel):
    price_id: str = Field(..., description="Stripe Price ID")

class ProductUploadResponse(BaseModel):
    image_url: str = Field(..., description="Public URL of uploaded image in R2")
    file_size: int = Field(..., description="Size of uploaded file in bytes")

class BannerUploadResponse(BaseModel):
    banner_url: str = Field(..., description="Public URL of banner in R2")
    file_size: int = Field(..., description="Size in bytes")


# ============ Helper Functions ============

def upload_product_image(file_data: bytes, filename: str) -> str:
    """Upload product image to R2 (sync for thread pool)"""
    if not r2_service.is_configured():
        raise ValueError("R2 storage not configured")
    
    # Store in products folder
    r2_path = f"shop/products/{filename}"
    url = r2_service.upload_file(file_data, r2_path, "image/jpeg")
    
    if url is None:
        raise RuntimeError(f"Failed to upload product image {filename}")
    
    return url

def upload_banner_image(file_data: bytes, filename: str) -> str:
    """Upload banner image to R2 (sync for thread pool)"""
    if not r2_service.is_configured():
        raise ValueError("R2 storage not configured")
    
    # Store in banners folder
    r2_path = f"shop/banners/{filename}"
    url = r2_service.upload_file(file_data, r2_path, "image/png")
    
    if url is None:
        raise RuntimeError(f"Failed to upload banner {filename}")
    
    return url


# ============ REST Endpoints ============

@router.get("/products", response_model=List[Product_Pydantic])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """Get all shop products with pagination"""
    products = await Product_Pydantic.from_queryset(
        Product.all().offset(skip).limit(limit)
    )
    return products


@router.post("/products/upload-image", response_model=ProductUploadResponse, dependencies=[Depends(require_admin)])
async def upload_product_image_endpoint(file: UploadFile = File(...)):
    """
    Upload a product image directly to R2
    
    Returns the public URL where the image can be accessed
    """
    if not r2_service.is_configured():
        raise HTTPException(status_code=503, detail="R2 storage not configured")
    
    try:
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_IMAGE_SIZE / (1024 * 1024):.1f}MB"
            )
        
        # Upload to R2
        image_url = await asyncio.get_event_loop().run_in_executor(
            executor,
            upload_product_image,
            file_content,
            file.filename
        )
        
        return ProductUploadResponse(image_url=image_url, file_size=file_size)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")


@router.post("/banners/upload", response_model=BannerUploadResponse, dependencies=[Depends(require_admin)])
async def upload_banner(file: UploadFile = File(...)):
    """
    Upload a shop banner image to R2
    
    Use this for hero banners, promotional images, etc.
    Returns the public URL for the banner
    """
    if not r2_service.is_configured():
        raise HTTPException(status_code=503, detail="R2 storage not configured")
    
    try:
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Banner too large. Maximum size is {MAX_IMAGE_SIZE / (1024 * 1024):.1f}MB"
            )
        
        # Upload to R2
        banner_url = await asyncio.get_event_loop().run_in_executor(
            executor,
            upload_banner_image,
            file_content,
            file.filename
        )
        
        return BannerUploadResponse(banner_url=banner_url, file_size=file_size)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload banner: {str(e)}")


@router.get("/r2/status")
async def get_r2_status():
    """Check R2 connection status"""
    if r2_service.is_configured():
        return {
            "status": "connected",
            "bucket": r2_service.bucket_name,
            "endpoint": r2_service.endpoint_url,
            "public_domain": r2_service.public_domain or "Using default domain"
        }
    else:
        return {
            "status": "disconnected",
            "message": "R2 storage not configured"
        }


@router.get("/r2/files", dependencies=[Depends(require_admin)])
async def list_r2_files(prefix: str = Query("shop/", description="Folder prefix")):
    """List files in R2 storage"""
    if not r2_service.is_configured():
        raise HTTPException(status_code=503, detail="R2 storage not configured")
    
    try:
        files = r2_service.list_files(prefix=prefix, max_keys=50)
        return {
            "prefix": prefix,
            "files_count": len(files),
            "files": [
                {
                    "key": f["key"],
                    "size": f["size"],
                    "url": f["url"],
                    "last_modified": f["last_modified"]
                }
                for f in files
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")


@router.post("/create-checkout-session")
async def create_checkout_session(item: CreateCheckoutSessionRequest):
    """
    Create a Stripe checkout session for purchasing
    
    Requires valid Stripe Price ID
    """
    if not stripe_secret_key:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    
    if not item.price_id or not item.price_id.startswith("price_"):
        raise HTTPException(
            status_code=400,
            detail="Invalid price ID. Must be a valid Stripe Price ID (e.g., price_xxx)"
        )
    
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': item.price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=os.getenv("STRIPE_SUCCESS_URL", "http://localhost/?success=true"),
            cancel_url=os.getenv("STRIPE_CANCEL_URL", "http://localhost/?canceled=true"),
        )
        return {"url": checkout_session.url}
    except stripe.error.InvalidRequestError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Stripe request: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stripe error: {str(e)}")


@router.get("/seed-products", dependencies=[Depends(require_admin)])
async def seed_products():
    """
    Create sample products for the shop
    
    Note: Replace stripe_price_id values with actual Stripe Price IDs
    """
    count = await Product.all().count()
    if count == 0:
        products = [
            {
                "name": "Professional DSLR Camera",
                "description": "Capture stunning photos with this high-end digital camera.",
                "price": 899.00,
                "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=500&auto=format&fit=crop&q=60",
                "stripe_price_id": "price_camera_001"
            },
            {
                "name": "Vintage Leather Camera Bag",
                "description": "Stylish and durable protection for your photography gear.",
                "price": 75.00,
                "image_url": "https://images.unsplash.com/photo-1524143899222-3837905146c3?w=500&auto=format&fit=crop&q=60",
                "stripe_price_id": "price_bag_002"
            },
            {
                "name": "Carbon Fiber Tripod",
                "description": "Lightweight and stable support for long exposure shots.",
                "price": 120.00,
                "image_url": "https://images.unsplash.com/photo-1581591524425-c7e0978865fc?w=500&auto=format&fit=crop&q=60",
                "stripe_price_id": "price_tripod_003"
            },
            {
                "name": "50mm f/1.8 Prime Lens",
                "description": "The perfect 'nifty fifty' for beautiful portraits and bokeh.",
                "price": 199.00,
                "image_url": "https://images.unsplash.com/photo-1617005082133-548c4dd27f35?w=500&auto=format&fit=crop&q=60",
                "stripe_price_id": "price_lens_004"
            },
            {
                "name": "Portable Studio Lighting Kit",
                "description": "Everything you need for professional lighting on the go.",
                "price": 250.00,
                "image_url": "https://images.unsplash.com/photo-1520390138845-fd2d229dd553?w=500&auto=format&fit=crop&q=60",
                "stripe_price_id": "price_lighting_005"
            },
            {
                "name": "External Speedlite Flash",
                "description": "Powerful flash for indoor and low-light photography.",
                "price": 145.00,
                "image_url": "https://images.unsplash.com/photo-1542038784456-1ea8e935640e?w=500&auto=format&fit=crop&q=60",
                "stripe_price_id": "price_flash_006"
            }
        ]
        
        for p in products:
            await Product.create(**p)
        
        return {
            "message": f"{len(products)} products seeded successfully!",
            "note": "Remember to update stripe_price_id values with real Stripe Price IDs for production"
        }
    
    return {"message": f"Shop already has {count} products"}


@router.get("/stats")
async def get_shop_stats():
    """Get shop statistics"""
    product_count = await Product.all().count()
    r2_connected = r2_service.is_configured()
    stripe_connected = bool(stripe_secret_key)
    
    return {
        "products": product_count,
        "r2_connected": r2_connected,
        "stripe_connected": stripe_connected,
        "bucket": r2_service.bucket_name if r2_connected else None
    }
