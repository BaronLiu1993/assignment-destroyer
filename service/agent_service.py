from pinecone import Pinecone
from pymongo import MongoClient
import re
from service.utils.constants import MONGODB_URI, PINECONE_API_KEY


# Initialise Pinecone client and point to index
client = MongoClient(uri=MONGODB_URI)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("quickstart")

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip()    

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def upsert_document_embeddings_into_pinecone(chunks, namespace):
    if chunks is None or namespace is None:
        raise ValueError("Chunks and namespace must be provided")
    
    index.upsert_records(
        f"{namespace}-requirements",
        chunks
    ) 