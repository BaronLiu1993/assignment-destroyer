
import re

import anthropic
from pinecone import Pinecone
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize the Anthropic client
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Initialize the MongoDB client
mongo_client = MongoClient(uri=os.getenv("MONGODB_URI"))

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip()

# Inject all context into model
def build_plan_context(document_text, file_ids):
    content = []
    for file_id in file_ids:
        content.append({
            "file_id": file_id,
            "text": clean_text(document_text)
        })
    return content

# Main function to generate a plan based on the provided context and focus areas
def generate_plan(context):
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-5",
        messages=[{"role": "user", "content": context}],
    )
    return response.content[0].text