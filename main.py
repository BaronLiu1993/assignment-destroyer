from dotenv import load_dotenv
load_dotenv()

import anthropic
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic()

@app.get("/health")
def health():
    return {"status": "ok"}
