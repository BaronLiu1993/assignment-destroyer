import re
from datetime import datetime, timezone

import anthropic
from pymongo import MongoClient
from service.utils.constants import ANTHROPIC_API_KEY, MONGODB_URI
from plan_dto import MemorySchema, PlanOutputSchema
from prompts.plan import planning_system_prompt

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
   

def insert_memory(user_id, thread_id, role, chunks):
    res = []
    for chunk in chunks:
        memory = MemorySchema(
            user_id=user_id,
            thread_id=thread_id,
            role=role,
            content=_clean_text(chunk),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        res.append(memory.model_dump())
    memory_collection.insert_many(res)

# Create plan first, of what to do with the document and add the current plan to the memory
# Main function to generate a plan based on the provided context and focus areas
def generate_plan(context, user_prompt, user_id, thread_id):
    response = anthropic_client.messages.create(
        model="claude-sonnet-4-5",
        messages=[{"role": "user", "content": planning_system_prompt + context + user_prompt}],
        output_config=PlanOutputSchema
    )
    insert_memory(user_id, thread_id, "plan", [response.content[0].text])
    return response.content[0].text