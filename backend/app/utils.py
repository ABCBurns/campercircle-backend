import time
import boto3
import os
from botocore.exceptions import ClientError

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "camper-profile-pics")

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    region_name="us-east-1",
)


def ensure_bucket(retries=10, delay=5):
    """Ensure the bucket exists, retrying until MinIO is ready."""
    for attempt in range(retries):
        try:
            s3_client.head_bucket(Bucket=MINIO_BUCKET)
            print(f"Bucket {MINIO_BUCKET} exists")
            return
        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code in ["404", "NoSuchBucket"]:
                print(f"Bucket {MINIO_BUCKET} not found, creating...")
                s3_client.create_bucket(Bucket=MINIO_BUCKET)
                return
            elif code in ["403", "Forbidden"]:
                print("⏳ MinIO not accepting credentials yet, retrying...")
            else:
                print(f"⚠️ Unexpected error: {e}")
        except Exception as e:
            print("MinIO not ready, retrying...", e)
        time.sleep(delay)

    raise Exception(
        f"Could not ensure MinIO bucket {MINIO_BUCKET} after {retries} attempts."
    )
