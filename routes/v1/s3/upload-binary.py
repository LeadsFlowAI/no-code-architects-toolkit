from flask import Blueprint, request, jsonify
from services.authentication import authenticate
from app_utils import queue_task_wrapper
import boto3
import os
import uuid
import logging

logger = logging.getLogger(__name__)
v1_s3_upload_binary_bp = Blueprint('v1_s3_upload_binary', __name__)

@v1_s3_upload_binary_bp.route('/v1/s3/upload-binary', methods=['POST'])
@authenticate
@queue_task_wrapper(bypass_queue=True)
def s3_upload_binary(job_id, data):
    try:
        if 'file' not in request.files:
            return {"error": "Missing file in form-data"}, "/v1/s3/upload-binary", 400

        uploaded_file = request.files['file']
        filename = request.form.get('filename', uploaded_file.filename)
        make_public = request.form.get('public', 'false').lower() == 'true'

        s3 = boto3.client(
            "s3",
            endpoint_url=os.getenv("S3_ENDPOINT_URL"),
            aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
            region_name=os.getenv("S3_REGION", "us-east-1"),
        )

        bucket = os.getenv("S3_BUCKET_NAME", "media")
        key = f"{uuid.uuid4()}_{filename}"

        s3.upload_fileobj(uploaded_file, bucket, key)

        url = f"{os.getenv('S3_ENDPOINT_URL')}/{bucket}/{key}"

        return {
            "filename": key,
            "bucket": bucket,
            "url": url,
            "public": make_public
        }, "/v1/s3/upload-binary", 200

    except Exception as e:
        logger.error(f"Job {job_id} - Upload error: {str(e)}")
        return {"error": str(e)}, "/v1/s3/upload-binary", 500
