import re
from datetime import datetime, timezone
from pathlib import Path

import anthropic
from pymongo import MongoClient
from service.utils.constants import ANTHROPIC_API_KEY, MONGODB_URI
from dto.plan.agent_dto import MemorySchema

# Initialize the Anthropic and Mongo Client
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
mongo_client = MongoClient(uri=MONGODB_URI)
database = mongo_client["database"]
memory_collection = database.get_collection("memory")


def _clean_text(text):
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
    if extension in {".txt", ".md", ".csv", ".tsv", ".json", ".py", ".js", ".ts", ".html", ".css"}:
        decoded = file_bytes.decode("utf-8", errors="ignore")
        return _clean_text(decoded)

    decoded = file_bytes.decode("utf-8", errors="ignore")
    return _clean_text(decoded)


def build_sliding_window_chunks(text, window_size=3000, overlap=200):
    if not text: 
        raise ValueError("Input text cannot be empty.")
    
    if window_size <= 0:
        raise ValueError("window_size must be greater than 0")
    
    if overlap < 0 or overlap >= window_size:
        raise ValueError("overlap must be >= 0 and < window_size")

    cleaned_text = _clean_text(text)
    step = window_size - overlap
    chunks = []
    for start in range(0, len(cleaned_text), step):
        chunk = cleaned_text[start:start + window_size]
        if chunk:
            chunks.append(chunk)
    return chunks


def insert_memory(user_id, thread_id, role, chunk):
    memory = MemorySchema(
        user_id=user_id,
        thread_id=thread_id,
        role=role,
        content=chunk,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    memory_collection.insert_one(memory.model_dump())


# Main function to generate a plan based on the provided context and focus areas
def generate_plan(context):
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-5",
        messages=[{"role": "user", "content": context}],
    )
    return response.content[0].text