import io
from uuid import uuid4

from minio import Minio

from src.config import settings


def get_minio_client() -> Minio:
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=False,
    )


def upload_file_to_minio(file_data: bytes, filename: str, content_type: str) -> str:
    client = get_minio_client()

    bucket = settings.MINIO_BUCKET_NAME
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)

    unique_filename = f"{uuid4()}_{filename}"
    client.put_object(
        bucket,
        unique_filename,
        data=io.BytesIO(file_data),
        length=len(file_data),
        content_type=content_type,
    )

    return f"http://{settings.MINIO_ENDPOINT}/{bucket}/{unique_filename}"
