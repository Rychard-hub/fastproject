import boto3

s3 = boto3.client(
    service_name='s3',
    # Provide your R2 endpoint: https://<ACCOUNT_ID>.r2.cloudflarestorage.com
    endpoint_url='https://<ACCOUNT_ID>.eu.r2.cloudflarestorage.com',
    # Provide your R2 Access Key ID and Secret Access Key
    aws_access_key_id='<ACCESS_KEY_ID>',
    aws_secret_access_key='<SECRET_ACCESS_KEY>',
    region_name='auto',  # Required by boto3, not used by R2
)

# Upload a file
s3.upload_file('myfile.txt', 'my-bucket', 'myfile.txt')
print('Uploaded myfile.txt')

# Download a file
s3.download_file('my-bucket', 'myfile.txt', 'downloaded.txt')
print('Downloaded to downloaded.txt')

# List objects
response = s3.list_objects_v2(Bucket='my-bucket')
for obj in response.get('Contents', []):
    print(f"Object: {obj['Key']}")