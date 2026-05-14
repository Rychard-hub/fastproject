"""
R2 Storage Service using boto3
Handles all Cloudflare R2 operations for file uploads, downloads, and catalog management
"""
import os
import boto3
from typing import Optional, List, Dict, Any
from botocore.exceptions import ClientError
from datetime import timedelta

class R2Service:
    def __init__(self):
        self.bucket_name = os.getenv("R2_BUCKET_NAME")
        self.account_id = os.getenv("R2_ACCOUNT_ID")
        self.access_key_id = os.getenv("R2_ACCESS_KEY_ID")
        self.secret_access_key = os.getenv("R2_SECRET_ACCESS_KEY")
        self.public_domain = os.getenv("R2_PUBLIC_DOMAIN")
        self.endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com" if self.account_id else None
        
        self.s3_client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize boto3 S3 client for R2"""
        if not all([self.bucket_name, self.access_key_id, self.secret_access_key, self.endpoint_url]):
            return
        
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                region_name='us-east-1'
            )
        except Exception as e:
            print(f"Failed to initialize R2 client: {e}")
    
    def is_configured(self) -> bool:
        """Check if R2 is properly configured"""
        return self.s3_client is not None
    
    def upload_file(self, file_data: bytes, file_key: str, content_type: str = "application/octet-stream") -> Optional[str]:
        """Upload a file to R2"""
        if not self.is_configured():
            return None
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_data,
                ContentType=content_type
            )
            return self._get_file_url(file_key)
        except ClientError as e:
            print(f"Error uploading file to R2: {e}")
            return None
    
    def upload_fileobj(self, file_obj, file_key: str, content_type: str = "application/octet-stream") -> Optional[str]:
        """Upload a file object to R2"""
        if not self.is_configured():
            return None
        
        try:
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                file_key,
                ExtraArgs={'ContentType': content_type}
            )
            return self._get_file_url(file_key)
        except ClientError as e:
            print(f"Error uploading file object to R2: {e}")
            return None
    
    def download_file(self, file_key: str) -> Optional[bytes]:
        """Download a file from R2"""
        if not self.is_configured():
            return None
        
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            return response['Body'].read()
        except ClientError as e:
            print(f"Error downloading file from R2: {e}")
            return None
    
    def delete_file(self, file_key: str) -> bool:
        """Delete a file from R2"""
        if not self.is_configured():
            return False
        
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            return True
        except ClientError as e:
            print(f"Error deleting file from R2: {e}")
            return False
    
    def list_files(self, prefix: str = "", max_keys: int = 1000) -> List[Dict[str, Any]]:
        """List files in R2 with optional prefix"""
        if not self.is_configured():
            return []
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'url': self._get_file_url(obj['Key'])
                })
            return files
        except ClientError as e:
            print(f"Error listing files in R2: {e}")
            return []
    
    def generate_signed_url(self, object_key: str, expires_minutes: int = 60) -> Optional[str]:
        """Generate a presigned GET URL for temporary file access"""
        if not self.is_configured():
            return None
            
        try:
            url = self.s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket_name, "Key": object_key},
                ExpiresIn=expires_minutes * 60
            )
            return url
        except ClientError as e:
            print("Signed URL error:", e)
            return None

    def generate_presigned_url(self, file_key: str, expiration: int = 3600) -> Optional[str]:
        """Generate a presigned URL for temporary file access"""
        if not self.is_configured():
            return None
        
        try:
            url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    def _get_file_url(self, file_key: str) -> str:
        """Get the public URL for a file"""
        if self.public_domain:
            return f"https://{self.public_domain}/{file_key}"
        else:
            return f"{self.endpoint_url}/{self.bucket_name}/{file_key}"
    
    def create_bucket_if_not_exists(self) -> bool:
        """Create R2 bucket if it doesn't exist"""
        if not self.is_configured():
            return False
        
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"Bucket {self.bucket_name} already exists")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    print(f"Created bucket {self.bucket_name}")
                    return True
                except ClientError as e:
                    print(f"Error creating bucket: {e}")
                    return False
            else:
                print(f"Error checking bucket: {e}")
                return False


# Global R2 service instance
r2_service = R2Service()
