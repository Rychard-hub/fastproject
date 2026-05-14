# Cloudflare R2 + E-Shop Integration Guide

## Overview

Your e-shop is fully integrated with **Cloudflare R2** for banner and product image storage. All images are uploaded directly to R2 and served via the public domain, providing fast, global CDN delivery.

## Current Configuration

```
✅ Connected: Yes
✅ Bucket: imagecloud
✅ Endpoint: https://fac9f5b02fe578321a3d57afe9935855.r2.cloudflarestorage.com
✅ Public Domain: fac9f5b02fe578321a3d57afe9935855.r2.dev
✅ Stripe Integration: Enabled
```

## API Endpoints

### 1. Check R2 Connection Status
```bash
GET /shop/r2/status
```

**Response:**
```json
{
    "status": "connected",
    "bucket": "imagecloud",
    "endpoint": "https://...",
    "public_domain": "..."
}
```

### 2. Upload Banner Image
Upload a hero banner for your shop (recommended: 1200x400px)

```bash
POST /shop/banners/upload
Content-Type: multipart/form-data

file: <image_file>
```

**Example:**
```bash
curl -X POST \
  -F "file=@banner.jpg" \
  http://localhost:8000/shop/banners/upload
```

**Response:**
```json
{
    "banner_url": "https://fac9f5b02fe578321a3d57afe9935855.r2.dev/shop/banners/banner.jpg",
    "file_size": 245000
}
```

**Use the `banner_url` to:**
- Display in shop header
- Set as hero image
- Use in email campaigns
- Share on social media

### 3. Upload Product Image
Upload images for individual products

```bash
POST /shop/products/upload-image
Content-Type: multipart/form-data

file: <image_file>
```

**Example:**
```bash
curl -X POST \
  -F "file=@camera.jpg" \
  http://localhost:8000/shop/products/upload-image
```

**Response:**
```json
{
    "image_url": "https://fac9f5b02fe578321a3d57afe9935855.r2.dev/shop/products/camera.jpg",
    "file_size": 128000
}
```

### 4. List Shop Files in R2
View all uploaded banners and product images

```bash
GET /shop/r2/files?prefix=shop/
```

**Response:**
```json
{
    "prefix": "shop/",
    "files_count": 2,
    "files": [
        {
            "key": "shop/banners/banner.jpg",
            "size": 245000,
            "url": "https://fac9f5b02fe578321a3d57afe9935855.r2.dev/shop/banners/banner.jpg",
            "last_modified": "2026-05-07T16:30:00Z"
        },
        {
            "key": "shop/products/camera.jpg",
            "size": 128000,
            "url": "https://fac9f5b02fe578321a3d57afe9935855.r2.dev/shop/products/camera.jpg",
            "last_modified": "2026-05-07T16:25:00Z"
        }
    ]
}
```

### 5. Get Shop Statistics
```bash
GET /shop/stats
```

**Response:**
```json
{
    "products": 6,
    "r2_connected": true,
    "stripe_connected": true,
    "bucket": "imagecloud"
}
```

## Usage Examples

### Upload Banner Photo (JavaScript/React)

```javascript
async function uploadBanner() {
  const fileInput = document.getElementById('bannerUpload');
  const file = fileInput.files[0];
  
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('/shop/banners/upload', {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // Use the banner URL
    document.getElementById('heroImage').src = data.banner_url;
    console.log('Banner uploaded:', data.banner_url);
  } else {
    console.error('Upload failed:', data.detail);
  }
}
```

### Upload Product Image (Python)

```python
import requests

def upload_product_image(image_path):
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            'http://localhost:8000/shop/products/upload-image',
            files=files
        )
    
    return response.json()

# Usage
result = upload_product_image('camera.jpg')
print(f"Image URL: {result['image_url']}")
print(f"File size: {result['file_size']} bytes")
```

### Upload via cURL

```bash
# Upload banner
curl -X POST \
  -F "file=@banner.jpg" \
  http://localhost:8000/shop/banners/upload

# Upload product image
curl -X POST \
  -F "file=@product.jpg" \
  http://localhost:8000/shop/products/upload-image

# List all shop files
curl http://localhost:8000/shop/r2/files

# Check R2 status
curl http://localhost:8000/shop/r2/status
```

## URL Structure in R2

All uploaded files are organized in the `imagecloud` bucket:

```
imagecloud/
├── shop/
│   ├── banners/
│   │   ├── banner.jpg
│   │   └── summer_sale.png
│   ├── products/
│   │   ├── camera.jpg
│   │   ├── lens.jpg
│   │   └── tripod.jpg
│   └── blog/
│       └── post1.jpg
```

**Public URLs:**
- Banner: `https://fac9f5b02fe578321a3d57afe9935855.r2.dev/shop/banners/banner.jpg`
- Product: `https://fac9f5b02fe578321a3d57afe9935855.r2.dev/shop/products/camera.jpg`

## Image Specifications

### Banner Images
- **Recommended Size:** 1200x400 pixels
- **Max File Size:** 10 MB
- **Format:** JPG, PNG, WebP
- **Aspect Ratio:** 3:1

### Product Images
- **Recommended Size:** 500x500 pixels (square)
- **Max File Size:** 10 MB
- **Format:** JPG, PNG, WebP
- **Aspect Ratio:** 1:1

## Integration with Shop Frontend

### React Example

```jsx
import React, { useState } from 'react';

function ShopBanner() {
  const [banner, setBanner] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleBannerUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/shop/banners/upload', {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        const data = await response.json();
        setBanner(data.banner_url);
      } else {
        const error = await response.json();
        alert(`Upload failed: ${error.detail}`);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept="image/*"
        onChange={handleBannerUpload}
        disabled={loading}
      />
      {banner && (
        <img
          src={banner}
          alt="Shop Banner"
          style={{ width: '100%', maxHeight: '400px' }}
        />
      )}
    </div>
  );
}

export default ShopBanner;
```

## Limits & Constraints

| Property | Limit |
|----------|-------|
| Max file size | 10 MB |
| Max files per upload | 1 |
| Supported formats | JPG, PNG, WebP, GIF |
| Concurrent uploads | 2 (thread pool size) |
| File retention | Permanent (until manually deleted) |
| CDN cache | 1 hour default |

## Pricing

Cloudflare R2 charges:
- **Storage:** $0.015 per GB per month
- **Class A operations:** $0.36 per million
- **Class B operations:** $0.0036 per million
- **Egress:** $0.02 per GB (first 100GB free/month)

## Troubleshooting

### 403 Forbidden Error
```json
{"status": "connected", "message": "R2 storage not configured"}
```
**Solution:** Check `.env` file has all R2 credentials:
- R2_BUCKET_NAME
- R2_ACCOUNT_ID
- R2_ACCESS_KEY_ID
- R2_SECRET_ACCESS_KEY

### File Size Exceeded
```json
{"detail": "File too large. Maximum size is 10.0MB"}
```
**Solution:** Resize image before uploading. Use tools like ImageMagick:
```bash
convert banner.jpg -resize 1200x400 banner_resized.jpg
```

### Slow Upload
- Compress image before uploading
- Use PNG for graphics, JPG for photos
- Check internet connection speed
- Verify R2 bucket is in correct region

## Direct R2 Access

Access files directly via:
```
https://fac9f5b02fe578321a3d57afe9935855.r2.dev/path/to/file
```

No authentication required for public files.

## Security

All uploads are:
- ✅ Scanned for file type (multipart/form-data validation)
- ✅ Size-limited (10MB max)
- ✅ Organized in shop folder (prevents conflicts)
- ✅ Publicly accessible (no DRM/encryption)
- ✅ Cached globally via CDN

## Next Steps

1. Upload a banner for your shop hero section
2. Upload product images for e-commerce display
3. Configure Stripe with real Price IDs
4. Test the complete checkout flow
5. Monitor R2 storage usage in Cloudflare dashboard

## Useful Commands

```bash
# Check R2 connection
curl http://localhost:8000/shop/r2/status

# List all shop files
curl http://localhost:8000/shop/r2/files

# Get shop statistics
curl http://localhost:8000/shop/stats

# Upload banner (form-data)
curl -F "file=@banner.jpg" http://localhost:8000/shop/banners/upload

# Upload product (form-data)
curl -F "file=@product.jpg" http://localhost:8000/shop/products/upload-image
```

## Support

For R2 issues, check:
- [Cloudflare R2 Docs](https://developers.cloudflare.com/r2/)
- [R2 API Reference](https://developers.cloudflare.com/r2/api/s3/)
- Bucket policy settings in Cloudflare dashboard
- Authentication credentials in `.env`
