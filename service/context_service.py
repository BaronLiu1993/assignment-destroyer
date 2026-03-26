import re
from datetime import datetime, timezone
from pathlib import Path

import boto3
from pymongo import MongoClient

from dto.plan_dto import MemorySchema
from service.tools.constants import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_S3_ENDPOINT,
    AWS_SECRET_ACCESS_KEY,
    MONGODB_URI,
)


mongo_client = MongoClient(uri=MONGODB_URI)
database = mongo_client["database"]
memory_collection = database.get_collection("memory")
metadata_collection = database.get_collection("metadata")


def build_s3_client():
    kwargs = {"region_name": AWS_REGION}

    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY

    if AWS_S3_ENDPOINT:
        kwargs["endpoint_url"] = AWS_S3_ENDPOINT

    return boto3.client("s3", **kwargs)


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip()


def parse_uploaded_file_content(file_bytes, filename):
    if not file_bytes:
        return ""

    extension = Path(filename or "").suffix.lower()
    text_extensions = {".txt", ".md", ".csv", ".tsv", ".json", ".py", ".js", ".ts", ".html", ".css"}

    if extension in text_extensions:
        decoded = file_bytes.decode("utf-8", errors="ignore")
        return clean_text(decoded)

    decoded = file_bytes.decode("utf-8", errors="ignore")
    return clean_text(decoded)


def build_sliding_window_chunks(text, window_size=2000, overlap=200):
    if window_size <= 0:
        raise ValueError("window_size must be greater than 0")
    if overlap < 0 or overlap >= window_size:
        raise ValueError("overlap must be >= 0 and < window_size")

    cleaned_text = clean_text(text)
    if not cleaned_text:
        return []

    step = window_size - overlap
    chunks = []
    for start in range(0, len(cleaned_text), step):
        chunk = cleaned_text[start:start + window_size]
        if chunk:
            chunks.append(chunk)
    return chunks


def insert_memory_chunks(user_id, thread_id, role, filename, chunks):
    if not chunks:
        return 0

    timestamp = datetime.now(timezone.utc).isoformat()
    total_chunks = len(chunks)
    documents = []

    for idx, chunk in enumerate(chunks, start=1):
        memory = MemorySchema(
            user_id=user_id,
            thread_id=thread_id,
            role=role,
            content=f"[file: {filename}] [chunk {idx}/{total_chunks}]\n{chunk}",
            timestamp=timestamp,
        )
        documents.append(memory.model_dump())

    memory_collection.insert_many(documents)
    return total_chunks


def get_file_bytes_from_s3(bucket, object_key):
    s3_client = build_s3_client()
    response = s3_client.get_object(Bucket=bucket, Key=object_key)
    return response["Body"].read()


def process_file_from_s3_to_memory(
    user_id,
    thread_id,
    bucket,
    object_key,
    filename,
    role="context",
    window_size=2000,
    overlap=200,
):
    file_bytes = get_file_bytes_from_s3(bucket=bucket, object_key=object_key)
    parsed_text = parse_uploaded_file_content(file_bytes=file_bytes, filename=filename)
    chunks = build_sliding_window_chunks(parsed_text, window_size=window_size, overlap=overlap)

    chunks_inserted = insert_memory_chunks(
        user_id=user_id,
        thread_id=thread_id,
        role=role,
        filename=filename,
        chunks=chunks,
    )

    return {
        "status": "processed" if chunks_inserted > 0 else "empty",
        "bucket": bucket,
        "object_key": object_key,
        "chunks_inserted": chunks_inserted,
        "window_size": window_size,
        "overlap": overlap,
    }


def save_file_metadata_to_mongo(file_metadata):
    return metadata_collection.insert_one(file_metadata)