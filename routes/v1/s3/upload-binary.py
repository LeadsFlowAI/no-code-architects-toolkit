from fastapi import APIRouter, UploadFile, File, Form, Header, HTTPException
from fastapi.responses import JSONResponse
import boto3
import uuid
import os

router = APIRouter()

@router.post("/v1/s3/upload-binary")
async def upload_binary_file(
    file: UploadFile = File(...),
    filename: str = Form(None),
    x_api_key: str = Header(...),
):
    # Auth simple (tu peux améliorer selon ta config)
    if x_api_key != os.getenv("API_KEY", "local-dev-key-123"):
        raise HTTPException(status_code=403, detail="Invalid API key")

    # Préparer Minio/S3
    s3 = boto3.client(
        "s3",
        endpoint_url=os.getenv("S3_ENDPOINT_URL"),
        aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
        region_name=os.getenv("S3_REGION", "us-east-1"),
    )
    bucket = os.getenv("S3_BUCKET_NAME", "media")
    key = filename or f"{uuid.uuid4()}_{file.filename}"

    # Uploader
    s3.upload_fileobj(file.file, bucket, key)

    return JSONResponse({
        "filename": key,
        "bucket": bucket,
        "url": f"{os.getenv('S3_ENDPOINT_URL')}/{bucket}/{key}",
        "public": False
    })
