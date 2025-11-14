import boto3
import os
from botocore.exceptions import NoCredentialsError
import json
import io
from typing import Dict, Any, List, Optional, Tuple

from dotenv import load_dotenv
load_dotenv()


# --- AWS Configuration ---
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
REGION_NAME = os.getenv("REGION_NAME")

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=os.getenv("REGION_NAME")
    )

def upload_file_to_s3_folder(local_file_path, s3_key, bucket_name=BUCKET_NAME):
    s3 = get_s3_client()
    try:
        s3.upload_file(local_file_path, bucket_name, s3_key)
        return f"s3://{bucket_name}/{s3_key}"
    except NoCredentialsError:
        raise RuntimeError("❌ AWS credentials not found.")

def upload_json_to_s3_folder(data, s3_key, bucket_name=BUCKET_NAME):
    json_str = data
    s3 = get_s3_client()
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json_str,
            ContentType='application/json'
        )
        return f"s3://{bucket_name}/{s3_key}"
    except NoCredentialsError:
        raise RuntimeError("❌ AWS credentials not found.")
    
def list_s3_json_files(prefix: str):
    """List all JSON files in a given S3 prefix."""
    s3 = get_s3_client()
    resp = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
    return [item['Key'] for item in resp.get('Contents', []) if item['Key'].endswith('.json')]

def read_s3_json(key: str) -> Dict[str, Any]:
    """Read JSON file from S3."""
    s3 = get_s3_client()
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
    return json.load(io.BytesIO(obj['Body'].read()))

    
def upload_dataframe_to_s3_folder(df, folder_prefix, filename, content_type="text/csv"):
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    s3 = get_s3_client()
    key = f"{folder_prefix}/{filename}"
    try:
        s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=csv_buffer.getvalue(), ContentType=content_type)
        return f"s3://{BUCKET_NAME}/{key}"
    except NoCredentialsError:
        raise RuntimeError("❌ AWS credentials not found.")
    

